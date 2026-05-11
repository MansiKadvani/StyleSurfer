from django.urls import path, include
from . import views

######################################################################################
######################################################################################

urlpatterns = [

    path('cart_detail/', views.cart_detail, name='cart_detail'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('apply_voucher/', views.apply_voucher, name='apply_voucher'),
    path('checkout_cart/', views.checkout_cart, name='checkout_cart'),
    path('order_form/', include('Customer.Order.urls')),

]

######################################################################################
######################################################################################

