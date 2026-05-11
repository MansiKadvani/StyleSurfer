import io
import datetime
from datetime import timedelta, date
from decimal import Decimal
from urllib.request import urlopen

from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.timezone import now, localdate
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.contrib.staticfiles import finders

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

from .forms import RegisterForm
from Customer.Account.forms import ProductForm
from .models import Register, OTPVerification, HelpRequest, Review_Rating
from ..Product.views import product

from Customer.SpinToWin.models import UserSpin, RedeemedVoucher
from Customer.Order.models import Order, OrderItem
from Customer.SellWithUs.models import CustomerSellerProduct, Customerproduct_SizeQuantity
from Seller.ProductS.models import Product, Resell_Product
from Customer.Buy_Back.models import Customedesign, Buyback, SellerRequest

#######################################################################################
#######################################################################################

def Registration(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        number = request.POST.get('number')
        password = request.POST.get('password')

        if Register.objects.filter(username=username).exists():
            return redirect('/Registration/?error=username is already exist.')
        elif Register.objects.filter(email=email).exists():
            return redirect('/Registration/?error=email is already exist.')
        elif Register.objects.filter(number=number).exists():
            return redirect('/Registration/?error=number is already exist.')

        otp_instance = OTPVerification(email=email)
        otp_instance.generate_otp()

        html_message = render_to_string('emails/otp_verification_email.HTML', {
            'otp': otp_instance.otp,
            'username': username,
            'email': email,
        })

        subject = 'Your OTP Verification Code'
        from_email = 'stylesurfer3@gmail.com'
        to_email = [email]

        email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
        email_message.attach_alternative(html_message, "text/html")
        email_message.send()

        request.session['temp_user_data'] = {
            'username': username,
            'email': email,
            'number': number,
            'password': password,
        }

        return redirect('otpVerify')

    return render(request, 'Registration.html')

######################################################################################

def otpVerify(request):
    if request.method == "POST":
        otp1 = request.POST.get('otp1')
        otp2 = request.POST.get('otp2')
        otp3 = request.POST.get('otp3')
        otp4 = request.POST.get('otp4')
        otp5 = request.POST.get('otp5')
        otp6 = request.POST.get('otp6')

        otp = otp1 + otp2 + otp3 + otp4 + otp5 + otp6

        email = request.session.get('temp_user_data', {}).get('email')

        try:
            otp_instance = OTPVerification.objects.get(email=email, otp=otp)
            if otp_instance.is_expired():
                return render(request, 'otpVerify.html', {'error': 'OTP has expired. Please request a new OTP.'})
        except OTPVerification.DoesNotExist:
            return render(request, 'otpVerify.html', {'error': 'Invalid OTP. Please try again.'})

        user_data = request.session.get('temp_user_data')

        if user_data:
            register = Register.objects.create(
                username=user_data['username'],
                email=user_data['email'],
                number=user_data['number'],
                password=user_data['password'],
            )
            register.save()

            html_message = render_to_string('emails/register_user_email.HTML', {
                'username': user_data['username'],
                'email': user_data['email'],
            })

            subject = 'Your Account Has Been Registered'
            from_email = 'stylesurfer3@gmail.com'
            to_email = [user_data['email']]

            email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
            email_message.attach_alternative(html_message, "text/html")
            email_message.send()

            del request.session['temp_user_data']

            return redirect('/Account/login/?success=Otp is verified!Now you can login.')

    return render(request, 'otpVerify.html')

######################################################################################

def otpResend(request):
    user_data = request.session.get('temp_user_data')

    if not user_data:
        return redirect('Registration')

    email = user_data['email']
    username = user_data['username']

    otp_instance = OTPVerification(email=email)
    otp_instance.generate_otp()

    html_message = render_to_string('emails/otp_verification_email.html', {
        'otp': otp_instance.otp,
        'username': username,
        'email': email,
    })

    subject = 'Your OTP Verification Code'
    from_email = 'stylesurfer3@gmail.com'
    to_email = [email]

    email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
    email_message.attach_alternative(html_message, "text/html")
    email_message.send()

    return redirect('otpVerify')

######################################################################################

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = Register.objects.filter(username=username).first()

        if user is None:
            return redirect('/login/?error=Username does not exist.')

        if not user.check_password(password):
            return redirect('/login/?error=Password is incorrect.')

        request.session['user_id'] = user.customer_id
        request.session['username'] = user.username
        request.session.set_expiry(0)

        return HttpResponse('Home Page')  

    return render(request, 'login.html')

######################################################################################

tokens = {}

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        users = Register.objects.filter(email=email)
        user = users.first()
        username = user.username

        if not users.exists():
            return redirect('/forgot_password/?error=Username does not exist.')

        token = get_random_string(length=32)
        tokens[email] = {'token': token, 'expires_at': now() + datetime.timedelta(minutes=30)}

        reset_link = request.build_absolute_uri(reverse('reset_password', args=[token]))

        try:

            html_message = render_to_string('emails/forgot_psw_email.html', {
                'forgot': reset_link,
                'username': username,
                'email': email,
            })

            subject = 'Reset Password'
            from_email = 'stylesurfer3@gmail.com'
            to_email = [email]

            email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
            email_message.attach_alternative(html_message, "text/html")
            email_message.send()
            return redirect('/forgot_password/?success=Password reset link has been sent to your email.')
        except Exception as e:
            return redirect('/forgot_password/?error=error in sending email.')

        return redirect('login')

    return render(request, 'forgot_password.html')


######################################################################################

def reset_password(request, token):
    email = None
    for key, value in tokens.items():
        if value['token'] == token and value['expires_at'] > now():
            email = key
            break

    if not email:
        return redirect('/Account/login/?error=Invalid or expired token.')

    if request.method == 'POST':
        password = request.POST.get('password')

        user = Register.objects.filter(email=email).first()
        if user:
            user.password = password
            user.save()
            del tokens[email]  
            return redirect('/Account/login/?success=Password Reset Successfully.')

    return render(request, 'reset_password.html', {'token': token})

######################################################################################

def logout(request):
    request.session.flush()
    return redirect('home')

######################################################################################

def account_home(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = Register.objects.get(customer_id=user_id)

    coin = UserSpin.objects.filter(user=user).first()  

    return render(request, 'account_home.html', {'user': user, 'coin': coin})


######################################################################################

def profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    else:
        user = Register.objects.get(customer_id=user_id)
        user_psw = user.password
        if request.method == 'POST':
            form = RegisterForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                form.save()
                return redirect(f'/Account/profile/?success=Profile Updated.')
            else:
                return redirect(f'/Account/profile/?error=Error in updating profile.')
        else:
            form = RegisterForm(instance=user)
    return render(request, 'profile.html', {'form': form, 'user': user, 'psw': user_psw})

######################################################################################

def password(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    else:
        user = Register.objects.get(customer_id=user_id)
        user_psw = user.password
        if request.method == 'POST':
            new_psw = request.POST.get('npsw')
            user.password = new_psw
            user.save()
    return render(request, 'password.html', {'oldPSW': user_psw})

######################################################################################

def help(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    if request.method == "POST":
        username = request.POST.get("uname")
        useremail = request.POST.get("uemail")
        usernumber = request.POST.get("unumber")
        userissue = request.POST.get("uissue")

        try:
            registered_user = Register.objects.get(email=useremail, username=username, number=usernumber)

            help_request = HelpRequest(
                user=registered_user,
                issue=userissue
            )
            help_request.save()
            return redirect('/help/?success=Your issue has been submitted successfully. Our team will contact you soon.')

        except Register.DoesNotExist:
            return redirect('/help/?error=User does not exist in the system!.')

    return render(request, 'help.html')

######################################################################################

def cvoucher(request):
    user_id = request.session.get('user_id')
    user = Register.objects.get(customer_id=user_id)
    vouchers = RedeemedVoucher.objects.filter(user=user).order_by('-is_active', '-voucher__expires_at')

    return render(request, 'voucher.html', {'vouchers': vouchers})

######################################################################################

def order(request):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    orders = Order.objects.filter(
        user__customer_id=user_id,
        payment_method__isnull=False,  
        order_status__isnull=False  
    ).order_by('-created_at').prefetch_related("items")

    context = {
        "orders": orders,

    }

    return render(request, "order.html", context)

#---------------------------------------------------------------------------------

def order_details(request, order_id):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")
    
    user = Register.objects.get(customer_id=user_id)
    order = get_object_or_404(Order, order_id=order_id, user__customer_id=user_id)

    order_items = order.items.all()

    existing_reviews = {item.id: None for item in order_items}

    for item in order_items:
        review = Review_Rating.objects.filter(user=user, prod_id=item.id).first()
        if review:
            existing_reviews[item.id] = review

    prod_items = OrderItem.objects.filter(order=order)

    context = {
        "order": order,
        "order_items": order_items,
        "existing_reviews": existing_reviews,
        "prod_items" : prod_items ,  
    }

    return render(request, "order_details.html", context)

#---------------------------------------------------------------------------------

@csrf_exempt
def submit_review(request) :
    if request.method == "POST":
        prod_id = request.POST.get('product_id')
        review_text = request.POST.get("review")
        rating = request.POST.get("rating")
        product_type = request.POST.get("product_type") 

        user_id = request.session.get('user_id')
        user = Register.objects.get(customer_id=user_id)

        order_item = OrderItem.objects.get(id=prod_id)

        if product_type == "own_product":
            product_record = Product.objects.filter(id=order_item.product_id).first()
        elif product_type == "sell_with_us":
            product_record = CustomerSellerProduct.objects.filter(id=order_item.product_id).first()
        else:
            product_record = Resell_Product.objects.filter(rid=order_item.rid).first()
        
        order_id = order_item.order.order_id

        if product_record :
            
            review_rating = Review_Rating.objects.create(
                user = user,
                order_id = order_id,
                prod_id = prod_id,
                product=product_record if isinstance(product_record, Product) else None,
                sell_with_us=product_record if isinstance(product_record,CustomerSellerProduct) else None,
                resell_product=product_record if isinstance(product_record, Resell_Product) else None,
                rating=rating,
                review=review_text
            )
            review_rating.save()
            return JsonResponse({'success': 'Review submitted successfully.'})
    return HttpResponse("HEllo")

#---------------------------------------------------------------------------------

def get_review(request):
    product_id = request.GET.get("product_id")

    if not product_id:
        return JsonResponse({"success": False, "message": "Missing product ID"})

    review = Review_Rating.objects.filter(prod_id=product_id).first()

    if review:
        return JsonResponse({
            "success": True,
            "review": review.review,
            "rating": review.rating
        })
    else:
        return JsonResponse({"success": False, "message": "Review not found"})

#---------------------------------------------------------------------------------

@csrf_exempt
def update_review(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        review_text = request.POST.get("review")
        rating = request.POST.get("rating")
        if not product_id or not review_text or not rating:
            return JsonResponse({"success": False, "message": "Missing required fields!"})

        try:
            rating = int(rating)
        except ValueError:
            return JsonResponse({"success": False, "message": "Invalid rating format!"})

        if rating < 1 or rating > 5:
            return JsonResponse({"success": False, "message": "Rating must be between 1 and 5!"})

        review = Review_Rating.objects.filter(prod_id=product_id).first()

        if review:
            review.review = review_text
            review.rating = rating
            review.save()
            return JsonResponse({"success": True, "message": "Review updated successfully!"})
        else:
            return JsonResponse({"success": False, "message": "Review not found!"})

    return JsonResponse({"success": False, "message": "Invalid request method!"})

#---------------------------------------------------------------------------------

def cancel_order(request, order_id):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    order = get_object_or_404(Order, order_id=order_id, user__customer_id=user_id)

    if order.order_status not in ['Delivered', 'Completed', 'Cancelled']:
        order_items = order.items.all() 
        for item in order_items:
            if item.date:  
                product = get_object_or_404(Product, name=item.name)
                product.quantity += item.quantity
                product.save()
            else:  
                rproduct = get_object_or_404(Resell_Product, rname=item.name)
                rproduct.rquantity += item.quantity
                rproduct.save()

        order.delete()
        # messages.success(request, "Order cancelled successfully.")
        return redirect("order/?success=Order cancelled successfully.")
    else:
        messages.error(request, "Order cannot be cancelled.")

    return redirect("order")

#---------------------------------------------------------------------------------

def generate_order_pdf(request, order_id):
    user_id = request.session.get("user_id")

    if not user_id:
        return redirect("login")

    order = get_object_or_404(Order, order_id=order_id, user__customer_id=user_id)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(f"Order Receipt - {order.order_id}")

    font_path = finders.find("fonts/DejaVuSans.ttf")
    if font_path:
        pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
        font_name = "DejaVuSans"
    else:
        font_name = "Helvetica"

    main_color = colors.HexColor("#6D4C41") 
    text_color = colors.HexColor("#4b3621")
    bg_color = colors.HexColor("#f5f5f5")

    logo_path = finders.find("images/logo.png")
    if logo_path:
        pdf.drawImage(logo_path, 50, 730, width=120, height=50, mask="auto")

    pdf.setFont("Helvetica-Bold", 20)
    pdf.setFillColor(main_color)
    pdf.drawString(180, 750, "StyleSurfer Order Receipt")

    pdf.setFont("Helvetica-Bold", 40)
    pdf.setFillColor(colors.HexColor("#D7CCC8"))
    pdf.rotate(45)
    pdf.drawString(150, 500, "StyleSurfer")
    pdf.rotate(-45)

    pdf.setFont(font_name, 12)
    pdf.setFillColor(text_color)
    pdf.drawString(50, 700, f"Order ID: {order.order_id}")
    pdf.drawString(50, 680, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.drawString(50, 660, f"Payment Method: {order.payment_method if order.payment_method else 'N/A'}")
    pdf.drawString(50, 640, f"Order Status: {order.order_status}")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, 610, "Shipping Address:")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 590, f"{order.first_name} {order.last_name}")
    pdf.drawString(50, 570, order.address1)
    if order.address2:
        pdf.drawString(50, 550, order.address2)
    pdf.drawString(50, 530, f"{order.city}, {order.state}, {order.country} - {order.zip_code}")
    pdf.drawString(50, 510, f"Phone: {order.phone} | Email: {order.email}")

    table_data = [["Image", "Product", "Color", "Size", "Days", "Price", "Qty", "Total"]]

    default_img_path = finders.find("images/no_image.png")

    for item in order.items.all():
        img_reader = None
        if item.image:
            try:
                img_reader = ImageReader(urlopen(item.image))
            except:
                img_reader = ImageReader(default_img_path) if default_img_path else None
        else:
            img_reader = ImageReader(default_img_path) if default_img_path else None

        row = [
            img_reader if img_reader else "No Image",
            item.name,
            item.color if item.color else "-",
            item.size if item.size else "-",
            str(item.days),
            f"₹ {item.price}",
            str(item.quantity),
            f"₹ {item.price * item.quantity}",
        ]
        table_data.append(row)

    table = Table(table_data, colWidths=[60, 120, 50, 50, 40, 60, 40, 70])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), main_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), bg_color),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]))

    table.wrapOn(pdf, 50, 380)
    table.drawOn(pdf, 50, 320)

    pdf.setFont(font_name, 12)
    pdf.drawString(50, 200, f"Subtotal: ₹ {order.total_price}")
    pdf.drawString(50, 180, f"Security Deposit: ₹ {order.total_security}")
    pdf.drawString(50, 160, f"Shipping Cost: ₹ {order.shipping_cost}")
    pdf.drawString(50, 140, f"Discount: ₹ {order.discount}")
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, 120, f"Grand Total: ₹ {order.Grand_total}")

    pdf.setFillColor(text_color)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 80, "Thank you for shopping with StyleSurfer!")
    pdf.drawString(50, 60, "For support, contact us at support@stylesurfer.com")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")

#---------------------------------------------------------------------------------

######################################################################################

def Buy_back(request):
    user_id = request.session.get('user_id')  

    if not user_id:
        return redirect('login')  

    user = get_object_or_404(Register, customer_id=user_id)  \
    
    buyback_items = Customedesign.objects.filter(
        buyback__user=user,
        buyback__buyback_status__in=["Buy", "Back", "Pending" , "purchased make own product"]
    )

    for item in buyback_items:
        item.seller_status = SellerRequest.objects.filter(custom_design=item).values_list('status', flat=True).first() or "Pending"

    return render(request, 'Buy_back.html', {
        'buyback_items': buyback_items,
    })

#---------------------------------------------------------------------------------

def cancel_buyback_request(request, buyback_id):
    user_id = request.session.get('user_id')  

    if not user_id:
        return redirect('login')  

    user = get_object_or_404(Register, customer_id=user_id)  
    buyback = get_object_or_404(Buyback, id=buyback_id)

    if buyback.user != user:
        return redirect('Buy_back')

    custom_design = Customedesign.objects.filter(buyback=buyback).first()
    seller_request = SellerRequest.objects.filter(buyback=buyback).first()

    if custom_design and seller_request:
        customer_status = custom_design.Customer_status
        seller_status = seller_request.status
        buyback_status = buyback.buyback_status

        if buyback_status == "Buy" and customer_status == "Buy Request" and seller_status == "Pending":
            buyback.delete()
            return redirect('/Buy_back/?success=Your buyback request has been canceled successfully.')

        elif buyback_status == "Buy" and customer_status == "Purchase Request" and seller_status == "Pending":
            custom_design.Customer_status = "Back Request"
            custom_design.save() 
            return redirect('/Buy_back/?success=Your buyback request status has been updated.')


        elif buyback_status == "Buy" and customer_status == "Buy Request" and seller_status == "Approve":
            buyback.buyback_status = "Attempted Cancel - Approved" 
            buyback.save()  
            return redirect('/Buy_back/?success=Your buyback request has already been approved and cannot be canceled.')
 
    return redirect('/Buy_back/?success=Unable to process your request.')

#---------------------------------------------------------------------------------

def buyback_detail(request, buyback_id):
    try:
        buyback_id = str(buyback_id)
    except ValueError:
        return render(request, 'error_page.html', {'error': 'Invalid Buyback ID'})

    buyback = get_object_or_404(Buyback, buyback_id=buyback_id)
    custom_designs = Customedesign.objects.filter(buyback=buyback)
    seller_requests = SellerRequest.objects.filter(buyback=buyback)
    current_date = localdate()

    for item in custom_designs:
        if item.return_date:
            five_day_range = sorted([
                item.return_date - timedelta(days=day)
                for day in range(5, 0, -1)
            ])
            item.five_days_before_return_list = five_day_range
        else:
            item.five_days_before_return_list = []

    context = {
        'buyback': buyback,
        'custom_designs': custom_designs,
        'buyback_id': buyback_id,
        'seller_requests': seller_requests,
        'current_date': current_date,
    }

    return render(request, 'buyback_detail.html', context)
#---------------------------------------------------------------------------------

def request_purchase(request, buyback_id):
    buyback = get_object_or_404(Buyback, buyback_id=buyback_id)
    custom_designs = Customedesign.objects.filter(buyback=buyback)


    today = date.today()
    updated_designs = []

    for design in custom_designs:
        if design.return_date:
            five_days_before = design.return_date - timedelta(days=5)
            if five_days_before <= today:
                design.Customer_status = "Purchase Request"  
                design.save()

                seller_request = SellerRequest.objects.filter(custom_design=design).first()
                if seller_request:
                    seller_request.status = "Pending"
                    seller_request.save()

                buyback.buyback_status = "purchased make own product"
                buyback.save()

                updated_designs.append(design)



    if updated_designs:
        messages.success(request, "Your purchase request has been updated.")
    else:
        messages.error(request, "Invalid request. No items are eligible for buyback.")

    return redirect(f'/Account/buyback_detail/{buyback_id}/?success=Successfully!')
######################################################################################

def Sell(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login')

    register = Register.objects.get(customer_id=user_id)

    products = CustomerSellerProduct.objects.filter(email=register.email)

    page = request.GET.get('page', 1)  
    items_per_page = 10  

    paginator = Paginator(products, items_per_page)

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1) 
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)  

    success_message = request.GET.get('success', '')

    return render(request, 'Sell.html', {'products': products_page})

#---------------------------------------------------------------------------------

def updateSellWithUs(request, product_id):
    product = get_object_or_404(CustomerSellerProduct, id=product_id)

    available_sizes = ["XS", "S", "M", "L", "XL", "XXL"]

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            Customerproduct_SizeQuantity.objects.filter(product=product).delete()

            sizes = request.POST.getlist("sizes[]")
            quantities = request.POST.getlist("quantities[]")

            for size, quantity in zip(sizes, quantities):
                if size and quantity.isdigit():
                    Customerproduct_SizeQuantity.objects.create(product=product, size=size, quantity=int(quantity))

            messages.success(request, 'Product updated successfully!')
            return redirect('Sell')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)

    size_quantity_data = product.CustomerSellerProduct_size_quantities.all()

    return render(request, 'sell_update.html', {'form': form, 'product': product ,  'size_quantity_data': size_quantity_data, 'available_sizes': available_sizes})

#---------------------------------------------------------------------------------

def deleteSellWithUs(request, product_id):
    product = get_object_or_404(CustomerSellerProduct, id=product_id)
    product.delete()
    return redirect(f'/Account/Sell/?success=Product deleted.')

def Sell_view(request, product_id):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
    

    register = Register.objects.get(customer_id=user_id)

    product = CustomerSellerProduct.objects.filter(id=product_id).first()

    order_items = OrderItem.objects.filter(name=product.name)
    
    page = request.GET.get('page', 1)  
    items_per_page = 10 

    paginator = Paginator(order_items, items_per_page)

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)  
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)  

    return render(request, 'Sell_view.html', {'product': product, 'page_obj': products_page})

#---------------------------------------------------------------------------------

def search_products(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login')

    register = Register.objects.get(customer_id=user_id)

    products = CustomerSellerProduct.objects.filter(email=register.email)

    query = request.GET.get('q')  
    

    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(category__icontains=query) 

        )

    page = request.GET.get('page', 1)  
    items_per_page = 10  

    paginator = Paginator(products, items_per_page)

    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1) 
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)

    return render(request, 'Sell.html', {'products': products_page, 'query': query})

######################################################################################