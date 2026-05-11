from django.urls import path, include
from . import views

######################################################################################
######################################################################################

urlpatterns = [

    path('Buydesc/<int:product_id>/', views.Buydesc, name='Buydesc'),
    path('submit_custom_design/', views.submit_custom_design, name='submit_custom_design'),
    path('buy_back_prod/', views.buy_back_prod, name='buy_back_prod'),
    path('buy1/<int:product_id>/', views.buy1, name='buy1'),
    path('buyback_products/', views.buyback_products, name='buyback_products'),

]

######################################################################################
######################################################################################

