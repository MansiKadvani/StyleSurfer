from django.contrib import admin
from django.urls import path , include
from . import views 

######################################################################################
######################################################################################

urlpatterns = [
    
    path('prod_desc/<int:product_id>/', views.prod_desc , name='prod_desc'),
    path('product/<str:category_name>/' , views.product , name = 'product'),
    path('product_filter/<str:category_name>/' , views.product_filter , name = 'product_filter'),
    path('product_list/<str:category_name>/' , views.product_list , name = 'product_list')
]

######################################################################################
######################################################################################
