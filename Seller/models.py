
# import

from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator, RegexValidator
from django.utils.timezone import now


########################################################################################################################
########################################################################################################################

class SellerData(models.Model):  # Class name follows PascalCase as per convention
    seller_id = models.AutoField(primary_key=True)

    sname = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(3)],
        default="",
    )

    semail = models.EmailField(
        max_length=250,
        default="",
        validators=[EmailValidator(message="Enter a valid email address.")],
    )

    snumber = models.CharField(
        max_length=10,
        default="",
        validators=[
            RegexValidator(
                regex=r"^(\+\d{1,3}[- ]?)?\d{10}$",
                message="Enter a valid 10-digit phone number.",
            )
        ],
    )

    saddress = models.CharField(
        max_length=500,
        default="",
    )

    spassword = models.CharField(max_length=128,blank=True)  # Store hashed passwords


    is_active = models.BooleanField(default=False)  # Seller can log in only if active

    def check_password(self, password):
        print(self.spassword)
        if(self.spassword != password) : 
            return False
        else : 
            return True
        
    class Meta:
        verbose_name = "Seller"
        verbose_name_plural = "Seller"


#######################################################################################################################

# token psw reset model

class PasswordResetToken(models.Model):
    user = models.ForeignKey(SellerData, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=now)
    is_used = models.BooleanField(default=False)

########################################################################################################################
########################################################################################################################
