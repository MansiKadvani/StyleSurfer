
# import

from django.contrib import admin
from django.core.mail import send_mail
from django.utils.http import urlencode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import SellerData

#######################################################################################################################
#######################################################################################################################

@admin.register(SellerData)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['seller_id', 'sname', 'semail', 'snumber', 'saddress', 'is_active']

    def save_model(self, request, obj, form, change):
        if not change:  # Only for new sellers
            obj.is_active = False  # Default to inactive
            obj.save()

            # Generate set-password URL
            current_site = get_current_site(request)
            reset_link = f"http://127.0.0.1:8000/Seller/Sset_password/?email={obj.semail}"

            # Render email content
            html_message = render_to_string("emails/Sset_password_email.html", {
                'name': obj.sname,
                'reset_link': reset_link,
                'company_name': "StyleSurfer",
                'company_email': "stylesurfer3@gmail.com",  # Replace with the actual logo URL
                'email': obj.semail,
                'number': obj.snumber,
                'address': obj.saddress,
            })
            plain_message = strip_tags(html_message)

            # Send email
            send_mail(
                subject="Action Required : Please Set Your Password",
                message=plain_message,
                from_email="admin@stylesurfer.com",
                recipient_list=[obj.semail],
                html_message=html_message
            )
        super().save_model(request, obj, form, change)
        
#######################################################################################################################
#######################################################################################################################