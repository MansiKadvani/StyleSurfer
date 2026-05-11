from django.contrib import admin
from django.urls import path , include
from . import views

######################################################################################
######################################################################################

urlpatterns = [
    
    path('resell/', views.resell , name='resell'),

    path('rmen/', views.rmen , name='rmen'),

    path('rwomen/', views.rwomen , name='rwomen'),

    path('men_product_filter/' , views.men_product_filter , name = 'men_product_filter'),

    path('men_product_list/' , views.men_product_list , name = 'men_product_list'),

    path('women_product_filter/' , views.women_product_filter , name = 'women_product_filter'),

    path('women_product_list/' , views.women_product_list , name = 'women_product_list'),

    path('Rprod_desc/<int:Resell_Product_rid>/', views.Rprod_desc , name='Rprod_desc'),

    path('Reselling/',views.Reselling , name='Reselling'),

    path('RProductList/' , views.RProductList , name='RProductList'),

    path('RProductFilter/', views.RProductFilter , name='RProductFilter'),

]