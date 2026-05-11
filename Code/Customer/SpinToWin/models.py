from django.db import models
from Customer.Account.models import Register
import random
import string
from django.utils.timezone import now
from datetime import timedelta
from django.db import models
from django.utils.timezone import now


######################################################################################
######################################################################################

class SpinReward(models.Model):
    label = models.CharField(max_length=20)
    value = models.IntegerField()
    question = models.TextField()

    def __str__(self):
        return self.question
    
######################################################################################

class UserSpin(models.Model):
    user =  models.ForeignKey(Register,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    count = models.IntegerField(default=0)
    reward = models.IntegerField(default=0)

######################################################################################

class Voucher(models.Model):
    discount = models.PositiveIntegerField()
    vprice = models.IntegerField()
    description = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.description} - Discount: {self.discount}%"

    def is_expired(self):
        """Check if the voucher has expired."""
        return now() > self.expires_at

    @classmethod
    def delete_expired_vouchers(cls):
        """Delete expired vouchers from the Voucher model."""
        expired_vouchers = cls.objects.filter(expires_at__lt=now())
        count = expired_vouchers.count()
        expired_vouchers.delete()
        print(f"{count} expired voucher(s) deleted from the Voucher model.")

######################################################################################

class RedeemedVoucher(models.Model):
    code = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    user = models.ForeignKey(Register, on_delete=models.CASCADE)  # Replace "Register" with your actual user model
    voucher = models.ForeignKey(Voucher, null=True, blank=True, on_delete=models.SET_NULL)  # Replace "Voucher" with your actual voucher model
    redeemed_at = models.DateTimeField(auto_now_add=True)
    _status = models.CharField(max_length=20, default="Redeemed")
    is_active = models.BooleanField(default=True)


    @property
    def status(self):
        """Determine and return the current status of the redeemed voucher."""
        if self.voucher is None or (self.voucher and self.voucher.is_expired()):
            if self._status != "Expired":  # Update status only if it's not already expired
                self._status = "Expired"
                self.save(update_fields=["_status"])  # Save only the status field to avoid recursion
            return "Expired"
        return self._status

    def save(self, *args, **kwargs):
        """Override save method to delete expired vouchers after 1 day."""
        if self._status == "Expired":
            expiry_threshold = self.redeemed_at + timedelta(days=1)
            if now() > expiry_threshold:
                self.delete()  
                return  
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.status}"

######################################################################################

class redeem(models.Model) : 
    user_redeem_voucher = models.ForeignKey(RedeemedVoucher,on_delete=models.CASCADE)

    def __str__(self) : 
        return f"{self.user_redeem_voucher.user}"
    
######################################################################################
######################################################################################
