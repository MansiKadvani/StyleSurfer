from django.contrib import admin
from django.urls import path, include
from . import views

######################################################################################
######################################################################################

urlpatterns = [

    path('OrderD/', views.OrderD, name='OrderD'),
    path('Dorderdetails/<str:order_id>/', views.Dorderdetails, name='Dorderdetails'),
    path('reject_order/<str:order_id>/', views.reject_order, name='reject_order'),
    path('accept_order/<str:order_id>/', views.accept_order, name='accept_order'),
    path('Dorder_complete/<str:order_id>/<int:item_id>/', views.Dorder_complete, name='Dorder_complete'),

    path('Dsend_email/<str:order_id>/', views.Dsend_email, name='Dsend_email'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),

    path('DRsend_email/<str:order_id>/', views.DRsend_email, name='DRsend_email'),
    path('Rverify_otp/', views.Rverify_otp, name='Rverify_otp'),

    path('Dcashsend_email/<str:order_id>/', views.Dcashsend_email, name='Dcashsend_email'),
    path('Rcashverify_otp/', views.Rcashverify_otp, name='Rcashverify_otp'),

    path('Dsecuritysend_email/<str:order_id>/', views.Dsecuritysend_email, name='Dsecuritysend_email'),
    path('Rsecurityverify_otp/', views.Rsecurityverify_otp, name='Rsecurityverify_otp'),

    path('test12/', views.test12, name='test12'),

]

######################################################################################
######################################################################################
