from django.contrib import admin
from .models import Category , rCategory , Product , Resell_Product , SizeQuantity , rSizeQuantity

#######################################################################################################################
#######################################################################################################################

admin.site.register(Category)

admin.site.register(rCategory)

admin.site.register(Product)

admin.site.register(Resell_Product)

admin.site.register(SizeQuantity)

admin.site.register(rSizeQuantity)

#######################################################################################################################
#######################################################################################################################