from django.shortcuts import render, get_object_or_404, redirect
from Customer.Order.models import Order, OrderItem
from Customer.Account.models import Register
from DP.models import DPData
from .models import DPOrder
from django.utils.timezone import now

from django.utils.timezone import now
today = now().date() 


from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
import json
from Customer.Buy_Back.models import Customedesign , SellerRequest

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
import json

import datetime
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from Customer.Order.models import Order, OrderItem

from django.shortcuts import render, get_object_or_404
from Customer.Order.models import Order, OrderItem
from .models import DPOrder  # Assuming DPOrder is the model that links to the delivery partner
from django.shortcuts import render, get_object_or_404
from Customer.Order.models import Order, OrderItem
from Customer.Account.models import OTPVerification

import random
from django.db.models import Count, Q
from DP.models import DPData
from DP.OrderD.models import DPOrder

from django.shortcuts import render, get_object_or_404, redirect
from Customer.Order.models import Order, OrderItem

######################################################################################
######################################################################################

def OrderD(request):
    dp_id = request.session.get('DP_id')
    if not dp_id:
        return redirect('DP_login')

    dp_user = DPData.objects.filter(DP_id=dp_id).first()
    if not dp_user:
        return redirect('DP_login')

    assigned_orders = DPOrder.objects.filter(dp=dp_user).select_related("order")
    return_orders = OrderItem.objects.filter(return_date=today)

    if not assigned_orders.exists():
        print(f"No orders assigned to DP {dp_user.DP_id}")  

    return render(request, 'DOrder_view.html', {'orders':[dp_order.order for dp_order in assigned_orders] , 'dp_user': dp_user , "return_orders": return_orders })



######################################################################################

def Dorderdetails(request, order_id):
    dp_id = request.session.get('DP_id')
    if not dp_id:
        return redirect('DP_login')

    dp_user = get_object_or_404(DPData, DP_id=dp_id)

    dp_order = DPOrder.objects.filter(order__order_id=order_id, dp=dp_user).first()

    if not dp_order:
        return render(request, 'DOrder_details.html', {
            'error_message': "This order is not assigned to you.",
            'dp_user': dp_user
        })

    order = dp_order.order  
    order_items = OrderItem.objects.filter(order=order)

    return render(request, 'DOrder_details.html', {
        'order': order,
        'order_items': order_items,
        'dp_user': dp_user
    })

######################################################################################

def assign_order_to_dp(order):
   
    today = now().date()

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

def reject_order(request, order_id):
   
    order = get_object_or_404(Order, order_id=order_id)
    dp_order = get_object_or_404(DPOrder, order=order)

    if dp_order.status != "Accepted":  
        dp_order.status = "Rejected"
        dp_order.save()

        assign_order_to_dp(order)

    return redirect("OrderD")  

######################################################################################

def accept_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order.is_accepted = True  
    order.save()
    return redirect('Dorderdetails', order_id=order_id)

######################################################################################


def Dorder_complete(request, order_id, item_id):
    dp_id = request.session.get('DP_id')

    if not dp_id:
        return redirect('DP_login')

    dp_user = DPData.objects.filter(DP_id=dp_id).first()

    if not dp_user:
        return redirect('DP_login')

    dp_order = get_object_or_404(DPOrder, order__order_id=order_id, dp=dp_user)
    order = dp_order.order
    order_item = get_object_or_404(OrderItem, order=order, id=item_id)


    show_return = order_item.return_date is not None

    current_time = now()

    return render(request, "Order_Complete.html", {
        "order": order,
        "order_item": order_item,
        "show_return": show_return,
        "current_time": current_time
    })

######################################################################################

def Dsend_email(request , order_id):
    dp_id = request.session.get('DP_id')

    if not dp_id:
        return redirect('DP_login')

    dp_user = DPData.objects.filter(DP_id=dp_id).first()

    if not dp_user:
        return redirect('DP_login')

    dp_order = get_object_or_404(DPOrder, order__order_id=order_id, dp=dp_user)

    order = dp_order.order

    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        email = item.order.email
        first_name = item.order.first_name
        last_name = item.order.last_name


    otp_instance = OTPVerification(email=email)
    otp_instance.generate_otp()


    html_message = render_to_string('emails/Dotp_verification_email.HTML', {
        'otp': otp_instance.otp,
        'username': first_name + " " + last_name,
        'email': email,
    })

    subject = 'Your OTP Verification Code'
    from_email = 'stylesurfer3@gmail.com'
    to_email = [email]

    email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
    email_message.attach_alternative(html_message, "text/html")
    email_message.send()

    request.session['temp_user_data'] = {
        'email': email,
    }

    return redirect(f'/DP/Dorder/Dorder_complete/{order_id}/{order_items.first().id}/?order_id={order_id}')

#######################################################################################


def verify_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        entered_otp = data.get("otp")
        order_id = data.get("order_id")
        item_id = data.get("item_id")

        email = request.session.get('temp_user_data', {}).get('email')

        if not email:
            return JsonResponse({"error": "Session expired. Please restart verification."}, status=400)

        try:
            otp_instance = OTPVerification.objects.get(email=email, otp=entered_otp)

            if otp_instance.is_expired():
                return JsonResponse({"error": "OTP has expired. Please request a new one."}, status=400)

        except OTPVerification.DoesNotExist:
            return JsonResponse({"error": "Invalid OTP. Please try again."}, status=400)

        if order_id and item_id:
            order = get_object_or_404(Order, order_id=order_id)
            order_item = get_object_or_404(OrderItem, order=order, id=item_id)

            
            if order_item.return_date is not None:  
                order_item.product_order_status = "delivered"
            else:  
                order_item.product_order_status = "Completed"

            order_item.save()

            all_rental_returned = all(
                item.product_order_status == "delivered" for item in OrderItem.objects.filter(order=order) if
                item.return_date is not None
            )
            all_reselling_completed = all(
                item.product_order_status == "Completed" for item in OrderItem.objects.filter(order=order) if
                item.return_date is None
            )

            if all_rental_returned and all_reselling_completed:
                order.order_status = "Completed"
            else:
                order.order_status = "Processing"

            order.save()

        return JsonResponse({"valid": True, "message": "OTP verified & order marked as returned."})

    return JsonResponse({"error": "Invalid request"}, status=400)

######################################################################################


def DRsend_email(request , order_id):
    dp_id = request.session.get('DP_id')

    if not dp_id:
        return redirect('DP_login')

    dp_user = DPData.objects.filter(DP_id=dp_id).first()

    if not dp_user:
        return redirect('DP_login')

    dp_order = get_object_or_404(DPOrder, order__order_id=order_id, dp=dp_user)

    order = dp_order.order

    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        email = item.order.email
        first_name = item.order.first_name
        last_name = item.order.last_name


    otp_instance = OTPVerification(email=email)
    otp_instance.generate_otp()


    html_message = render_to_string('emails/Dotp_verification_email.HTML', {
        'otp': otp_instance.otp,
        'username': first_name + " " + last_name,
        'email': email,
    })

    subject = 'Your OTP Verification Code'
    from_email = 'stylesurfer3@gmail.com'
    to_email = [email]

    email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
    email_message.attach_alternative(html_message, "text/html")
    email_message.send()

    request.session['temp_user_data'] = {
        'email': email,
    }

    return redirect(f'/DP/Dorder/Dorder_complete/{order_id}/{order_items.first().id}/?order_id={order_id}')


######################################################################################

def Rverify_otp(request):
    if request.method == "POST":
        data = json.loads(request.body)
        entered_otp = data.get("otp")
        order_id = data.get("order_id")
        item_id = data.get("item_id")

       

        email = request.session.get('temp_user_data', {}).get('email')

        if not email:
            return JsonResponse({"error": "Session expired. Please restart verification."}, status=400)

        try:
            otp_instance = OTPVerification.objects.get(email=email, otp=entered_otp)

            if otp_instance.is_expired():
                return JsonResponse({"error": "OTP has expired. Please request a new one."}, status=400)

        except OTPVerification.DoesNotExist:
            return JsonResponse({"error": "Invalid OTP. Please try again."}, status=400)

        if order_id and item_id:
            order = get_object_or_404(Order, order_id=order_id)
            order_item = get_object_or_404(OrderItem, order=order, id=item_id)

            if order_item.return_date is not None:  # Rental product
                order_item.product_order_status = "Returned"
            else: 
                order_item.product_order_status = "Completed"

            order_item.save()

            all_rental_returned = all(
                item.product_order_status == "Returned" for item in OrderItem.objects.filter(order=order) if
                item.return_date is not None
            )
            all_reselling_completed = all(
                item.product_order_status == "Completed" for item in OrderItem.objects.filter(order=order) if
                item.return_date is None
            )

            if all_rental_returned and all_reselling_completed:
                order.order_status = "Completed"
            else:
                order.order_status = "Processing"

            order.save()

            if item_id:
                try:
                    design = Customedesign.objects.get(id=item_id, Customer_status="Back Request")
                    request_obj = SellerRequest.objects.get(custom_design=design, status="Pending")

                    design.Customer_status = "Back Request"
                    request_obj.status = "Approve"
                    design.save()
                    request_obj.save()

                    return JsonResponse({"valid": True, "message": "OTP verified. Custom design marked as returned."})

                except Customedesign.DoesNotExist:
                    pass  
                except SellerRequest.DoesNotExist:
                    pass 


            return JsonResponse({"valid": True, "message": "OTP verified & order marked as returned."})

        return JsonResponse({"valid": True, "message": "OTP verified but no order ID provided."})

    return JsonResponse({"error": "Invalid request"}, status=400)

######################################################################################

def Dsecuritysend_email(request , order_id):
    dp_id = request.session.get('DP_id')
    if not dp_id:
        return redirect('DP_login')

    dp_user = DPData.objects.filter(DP_id=dp_id).first()

    if not dp_user:
        return redirect('DP_login')

    dp_order = get_object_or_404(DPOrder, order__order_id=order_id, dp=dp_user)

    order = dp_order.order

    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        email = item.order.email
        first_name = item.order.first_name
        last_name = item.order.last_name


    otp_instance = OTPVerification(email=email)
    otp_instance.generate_otp()

    html_message = render_to_string('emails/Dsecurityotp_verification_email.HTML', {
        'otp': otp_instance.otp,
        'username': first_name + " " + last_name,
        'email': email,
    })

    subject = 'Your OTP Verification Code'
    from_email = 'stylesurfer3@gmail.com'
    to_email = [email]

    email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
    email_message.attach_alternative(html_message, "text/html")
    email_message.send()

    request.session['temp_user_data'] = {
        'email': email,
    }

    return redirect(f'/DP/Dorder/Dorder_complete/{order_id}/{order_items.first().id}/?order_id={order_id}')

######################################################################################

def Dcashsend_email(request , order_id):
    dp_id = request.session.get('DP_id')

    if not dp_id:
        return redirect('DP_login')

    dp_user = DPData.objects.filter(DP_id=dp_id).first()

    if not dp_user:
        return redirect('DP_login')

    dp_order = get_object_or_404(DPOrder, order__order_id=order_id, dp=dp_user)

    order = dp_order.order

    order_items = OrderItem.objects.filter(order=order)
    for item in order_items:
        email = item.order.email
        first_name = item.order.first_name
        last_name = item.order.last_name


    otp_instance = OTPVerification(email=email)
    otp_instance.generate_otp()

    
    html_message = render_to_string('emails/Dcashotp_verification_email.HTML', {
        'otp': otp_instance.otp,
        'username': first_name + " " + last_name,
        'email': email,
    })

    subject = 'Your OTP Verification Code'
    from_email = 'stylesurfer3@gmail.com'
    to_email = [email]

    email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
    email_message.attach_alternative(html_message, "text/html")
    email_message.send()

    request.session['temp_user_data'] = {
        'email': email,
    }

    return redirect(f'/DP/Dorder/Dorder_complete/{order_id}/{order_items.first().id}/?order_id={order_id}')

######################################################################################

def Rcashverify_otp(request):
        if request.method == "POST":
            data = json.loads(request.body)
            entered_otp = data.get("otp")
            order_id = data.get("order_id")
            item_id = data.get("item_id")

            email = request.session.get('temp_user_data', {}).get('email')

            if not email:
                return JsonResponse({"error": "Session expired. Please restart verification."}, status=400)

            try:
                otp_instance = OTPVerification.objects.get(email=email, otp=entered_otp)

                if otp_instance.is_expired():
                    return JsonResponse({"error": "OTP has expired. Please request a new one."}, status=400)

            except OTPVerification.DoesNotExist:
                return JsonResponse({"error": "Invalid OTP. Please try again."}, status=400)

            if order_id and item_id:
                order = get_object_or_404(Order, order_id=order_id)
                order_item = get_object_or_404(OrderItem, order=order, id=item_id)

                if order_item.return_date is not None: 
                    order_item.product_payment_status = "Completed"
                else: 
                    order_item.product_payment_status = "Completed"

                order_item.save()

                all_rental_returned = all(
                    item.product_payment_status == "Completed" for item in OrderItem.objects.filter(order=order) if
                    item.return_date is not None
                )
                all_reselling_completed = all(
                    item.product_payment_status == "Completed" for item in OrderItem.objects.filter(order=order) if
                    item.return_date is None
                )

                if all_rental_returned and all_reselling_completed:
                    order.payment_status = "Completed"
                else:
                    order.payment_status = "Pending"

                order.save()
               
                return JsonResponse({"valid": True, "message": "OTP verified & order marked as returned."})

            return JsonResponse({"valid": True, "message": "OTP verified but no order ID provided."})

        return JsonResponse({"error": "Invalid request"}, status=400)

######################################################################################

def Rsecurityverify_otp(request):
        if request.method == "POST":
            data = json.loads(request.body)
            entered_otp = data.get("otp")
            order_id = data.get("order_id")
            item_id = data.get("item_id")

            email = request.session.get('temp_user_data', {}).get('email')

            if not email:
                return JsonResponse({"error": "Session expired. Please restart verification."}, status=400)

            try:
                otp_instance = OTPVerification.objects.get(email=email, otp=entered_otp)

                if otp_instance.is_expired():
                    return JsonResponse({"error": "OTP has expired. Please request a new one."}, status=400)

            except OTPVerification.DoesNotExist:
                return JsonResponse({"error": "Invalid OTP. Please try again."}, status=400)

            if order_id and item_id:
                order = get_object_or_404(Order, order_id=order_id)
                order_item = get_object_or_404(OrderItem, order=order, id=item_id)

                if order_item.return_date is not None:  # Rental product
                    order_item.product_security_status = "Completed"
                    order_item.security = 0.00
                else:  
                    order_item.product_security_status = "Completed"
                    order_item.security = 0.00

                order_item.save()

                all_rental_returned = all(
                    item.product_security_status == "Completed" and order_item.security == 0.00 for item in OrderItem.objects.filter(order=order) if
                    item.return_date is not None
                )
                all_reselling_completed = all(
                    item.product_security_status == "Completed" and order_item.security == 0.00 for item in OrderItem.objects.filter(order=order) if
                    item.return_date is None
                )

                if all_rental_returned and all_reselling_completed:
                    order.security_status = "Completed"
                    order.total_security = 0.00

                else:
                    order.security_status = "Pending"

                order.save()

                return JsonResponse({"valid": True, "message": "OTP verified & order marked as returned."})

            return JsonResponse({"valid": True, "message": "OTP verified but no order ID provided."})

        return JsonResponse({"error": "Invalid request"}, status=400)

######################################################################################

def test12(request):
    return render(request, 'test.html')

######################################################################################
######################################################################################
