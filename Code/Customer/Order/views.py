import random
import string
import stripe
import os

from datetime import datetime

from celery import shared_task

from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives , send_mail
from django.template.loader import render_to_string
from .utils import generate_order_pdf
from django.db.models import Count, Q
from django.utils.timezone import now

from .models import Order, OrderItem
from Customer.Cart.models import Cart, CartItem
from Customer.Account.models import Register
from Customer.Buy_Back.models import  Customedesign , Buyback
from Seller.ProductS.models import Product , Resell_Product
from DP.models import DPData
from DP.OrderD.models import DPOrder  
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
import random
import string

######################################################################################
######################################################################################

stripe.api_key = settings.STRIPE_SECRET_KEY

def order_form(request):
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "You must be logged in to place an order.")
        return redirect("login")

    user = get_object_or_404(Register, customer_id=user_id)
    cart = Cart.objects.filter(user=user).first()

    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart_detail")

    if request.method == "POST":
        existing_order = Order.objects.filter(user=user, order_status='Pending').first()

        if not existing_order:
            order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

            order = Order.objects.create(
                user=user,
                first_name=request.POST.get('fname', ''),
                last_name=request.POST.get('lname', ''),
                email=request.POST.get('email', ''),
                phone=request.POST.get('number', ''),
                address1=request.POST.get('address1', ''),
                address2=request.POST.get('address2', ''),
                zip_code=request.POST.get('pincode', ''),
                city=request.POST.get('city', 'Rajkot'),
                state=request.POST.get('state', 'Gujarat'),
                country=request.POST.get('country', 'India'),
                order_id=order_id,
                order_status='Pending',
                total_price=cart.total_price,
                total_security=cart.total_security,
                Grand_total=cart.Grand_total,
                discount=cart.discount,
            )

            for item in cart.items.all():
                delivery_date = item.delivery_date
                rental_date = item.rental_date
                return_date = item.return_date
                days = item.days
                security = item.security if item.security else 0
                prod_type = item.prod_type
                buyback_id = str(item.buyback_id)


                if prod_type == 'Buy_back' and buyback_id:
                    try:
                        buyback_instance = Buyback.objects.filter(buyback_id=buyback_id).first()

                        if not buyback_instance:
                            print(f"Buyback with ID {buyback_id} not found.")
                        else:
                            custom_design = Customedesign.objects.filter(buyback=buyback_instance).first()
                            if custom_design:
                                custom_design.return_date = return_date
                                custom_design.save()
                    except Buyback.DoesNotExist:
                        print(f"Buyback with ID {buyback_id} does not exist.")

                try:
                    OrderItem.objects.create(
                        order=order,
                        product_id=item.product_id if item.prod_type in ['own_product', 'sell_with_us'] else None,
                        rid=item.rid if item.prod_type == 'resell_product' else None,
                        name=item.name,
                        brand=item.brand,
                        price=item.price,
                        quantity=item.quantity,
                        image=item.image,
                        color=item.color,
                        size=item.size,
                        days=days,
                        rental_date=", ".join([date.strftime('%d %B %Y') for date in rental_date]) if isinstance(rental_date, list) else rental_date,
                        return_date=return_date,
                        delivery_date=delivery_date,
                        security=security,
                        prod_type=prod_type
                    )
                except Exception as e:
                    print(f"Error saving order item: {e}")

        else:
            order = existing_order

        if 'cash_on_delivery' in request.POST:
            return redirect('order_success', order_id=order.order_id)
        elif 'online_payment' in request.POST:
            return redirect("create_checkout_session")
        
        print(user.email)

    context = {
        "cart_items": cart.items.all(),
        "cart": cart,
        "user" : user,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, "orderc.html", context)

######################################################################################

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'POST':
        user_id = request.session.get("user_id")
        user = get_object_or_404(Register, customer_id=user_id)
        order = Order.objects.filter(user=user, order_status='Pending').first()

        if not order:
            return JsonResponse({'error': 'No pending order found'})

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'product_data': {'name': 'Fashion Rental Order'},
                    'unit_amount': int(float(request.POST['amount']) * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f'/order/payment_success/{order.order_id}/'),
            cancel_url=request.build_absolute_uri('/order/payment_cancel/'),
        )
        return JsonResponse({'sessionId': checkout_session.id})

######################################################################################

def send_order_email(order, order_items):
    """Send email with order confirmation (No PDF attachment)."""
    user_email = order.user.email

    subject = "Your Order has been Placed Successfully!"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user_email]

    # Render email template properly
    html_message = render_to_string('emails/order_confirmation.html', {
        'username': order.user.username,
        'order_id': order.order_id,
        'order_items': order_items,
        'total_price': order.Grand_total,
        'payment_method': order.payment_method,
    })

    email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
    email_message.attach_alternative(html_message, "text/html")

    email_message.send()

######################################################################################

def assign_order_to_dp(order):
    """
    Assign an order to a DP with less than 5 active orders today.
    If rejected, reassign to another available DP.
    """
    today = datetime.today().date()

    existing_assignment = DPOrder.objects.filter(order=order).first()

    if existing_assignment and existing_assignment.status == "Accepted":
        return existing_assignment.dp  

    available_dps = DPData.objects.annotate(
        order_count=Count('assigned_orders', filter=Q(assigned_orders__assigned_date=today, assigned_orders__status="Accepted"))
    ).filter(order_count__lt=5, is_active=True)

    if available_dps.exists():
        dp = random.choice(list(available_dps))  

        if existing_assignment:
            existing_assignment.dp = dp
            existing_assignment.status = "Pending"  
            existing_assignment.assigned_date = today
            existing_assignment.save()
        else:
            DPOrder.objects.create(dp=dp, order=order, status="Pending")

        return dp 

    return None  

######################################################################################

def payment_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order_items = OrderItem.objects.filter(order=order)


    if order.order_status == 'Pending':  
        order.order_status = 'Processing'
        order.payment_method = 'Online'
        order.payment_status = 'Completed'
        order.payment_date = datetime.now()
        order.save()

        for item in order_items:
            item.product_payment_status = 'Completed'
            item.save()


        cart = Cart.objects.filter(user=order.user).first()
        assigned_dp = assign_order_to_dp(order)
        if cart:
            cart.items.all().delete()
            cart.delete()

    messages.success(request, "Order placed successfully with online payment.")
    order_items = OrderItem.objects.filter(order=order)
    send_order_email(order, order_items)

    return render(request, 'payment_success.html', {
        'order': order,
        'order_items': order_items
    })

######################################################################################

def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order_items = OrderItem.objects.filter(order=order)

    if order.order_status == 'Pending':  
        order.order_status = 'Processing'
        order.payment_method = 'Cash_on_delivery'
        order.payment_status = 'Pending'
        order.payment_date = datetime.now()
        order.save()

        for item in order_items:
            item.product_payment_status = 'Pending'
            item.save()

        cart = Cart.objects.filter(user=order.user).first()

        request.session['discount'] = 0
        assigned_dp = assign_order_to_dp(order)

        if cart:
            cart.items.all().delete()
            cart.delete()

    messages.success(request, "Order placed successfully with Cash on Delivery.")
    order_items = OrderItem.objects.filter(order=order)
    send_order_email(order, order_items)

    return render(request, 'payment_success.html', {
        'order': order,
        'order_items': order_items
    })

######################################################################################

def payment_cancel(request):
    return render(request, 'payment_cancel.html')

######################################################################################

@shared_task
def send_return_notifications():
    today = now().date()
    items_due_for_return = OrderItem.objects.filter(return_date=today, return_status="Pending")

    for item in items_due_for_return:
        order = item.order
        dp_order = DPOrder.objects.filter(order=order).first()  

        send_mail(
            "Product Return Reminder",
            f"Dear {order.user.username},\nYour rented item '{item.name}' is due for return today.",
            "noreply@stylesurfer.com",
            [order.user.email],
        )

        if dp_order:
            send_mail(
                "Return Order Alert",
                f"Order {order.order_id} is due for return. Please coordinate for pickup.",
                "noreply@stylesurfer.com",
                [dp_order.dp.email],  
            )

    return f"Sent return notifications for {len(items_due_for_return)} items."

######################################################################################