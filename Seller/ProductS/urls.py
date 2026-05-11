from django.urls import path
from . import views

#######################################################################################################################
#######################################################################################################################

urlpatterns = [

    path('catproduct/', views.catproduct, name='ProductS/catproduct'),

    path('categories/<int:category_id>/add-product/', views.addproduct, name='ProductS/addproduct'),

    path('categories/<int:category_id>/products/', views.ownproduct, name='ProductS/ownproduct'),

    path('product/update/<int:category_id>/<int:product_id>/', views.updateProduct, name='ProductS/updateproduct'),

    path('product/delete/<int:product_id>/', views.deleteProduct, name='ProductS/deleteproduct'),

    path('search/', views.search_products, name='search_products'),

    path('rcategories/', views.rcatproduct, name='ProductS/rcatproduct'),

    path('rproduct/rdelete/<int:rproduct_id>/', views.rdeleteProduct, name='ProductS/rdeleteproduct'),

    path('rproduct/rupdate/<int:rcategory_id>/<int:rproduct_id>/', views.rupdateProduct, name='ProductS/rupdateproduct'),

    path('rcategories/<int:rcategory_id>/rproducts/', views.resellproduct, name='ProductS/resellproduct'),

    path('resell/<int:product_id>/<int:seller_id>/', views.mark_as_reselling, name='ProductS/resell'),
    
]

#######################################################################################################################
#######################################################################################################################