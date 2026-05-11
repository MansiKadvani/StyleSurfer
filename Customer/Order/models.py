from django.db import models
from Customer.Account.models import Register
from decimal import Decimal
from datetime import datetime
import uuid
from django.utils import timezone
from Customer.Cart.models import Cart

######################################################################################
######################################################################################

class Order(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name="orders")
    first_name = models.CharField(max_length=50, default="name")
    last_name = models.CharField(max_length=50, default="name")
    email = models.EmailField(default="example@example.com")
    phone = models.CharField(max_length=15, default="0000000000")
    address1 = models.TextField(default="")
    address2 = models.TextField(default="")
    city = models.CharField(max_length=50, default="Rajkot")
    state = models.CharField(max_length=50, default="Gujarat")
    country = models.CharField(max_length=50, default="India")
    zip_code = models.CharField(max_length=10, default="000000")
    is_accepted = models.BooleanField(default=False)

    order_id = models.CharField(max_length=10, unique=True)
    order_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Processing", "Processing"),
                 ("Completed", "Completed")],
        default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_security = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    Grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    payment_method = models.CharField(max_length=20, blank=True, null=True ,
    choices = [("Cash_on_delivery", "Online")],
    ) 
    payment_date = models.DateTimeField(blank=True, null=True)

    payment_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"),
                 ("Completed", "Completed")],
        default="Pending"
    )

    security_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"),
                 ("Processing", "Processing"),
                 ("Refunded", "Refunded")],
        default="Pending"
    )
   

    is_permanent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_unique_order_id()
        super().save(*args, **kwargs)

    def generate_unique_order_id(self):
        while True:
            unique_id = str(uuid.uuid4())[:10].upper()  # Generate a 10-character UUID
            if not Order.objects.filter(order_id=unique_id).exists():
                return unique_id

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"

######################################################################################

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product_id = models.PositiveIntegerField(blank=True, null=True , default=None)
    rid = models.PositiveIntegerField(blank=True, null=True , default=None)
    name = models.CharField(max_length=255, default="Unknown")
    brand = models.CharField(max_length=255, default="Generic")
    image = models.URLField(blank=True, null=True, default="")
    color = models.CharField(max_length=255, blank=True, null=True, default="")
    size = models.CharField(max_length=10, blank=True, null=True, default="")
    days = models.PositiveIntegerField(default=1)
    product_order_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("delivered", "delivered"),
                 ("Completed", "Completed"), ("Returned", "Returned")],

        default="Pending"
    )
    product_payment_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"),
                 ("Completed", "Completed")],
        default="Pending"
    )

    product_security_status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"),
                 ("Completed", "Completed")],
        default="Pending"
    )
    delivery_date = models.DateField(null=True, blank=True)
    rental_date = models.TextField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    security = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prod_type = models.CharField(max_length=255,null=True,blank=True)

    def __str__(self):
        return f"{self.name} (x{self.quantity})"

######################################################################################
######################################################################################

