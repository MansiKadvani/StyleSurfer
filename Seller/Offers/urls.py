from django.urls import path
from . import views

urlpatterns = [
    
    path('offer/', views.offer, name='offer'),
    path('brand/', views.brand, name='brand'),
    path('brand_view/<str:brand_name>/' , views.brand_view , name='brand_view'),
    path('category/', views.category, name='category'),
    path('category_view/<str:category_name>/' , views.category_view , name='category_view')
]