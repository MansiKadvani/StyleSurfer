from django.contrib import admin
from django.urls import path  , include
from . import views

######################################################################################
######################################################################################

urlpatterns = [
    
    path('Dset_password/', views.Dset_password, name='Dset_password'),
    path('DP_login/', views.DP_login , name='DP_login'),
    path('Dlogout/', views.Dlogout , name='Dlogout'),
    path('Dforgot_password/', views.Dforgot_password, name='Dforgot_password'),
    path('Dreset_password/<str:token>/', views.Dreset_password, name='Dreset_password'),
    
    
    path('Ddashboard/', views.Ddashboard , name='Ddashboard'),
    
    path('base_dp/', views.base_dp , name='base_dp'),

    path('Dprofile/', views.Dprofile , name='Dprofile'),    
    

    path('Daccount/', views.Daccount , name='Daccount'),
    
    path('Dpassword/', views.Dpasword , name='Dpasword'),

    path('Dorder/' , include('DP.OrderD.urls')) ,
    
]

######################################################################################
######################################################################################
