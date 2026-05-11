from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator, RegexValidator
import random
from django.utils import timezone
from django.utils.timezone import now
from Seller.ProductS.models import Product , Resell_Product
from Customer.SellWithUs.models import CustomerSellerProduct

######################################################################################
######################################################################################

class Register(models.Model):
    customer_id = models.AutoField(primary_key=True)
    username = models.CharField(
        max_length=50, 
        default="",
        validators=[MinLengthValidator(3)] 
    )
    email = models.EmailField(
        max_length=30,
        default="",
        validators=[EmailValidator(message="Enter a valid email address.")]
    )
    number = models.CharField(
        max_length=10,
        default="",
        validators=[RegexValidator(regex=r'^(\+\d{1,3}[- ]?)?\d{10}$', message="Enter a valid 10-digit phone number.")]
    )
    password = models.CharField(
        max_length=128,
        default="",
       validators=[RegexValidator(regex=r'^(?=.[A-Z])(?=.[!@#$%^&()_+{}\[\]:;\"\'<>,.?~-])[A-Za-z\d!@#$%^&()_+{}\[\]:;\"\'<>,.?~-]{8,}$',
    message="Password must be at least 8 characters long, contain at least one uppercase letter, "
        "and one special character"
    )]
    )
    def check_password(self, password):
        print(self.password)
        if(self.password != password) : 
            return False
        else : 
            return True
    def __str__(self):
        return self.username

######################################################################################

class OTPVerification(models.Model):
    email = models.EmailField(default="example@gmail.com")
    otp = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_at = models.DateTimeField(null=True, blank=True)
    def generate_otp(self):
        self.otp = random.randint(100000, 999999)
        self.expiry_at = timezone.now() + timezone.timedelta(minutes=2)
        self.save()
    def is_expired(self):
        return timezone.now() > self.expiry_at

######################################################################################

class PasswordResetToken(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=now)
    is_used = models.BooleanField(default=False)

######################################################################################

class HelpRequest(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    issue = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

######################################################################################

class Review_Rating(models.Model) :
    user = models.ForeignKey(Register,on_delete=models.CASCADE)
    order_id = models.CharField(max_length=10)
    prod_id = models.PositiveIntegerField(default=0)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True, blank=True)
    sell_with_us = models.ForeignKey(CustomerSellerProduct,on_delete=models.CASCADE,null=True, blank=True)
    resell_product = models.ForeignKey(Resell_Product,on_delete=models.CASCADE,null=True, blank=True)
    rating = models.IntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

######################################################################################
######################################################################################