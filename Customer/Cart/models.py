from django.db import models
from Customer.Account.models import Register
from datetime import datetime
from decimal import Decimal
from datetime import date
from Seller.ProductS.models import Product , Resell_Product
from Customer.SpinToWin.models import RedeemedVoucher
from Seller.ProductS.models import Product , Resell_Product , SizeQuantity
from Customer.SellWithUs.models import CustomerSellerProduct
from ..Product.views import product
from Customer.Buy_Back.models import Customedesign
from Customer.SpinToWin.models import RedeemedVoucher

######################################################################################
######################################################################################

class Cart(models.Model):

    user = models.ForeignKey(Register, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_security = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2 , default=10.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    Grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())

    def get_total_price(self):
        return sum(item.price for item in self.items.all())

    def get_total_security(self):
        return sum(item.security for item in self.items.all())

    def get_grand_total(self, discount=0):
        total_price = self.get_total_price()
        total_security = self.get_total_security()
        shipping_cost = Decimal(10)
        discount = Decimal(discount)
        Grand_total = total_price + total_security + shipping_cost - discount
        return Grand_total

    def save_checkout_data(self, discount=0):
        self.total_price = self.get_total_price()
        self.total_security = self.get_total_security()
        self.Grand_total = self.get_grand_total(discount)
        self.discount = discount
        self.voucher_applied = discount > 0

        expired_vouchers = RedeemedVoucher.objects.filter(
            user=self.user,
            voucher__expires_at__lt=datetime.today()
        ).values_list('code', flat=True)
        self.expired_vouchers = list(expired_vouchers)
        self.save()

######################################################################################

class CartItem(models.Model): 
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    seller_email = models.EmailField(blank=True, null=True)
    product_id = models.PositiveIntegerField(blank=True, null=True , default=None)
    rid = models.PositiveIntegerField(blank=True, null=True , default=None)
    buyback_id = models.CharField(blank=True, null=True , max_length=10 , default=None)
    name = models.CharField(max_length=255, default="Unnamed Product")
    brand = models.CharField(max_length=255, default="Unnamed Brand")
    image = models.URLField(blank=True, null=True)
    color = models.CharField(max_length=10, blank=True, null=True)
    size = models.CharField(max_length=10, blank=True, null=True)
    stoke = models.CharField(max_length=20,blank=True,null=True)
    days = models.PositiveIntegerField(default=1)
    delivery_date = models.DateField(null=True, blank=True)
    rental_date = models.TextField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    security = models.DecimalField(max_digits=10, decimal_places=2, default=0.00 , null=True, blank=True)
    prod_type = models.CharField(max_length=255,null=True,blank=True)

    def save(self, *args, **kwargs):
        self.price = Decimal(self.price / max(self.quantity, 1)) * self.quantity
        self.security = Decimal(self.security / max(self.quantity, 1)) * self.quantity
        super().save(*args, **kwargs)

######################################################################################
######################################################################################
