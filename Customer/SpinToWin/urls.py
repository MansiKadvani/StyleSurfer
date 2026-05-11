from django.urls import path
from . import views

######################################################################################
######################################################################################

urlpatterns = [
    path('check_spin_limit/', views.check_spin_limit, name='check_spin_limit'),
    path('spin_voucher/' , views.spin_voucher , name='spin_voucher') , 
    path('redeem_voucher/<int:voucher_id>/' , views.redeem_voucher , name='redeem_voucher') , 
]

######################################################################################
######################################################################################
