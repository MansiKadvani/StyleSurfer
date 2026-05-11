
# import

from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator, RegexValidator
from django.db import models
from django.utils.timezone import now

# ----------------------------------------------------------------------------------------

# DP Data Model

class DPData(models.Model):  # Class name follows PascalCase as per convention
    DP_id = models.AutoField(primary_key=True)

    Dname = models.CharField(
        max_length=50,
        validators=[MinLengthValidator(3)],
        default="",
    )

    Demail = models.EmailField(
        max_length=250,
        default="",
        validators=[EmailValidator(message="Enter a valid email address.")],
    )

    Dnumber = models.CharField(
        max_length=10,
        default="",
        validators=[
            RegexValidator(
                regex=r"^(\+\d{1,3}[- ]?)?\d{10}$",
                message="Enter a valid 10-digit phone number.",
            )
        ],
    )

    Daddress = models.CharField(
        max_length=500,
        default="",
    )

    Dpassword = models.CharField(max_length=128,blank=True)  # Store hashed passwords


    is_active = models.BooleanField(default=False)  # Seller can log in only if active


    def check_password(self, password):
        print(self.Dpassword)
        if(self.Dpassword != password) : 
            return False
        else : 
            return True
        
    class Meta:
        verbose_name = "Delivery Partner"
        verbose_name_plural = "Delivery Partners"
# ----------------------------------------------------------------------------------------

# token with resetpswd

class PasswordResetToken(models.Model):
    user = models.ForeignKey(DPData, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=now)
    is_used = models.BooleanField(default=False)

# ------------------------------------------------------------------------------------------