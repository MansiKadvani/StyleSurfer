from django.db import models
from django.db.models import Max
from django.utils import timezone
from Seller.models import SellerData
from decimal import Decimal
from django.utils.timezone import now

#######################################################################################################################
#######################################################################################################################

class Category(models.Model):

    MAIN_CATEGORY_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Bride', 'Bride'),
        ('Groom', 'Groom'),
    ]
    main_category = models.CharField(max_length=50, choices=MAIN_CATEGORY_CHOICES)
    sub_category = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.main_category} - {self.sub_category}"

#######################################################################################################################

class rCategory(models.Model):

    rid = models.AutoField(primary_key=True)
    rMAIN_CATEGORY_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
        ('Bride', 'Bride'),
        ('Groom', 'Groom'),
    ]
    rmain_category = models.CharField(max_length=50, choices=rMAIN_CATEGORY_CHOICES)
    rsub_category = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.rmain_category} - {self.rsub_category}"

#######################################################################################################################

class SizeQuantity(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='size_quantities')
    size = models.CharField(max_length=20)
    quantity = models.PositiveIntegerField(default=0)

    def _str_(self):
        return f"{self.product.name} - {self.size}: {self.quantity}"
    
#######################################################################################################################

class Product(models.Model):
    prod_type = models.CharField(max_length=255, default="own_product")
    name = models.CharField(max_length=255, default="Unnamed Product")
    description = models.TextField(default="No description available.")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    brand = models.CharField(max_length=100, blank=True, null=True, default="No Brand")
    color = models.CharField(max_length=50, default="Not Specified")
    image_front = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image_side = models.ImageField(upload_to='product_images/', blank=True, null=True)
    image_back = models.ImageField(upload_to='product_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", default=1)
    seller = models.ForeignKey(SellerData, on_delete=models.CASCADE, related_name="products", default=1)
    category_specific_id = models.PositiveIntegerField(null=True, blank=True, editable=False, default=0)
    discount_percentage = models.PositiveIntegerField(default=30, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    buyback = models.BooleanField(default=False)
    test_quantity = models.TextField(default="No test quantity available.")
    discount = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} (Category-specific ID: {self.category_specific_id})"

#######################################################################################################################

class rSizeQuantity(models.Model):
    Resell_Product = models.ForeignKey('Resell_Product', on_delete=models.CASCADE, related_name='size_quantities')
    rsize = models.CharField(max_length=20)
    rquantity = models.PositiveIntegerField(default=1)

    def _str_(self):
        return f"{self.product.name} - {self.size}: {self.quantity}"

#######################################################################################################################

class Resell_Product(models.Model):
    prod_type = models.CharField(max_length=255,default="resell_product")
    rid = models.AutoField(primary_key=True)
    rname = models.CharField(max_length=255)
    rdescription = models.TextField()
    oprice = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rprice = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    rbrand = models.CharField(max_length=100, blank=True, null=True)
    rcolor = models.CharField(max_length=50)
    rimage_front = models.ImageField(upload_to='product_images/', blank=True, null=True)
    rimage_side = models.ImageField(upload_to='product_images/', blank=True, null=True)
    rimage_back = models.ImageField(upload_to='product_images/', blank=True, null=True)
    rdiscount_percentage = models.PositiveIntegerField(default=30)
    rcategory = models.ForeignKey(rCategory, on_delete=models.CASCADE, related_name="resell_products", default=1)
    rcategory_specific_id = models.PositiveIntegerField(null=True, blank=True, editable=False)
    rseller = models.ForeignKey(SellerData, on_delete=models.CASCADE, related_name="resell_products")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rname} (rCategory-specific ID: {self.rcategory_specific_id})"

#######################################################################################################################
#######################################################################################################################