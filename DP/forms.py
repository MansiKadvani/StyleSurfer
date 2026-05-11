from django import forms
from .models import DPData

######################################################################################

class DPForm(forms.ModelForm):
    class Meta:
        model = DPData
        fields = ['Dname', 'Demail', 'Dnumber' , 'Daddress']
        
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            for field in self.fields.values():
                field.required = False  
                
######################################################################################
######################################################################################
