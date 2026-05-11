from django.contrib import admin
from django.urls import path , include
from . import views

#######################################################################################################################
#######################################################################################################################

urlpatterns = [
    
    path('view_order/', views.view_order , name='view_order'),

    path('resell_order/<str:order_id>/', views.detail_resell , name='detail_resell'),

    path('order_detail/<str:order_id>/', views.order_detail, name='order_detail'),

]