from django.contrib import admin
from .models import CustomerSellerReq, CustomerSellerProduct , Customerproduct_SizeQuantity , Customersell_SizeQuantity
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

######################################################################################
######################################################################################

class CustomerSellerReqAdmin(admin.ModelAdmin):
    list_display = ('csname', 'email', 'status')
    list_filter = ('status',)
    search_fields = ('name', 'csname', 'email')
    actions = ['approve_request', 'reject_request', 'verify_product']

    def approve_request(self, request, queryset):
        queryset.update(status='Approved')
        for seller_request in queryset:
            self.send_status_email(seller_request, 'approved')

    approve_request.short_description = "Approve selected requests"

    def reject_request(self, request, queryset):
        queryset.update(status='Rejected')
        for seller_request in queryset:
            self.send_status_email(seller_request, 'rejected')

    reject_request.short_description = "Reject selected requests"

    def verify_product(self, request, queryset):
        queryset.update(status='Verified')
        for seller_request in queryset:

            new_product = CustomerSellerProduct.objects.create(
                csname=seller_request.csname,
                number=seller_request.number,
                addr=seller_request.addr,
                pincode=seller_request.pincode,
                email=seller_request.email,
                boutique=seller_request.boutique,
                name=seller_request.name,
                brand=seller_request.brand,
                description=seller_request.description,
                price=seller_request.price,
                rental_price=seller_request.price / 2 ,
                color=seller_request.color,
                category=seller_request.category,
                image_front=seller_request.image_front,
                image_back=seller_request.image_back,
                image_side=seller_request.image_side,
                status='active'
            )

            print("Verifying Product:", seller_request.name)

            size_qty_set = seller_request.CustomerSellerReq_size_quantities.all()
            print("Size-Quantity Set:", size_qty_set)

            for sq in size_qty_set:
                print(f"Creating for size: {sq.size}, quantity: {sq.quantity}")
                Customerproduct_SizeQuantity.objects.create(
                    product=new_product,
                    size=sq.size,
                    quantity=sq.quantity
                )

            seller_request.delete()
            self.send_status_email(seller_request, 'verified')

    verify_product.short_description = "Verify selected products"

    def send_status_email(self, seller_request, status):
        html_message = render_to_string('emails/status_notification_email.html', {
            'status': status,
            'csname': seller_request.csname,
            'product_name': seller_request.name,
        })
        subject = f"Your product '{seller_request.name}' has been {status}"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [seller_request.email]
        
        email_message = EmailMultiAlternatives(subject, '', from_email, recipient_list)
        email_message.attach_alternative(html_message, "text/html")
        email_message.send()

######################################################################################

admin.site.register(CustomerSellerReq, CustomerSellerReqAdmin)

######################################################################################

admin.site.register(CustomerSellerProduct)

######################################################################################

admin.site.register(Customerproduct_SizeQuantity)

######################################################################################

admin.site.register(Customersell_SizeQuantity)

######################################################################################
######################################################################################


