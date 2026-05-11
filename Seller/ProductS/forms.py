from django import forms
from .models import Product , Resell_Product

#######################################################################################################################
#######################################################################################################################

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'rental_price', 'brand',  'color',  'discount_percentage', 'discount', 'image_front', 'image_side', 'image_back', 'buyback']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.buyback is not None:
                self.initial['buyback'] = str(self.instance.buyback)


    def clean_buyback(self):
        return self.cleaned_data.get('buyback', False)  # If checkbox is unchecked, it will return False


#######################################################################################################################

class rProductForm(forms.ModelForm):

    class Meta:
        model = Resell_Product
        fields = ['rname', 'rdescription', 'oprice', 'rbrand' , 'rcolor', 'rdiscount_percentage' , 'rimage_front', 'rimage_side', 'rimage_back']


#######################################################################################################################
#######################################################################################################################