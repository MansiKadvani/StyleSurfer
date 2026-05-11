
from Seller.models import SellerData
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.timezone import now
from Customer.Buy_Back.models import SellerRequest, Customedesign, Buyback
from django.utils.html import strip_tags
from decimal import Decimal

#######################################################################################################################
#######################################################################################################################


def buy_backS(request):
    # Get the logged-in seller
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')

    seller = SellerData.objects.filter(seller_id=seller_id).first()
    # Assuming seller is logged in

    # Get all buyback requests for this seller
    seller_requests = SellerRequest.objects.filter(seller=seller)

    return render(request, "Sbuy_back.html", {"seller_requests": seller_requests})


#######################################################################################################################

def customization_details(request, buyback_id):
    buyback = get_object_or_404(Buyback, buyback_id=buyback_id)
    products = Customedesign.objects.filter(buyback=buyback)  # Get all products linked to this buyback ID
    seller_request = SellerRequest.objects.filter(buyback=buyback).first()  # Get seller request for this buyback

    return render(
        request,
        "t.html",
        {"buyback": buyback, "products": products, "seller_request": seller_request}
    )


#######################################################################################################################


def accept_request(request, buyback_id):
    buyback = get_object_or_404(Buyback, buyback_id=buyback_id)
    seller_request = get_object_or_404(SellerRequest, buyback=buyback)
    custom_design = seller_request.custom_design

    # Corrected: Fetch user from Buyback
    if buyback.user:
        user_email = buyback.user.email
        user_name = buyback.user.username
    else:
        messages.error(request, "No user associated with this buyback request.")
        return redirect("seller_dashboard")

    # Fetch related product details from Customedesign
    product_name = custom_design.name  # Custom design name
    product_category = custom_design.clothing  # Assuming 'clothing' represents the category
    product_condition = custom_design.Customer_status

    # Customer status as condition

    if request.method == "POST":
        total_price = request.POST.get("totalPrice")
        description = request.POST.get("description")
        total_days = request.POST.get("totalDays")

        if custom_design.Customer_status == "Buy Request" and seller_request.status == "Pending":
            seller_request.status = "Approve"
            seller_request.customization_done = "Pending"
            custom_design.Customer_status = "Buy Request"
            buyback.buyback_status = "Buy"
    
            # Convert total_price to Decimal before addition
            custom_design.customize_total_price = Decimal(total_price)
            print("customize total price", custom_design.customize_total_price)
            custom_design.how_many_days = total_days
            print("how many days", custom_design.how_many_days)
            # Calculate security as 50% of the customize_total_price
            custom_design.security = custom_design.customize_total_price * Decimal('0.5')
            if description:
                custom_design.description = description
                print("description", custom_design.description)


        elif custom_design.Customer_status == "Purchase Request" and seller_request.status == "Pending" :
            seller_request.status = "Approve"
            custom_design.Customer_status = "Purchase Request"
            buyback.buyback_status = "purchased make own product"




        # Save form data
        custom_design.name = f"Customization {product_name} {user_name}"
        seller_request.save()
        custom_design.save()
        buyback.save()

        print("seller status" , seller_request.status)
        print("Custome status" , custom_design.Customer_status)
        print("buyback status" , buyback.bayback_status)
        print("customize total price", custom_design.customize_total_price)


        # Render HTML email template
        email_html_content = render_to_string("emails/Approve_buyrequest.html", {
            "user_name": user_name,
            "buyback_id": buyback_id,
            "product_name": custom_design.name,
            "product_category": product_category,
            "product_condition": product_condition,
            "total_price": total_price,
            "description": description,
            "total_days": total_days,
            "customization_status": seller_request.customization_done,
            "approval_date": now().strftime("%d-%m-%Y"),
        })
        email_plain_content = strip_tags(email_html_content)  # Convert HTML to plain text

        # Send email
        subject = "Your Buyback Customization Request is Approved!"
        email = EmailMultiAlternatives(subject, email_plain_content, settings.DEFAULT_FROM_EMAIL, [user_email])
        email.attach_alternative(email_html_content, "text/html")
        email.send()

        messages.success(request, f"Request for Buyback ID {buyback_id} approved successfully!")
        return redirect("customization_details", buyback_id=buyback_id)

    return redirect("customization_details", buyback_id=buyback_id)


#######################################################################################################################


def reject_request(request, buyback_id):
    print("reject request")
    buyback = get_object_or_404(Buyback, buyback_id=buyback_id)
    seller_request = get_object_or_404(SellerRequest, buyback=buyback)
    custom_design = seller_request.custom_design  # Fetch the related product

    # Corrected: Fetch user from Buyback
    if buyback.user:
        user_email = buyback.user.email
        user_name = buyback.user.username

        print("email" , user_email)
        print("name" , user_name)
    else:
        messages.error(request, "No user associated with this buyback request.")
        return redirect("seller_dashboard")

    # Fetch related product details from Customedesign
    product_name = custom_design.name  # Custom design name
    product_category = custom_design.clothing  # Assuming 'clothing' represents the category
    product_condition = custom_design.Customer_status  # Customer status as condition

    # Update statuses

    if custom_design.Customer_status == "Buy Request" and seller_request.status == "Pending":
        seller_request.status = "Rejected"
        custom_design.Customer_status = "Buy Request"
        buyback.bayback_status = "Pending"
    elif custom_design.Customer_status == "Purchase Request" and seller_request.status == "Pending":
        seller_request.status = "Rejected"
        custom_design.Customer_status = "Purchase Request"
        buyback.bayback_status = "Buy"


    # Keeping 'Buy' as per your requirement

    seller_request.save()
    custom_design.save()
    buyback.save()

    print("seller status" , seller_request.status)
    print("Custome status" , custom_design.Customer_status)

    # Render HTML email template
    email_html_content = render_to_string("emails/Reject_buyrequest.html", {
        "user_name": user_name,
        "buyback_id": buyback_id,
        "product_name": product_name,
        "product_category": product_category,
        "product_condition": product_condition,
        "rejection_date": now().strftime("%d-%m-%Y"),
    })
    email_plain_content = strip_tags(email_html_content)  # Convert HTML to plain text

    # Send email
    subject = "Your Buyback Customization Request is Rejected"
    email = EmailMultiAlternatives(subject, email_plain_content, settings.DEFAULT_FROM_EMAIL, [user_email])
    email.attach_alternative(email_html_content, "text/html")
    email.send()

    messages.success(request, f"Request for Buyback ID {buyback_id} rejected successfully!")
    return redirect("customization_details", buyback_id=buyback_id)

#######################################################################################################################




def send_customization_done(request, buyback_id):
    buyback = get_object_or_404(Buyback, buyback_id=buyback_id)
    seller_request = get_object_or_404(SellerRequest, buyback=buyback)
    custom_design = seller_request.custom_design

    if not buyback.user:
        messages.error(request, "No user associated with this buyback request.")
        return redirect("seller_dashboard")

    user_email = buyback.user.email
    user_name = buyback.user.username

    # Set customization done status if conditions match
    if custom_design.Customer_status == "Buy Request" and seller_request.status == "Approve":
        seller_request.customization_done = "Complete"
        seller_request.save()

    # Prepare context for email
    context = {
        "user_name": user_name,
        "buyback_id": buyback_id,
        "product_name": custom_design.name,
        "product_category": custom_design.clothing,
        "product_condition": custom_design.Customer_status ,

        "total_price": custom_design.customize_total_price,
        "total_days": custom_design.how_many_days,
        "approval_date": now().strftime("%d-%m-%Y"),
        "account_url": f"http://127.0.0.1:8000/Account/buyback_detail/{buyback_id}/"
        # Update this as per your app
    }

    email_html_content = render_to_string("emails/send_customization_done.html", context)
    email_plain_content = strip_tags(email_html_content)

    subject = "Your Customized Product is Ready – StyleSurfer"
    email = EmailMultiAlternatives(subject, email_plain_content, settings.DEFAULT_FROM_EMAIL, [user_email])
    email.attach_alternative(email_html_content, "text/html")
    email.send()

    messages.success(request, f"Customization completion email sent for Buyback ID {buyback_id}.")
    return redirect("customization_details", buyback_id=buyback_id)

#######################################################################################################################
#######################################################################################################################
