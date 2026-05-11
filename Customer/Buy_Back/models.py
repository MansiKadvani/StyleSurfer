from django.db import models
from django.utils.timezone import now
from Customer.Account.models import Register
from django.db import models
from datetime import datetime

######################################################################################
######################################################################################

class Buyback(models.Model):
    buyback_id = models.CharField(max_length=10, unique=True )
    user = models.ForeignKey(Register, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    buyback_status = models.CharField(max_length=255, choices=[("Buy", "Buy"), ("Back", "Back"), ("purchased make own product", "purchased make own product")  , ("Pending", "Pending")], default="Pending")

    def __str__(self):
        return f"Buyback by {self.user}"

######################################################################################

class Customedesign(models.Model):
    buyback = models.ForeignKey(Buyback, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="Unnamed Product")
    brand = models.CharField(max_length=255, default="Unnamed Brand")
    prod_type = models.CharField(max_length=255, default="Buy_back")
    fimage = models.URLField(blank=True, null=True)
    simage = models.URLField(blank=True, null=True)
    bimage = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    security = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    Customer_status = models.CharField(max_length=20, choices=[("Buy Request", "Buy Request"), ("Back Request", "Back Request"), ("pending Request", "pending Request") ,  ("Purchase Request", "Purchase Request")], default="Pending Request")
    seller = models.ForeignKey('Seller.SellerData', on_delete=models.CASCADE)

    days = models.PositiveIntegerField(default=20)
    how_many_days = models.PositiveIntegerField(default=20)
    description = models.TextField(blank=True, null=True)
    delivery_date = models.DateField(null=True, blank=True)
    rental_date = models.TextField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    gender = models.CharField(max_length=20)
    clothing = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=20 , default='size')
    embroidery_style = models.CharField(max_length=100, default='Standard')
    stone_size = models.CharField(max_length=50, default='Medium')
    placement = models.CharField(max_length=100, default='Front')
    density = models.CharField(max_length=50, default='none')
    thread_option = models.CharField(max_length=100, default='none')
    mirror_shape = models.CharField(max_length=100, default='none')
    mirror_size = models.CharField(max_length=100, default='none')
    border_color = models.CharField(max_length=100, default='none')
    design_style = models.CharField(max_length=100, default='none')
    addons = models.CharField(max_length=100, default='None')
    uploaded_file = models.FileField(upload_to="design_uploads/")

    submitted_at = models.DateTimeField(default=now)
    customize_total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    customize_seller_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Design Submission ({self.gender}, {self.name})"

######################################################################################

class SellerRequest(models.Model):
    buyback = models.ForeignKey(Buyback, on_delete=models.CASCADE)
    seller = models.ForeignKey('Seller.SellerData', on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField()
    custom_design = models.ForeignKey(Customedesign, on_delete=models.CASCADE)
    customization_done = models.TextField(max_length=20,
                                          choices=[("Pending", "Pending"), ("Complete", "Complete"), ], default="Pending")
    status = models.CharField(max_length=20, choices=[("Pending", "Pending"), ("Approve", "Approve"), ("Rejected", "Rejected")], default="Pending")

    def __str__(self):
        return f"Request for {self.buyback.buyback_id} to Seller {self.seller.sname }"

######################################################################################
######################################################################################