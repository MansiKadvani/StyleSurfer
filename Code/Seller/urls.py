
# import

from django.contrib import admin
from django.urls import path , include
from . import views


########################################################################################################################
########################################################################################################################

urlpatterns = [
    
    path('Sset_password/', views.Sset_password, name='set_password'),

    path('seller_login/', views.seller_login , name='seller_login'),

    path('Sforgot_password/', views.Sforgot_password, name='Sforgot_password'),

    path('Sreset_password/<str:token>/', views.Sreset_password, name='Sreset_password'),

    path('Slogout/', views.Slogout , name='Slogout'),
    
    path('Sdashboard/', views.dashboard , name='Sdashboard'),

    path('base_seller/', views.base_seller , name='base_seller'),
    
    path('seller_profile/', views.Sprofile , name='Sprofile'),

    path('Saccount/', views.Saccount , name='Saccount'),
    
    path('Spassword/', views.Spasword , name='Spasword'),
    
    path('ProductS/',include('Seller.ProductS.urls')) ,

    path('sorder/' , include('Seller.OrderS.urls')),

    path('SBuyBack/' , include('Seller.BuyBackS.urls')),

    path('SOffer/' , include('Seller.Offers.urls')),

]

########################################################################################################################
########################################################################################################################