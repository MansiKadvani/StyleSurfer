from django.contrib import admin
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlencode
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import DPData

######################################################################################

@admin.register(DPData)
class DPAdmin(admin.ModelAdmin):
    list_display = ['DP_id', 'Dname', 'Demail', 'Dnumber', 'Daddress', 'is_active']

    def save_model(self, request, obj, form, change):
        if not change:  
            obj.is_active = False  
            obj.save()

            current_site = get_current_site(request)
            reset_link = f"http://127.0.0.1:8000/DP/Dset_password/?email={obj.Demail}"

            html_message = render_to_string("emails/Dset_password_email.html", {
                'name': obj.Dname,
                'email': obj.Demail,
                'number': obj.Dnumber,
                'address': obj.Daddress,
                'reset_link': reset_link,
                'company_name': "StyleSurfer",
                'company_email': "stylesurfer3@gmail.com",
            })
            plain_message = strip_tags(html_message)

            send_mail(
                subject="Action Required: Set Your Password",
                message=plain_message,
                from_email="admin@stylesurfer.com",
                recipient_list=[obj.Demail],
                html_message=html_message
            )
        super().save_model(request, obj, form, change)

######################################################################################
######################################################################################
