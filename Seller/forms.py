
#import

from django import forms
from .models import SellerData

#######################################################################################################################
#######################################################################################################################

class sellerForm(forms.ModelForm):
    class Meta:
        model = SellerData
        fields = ['sname', 'semail', 'snumber' , 'saddress']
        
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing (i.e., instance is provided), make fields not required
        if self.instance and self.instance.pk:
            for field in self.fields.values():
                field.required = False  # Make all fields non-required for editing
                
#######################################################################################################################
#######################################################################################################################