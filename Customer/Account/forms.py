from django import forms
from .models import Register
from ..SellWithUs.models import CustomerSellerProduct

######################################################################################
######################################################################################

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Register
        fields = ['username' , 'email' , 'number']

######################################################################################

class ProductForm(forms.ModelForm):
    class Meta:
        model = CustomerSellerProduct
        fields = ['csname', 'number', 'addr', 'pincode', 'name', 'description', 
                  'price', 'brand', 'color', 'category',
                  'image_front', 'image_side', 'image_back', 'boutique']
    def save(self, commit=True):
        """Override save to recalculate rental price"""
        instance = super().save(commit=False)
        if 'price' in self.changed_data:
            instance.rental_price = instance.price / 2
        if commit:
            instance.save()
        return instance

######################################################################################
######################################################################################