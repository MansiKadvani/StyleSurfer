from django.urls import path , include
from django.contrib import admin
from . import views

######################################################################################
######################################################################################


urlpatterns = [
    path('base/', views.base , name='base'),
    path('Account/', include('Customer.Account.urls')),
    path('', views.home , name='home'),
    path('Product/', include('Customer.Product.urls')),
    path('Reselling/', include('Customer.Reselling.urls')),
    path('Women/',views.women , name='women'),
    path('men/',views.men , name='men'),
    path('bridal/',views.bridal , name='bridal'),
    path('groom/',views.groom , name='groom'),
    path('Cart/', include('Customer.Cart.urls')),
    path('privacy_policy' , views.privacy_policy , name='privacy_policy'),
    path('terms_condition' , views.terms_condition , name='terms_condition'),

    path('SpinToWin/', include('Customer.SpinToWin.urls')),
    path('SellWithUs/', include('Customer.SellWithUs.urls')),

    path('search/' , views.search , name='search'),

    path('order/',  include('Customer.Order.urls')),

    path('Buy_Back/',include('Customer.Buy_Back.urls')),


    path('base1/' , views.base1 , name='base1'),

    path('brand/<str:brand_name>/', views.brand_products, name='brand_products'),

    path('ocassion/<str:ocassion_name>/', views.ocassion, name='ocassion'),


]

######################################################################################
######################################################################################
