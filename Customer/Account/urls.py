from django.urls import path 
from .import views

######################################################################################
######################################################################################

urlpatterns = [

    path('Registration/',views.Registration, name='Registration'),
    path('otpVerify/',views.otpVerify, name='otpVerify'),
    path('otpResend/',views.otpResend, name='otpResend'),
    path('login/', views.login, name='login'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<str:token>/', views.reset_password, name='reset_password'),
    path('logout/', views.logout, name='logout'),

    ##################################################################################
 
    path('account_home/' , views.account_home , name='account_home'),

    ##################################################################################

    path('profile/' , views.profile , name='profile'),

    ##################################################################################

    path('password/' , views.password , name='password'),

    ##################################################################################

    path('help/' , views.help , name='help'),

    ##################################################################################

    path('cvoucher/' , views.cvoucher , name='cvoucher'),

    ##################################################################################

    path('order/', views.order, name='order'),
    path('order_details/<str:order_id>/', views.order_details, name='order_details'),
    path('cancel_order/<str:order_id>/', views.cancel_order, name='cancel_order'),
    path("orders/<str:order_id>/pdf/", views.generate_order_pdf, name="generate_order_pdf"),

    ##################################################################################

    path("Sell/" , views.Sell,name="Sell"),
    path("Sell_view/<int:product_id>/" , views.Sell_view,name="Sell_view"),
    path('Sell/update/<int:product_id>/', views.updateSellWithUs, name='updateSellWithUs'),
    path('Sell/delete/<int:product_id>/', views.deleteSellWithUs, name='deleteSellWithUs'),
    path('submit_review/', views.submit_review, name='submit_review'),
    path("get_review/", views.get_review, name="get_review"),
    path("update_review/", views.update_review, name="update_review"),
    path('search/', views.search_products, name='search_products'),

    ##################################################################################

    path("Buy_back/", views.Buy_back, name="Buy_back"),
    path('buyback_detail/<str:buyback_id>/', views.buyback_detail, name='buyback_detail'),
    path('cancel_buyback_request/<str:buyback_id>/', views.cancel_buyback_request, name='cancel_buyback_request'),
    path("request_purchase/<str:buyback_id>/", views.request_purchase, name="request_purchase"),

    ##################################################################################

]

######################################################################################
######################################################################################
