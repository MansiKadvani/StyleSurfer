
from .forms import ProductForm , rProductForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect , render
from django.contrib import messages
from .models import Product, Resell_Product, SizeQuantity, rSizeQuantity, SellerData, rCategory , Category
from decimal import Decimal

#######################################################################################################################
#######################################################################################################################

#  own product category
def catproduct(request):
    categories = Category.objects.all()
    page = request.GET.get('page', 1)  
    items_per_page = 9  
    paginator = Paginator(categories, items_per_page)
    try:
        category_page = paginator.page(page)
    except PageNotAnInteger:
       category_page = paginator.page(1) 
    except EmptyPage:
        category_page = paginator.page(paginator.num_pages)
    return render(request, 'own/catproduct.html', {'categories': categories , 'category': category_page})


#######################################################################################################################

def search_products(request):
    categories = Category.objects.all()
    query = request.GET.get('q', '').strip()  
    category = Category.objects.none()

    if query:
        category = categories.filter(
            Q(main_category__icontains=query) | 
            Q(sub_category__icontains=query)
        )
    
    # Pagination
    page = request.GET.get('page', 1)
    items_per_page = 10
    paginator = Paginator(category, items_per_page)

    try:
        category_page = paginator.page(page)
    except PageNotAnInteger:
        category_page = paginator.page(1)
    except EmptyPage:
        category_page = paginator.page(paginator.num_pages)

    return render(request, 'own/catproduct.html', {
        'category': category_page,
        'query': query
    })

#######################################################################################################################

def rcatproduct(request):
    rcategories = rCategory.objects.all() 
    page = request.GET.get('page', 1)  
    items_per_page = 9  
    paginator = Paginator(rcategories, items_per_page)
    try:
        category_page = paginator.page(page)
    except PageNotAnInteger:
       category_page = paginator.page(1) 
    except EmptyPage:
        category_page = paginator.page(paginator.num_pages)
    return render(request, 'reselling/rcatproduct.html', {'categories': category_page})


#######################################################################################################################

def ownproduct(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    seller_id = request.session.get('seller_id')
    if not seller_id :
        return redirect('seller_login')
    seller = get_object_or_404(SellerData , seller_id = seller_id)
    products = Product.objects.filter(category=category , seller = seller)

    page = request.GET.get('page', 1)  
    items_per_page = 9  
    paginator = Paginator(products, items_per_page)
    try:
        product_page = paginator.page(page)
    except PageNotAnInteger:
       product_page = paginator.page(1) 
    except EmptyPage:
        product_page = paginator.page(paginator.num_pages)

    return render(request, 'own/ownproduct.html', {'category': category, 'products': product_page , 'seller' : seller})

#######################################################################################################################

def addproduct(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')
    seller = get_object_or_404(SellerData, seller_id=seller_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.category = category
            product.seller = seller
            product.save()

            # Process size and quantity
            sizes = request.POST.getlist('size[]')
            quantities = request.POST.getlist('quantity[]')

            for size, quantity in zip(sizes, quantities):
                if size and quantity.isdigit():
                    SizeQuantity.objects.create(product=product, size=size, quantity=int(quantity))

            messages.success(request, 'Product added successfully!')
            return redirect('ProductS/ownproduct', category_id=category.id)
    else:
        form = ProductForm()

    return render(request, 'own/addproduct.html', {'form': form, 'category': category})


#######################################################################################################################

def updateProduct(request, product_id, category_id):
    category = get_object_or_404(Category, id=category_id)
    product = get_object_or_404(Product, id=product_id)

    available_sizes = ["XS", "S", "M", "L", "XL", "XXL"]  # Example sizes, replace with actual

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            form.save()
            SizeQuantity.objects.filter(product=product).delete()

            discount = request.POST.get('discount')
            
            if discount : 
                discount = Decimal(discount)
                original_price = product.rental_price
                product.rental_price = original_price - (original_price * discount / Decimal('100'))
                product.discount = discount  # Optional, only if you have a discount field
                product.save()

            sizes = request.POST.getlist("sizes[]")
            quantities = request.POST.getlist("quantities[]")

            for size, quantity in zip(sizes, quantities):
                if size and quantity.isdigit():
                    SizeQuantity.objects.create(product=product, size=size, quantity=int(quantity))

            messages.success(request, 'Product updated successfully!')
            return redirect('ProductS/ownproduct', category.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)

    size_quantity_data = product.size_quantities.all()

    return render(
        request,
        'own/updateproduct.html',
        {'form': form, 'product': product, 'size_quantity_data': size_quantity_data, 'available_sizes': available_sizes}
    )


#######################################################################################################################

def deleteProduct(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('ProductS/ownproduct', category_id=product.category.id)

#######################################################################################################################

def resellproduct(request, rcategory_id):
    rcategory = get_object_or_404(rCategory, rid=rcategory_id)
    seller_id = request.session.get('seller_id')
    if not seller_id : 
        return redirect('seller_login')
    seller = get_object_or_404(SellerData , seller_id = seller_id)
    rproduct = Resell_Product.objects.filter(rcategory=rcategory , rseller = seller)

    page = request.GET.get('page', 1)  
    items_per_page = 9  
    paginator = Paginator(rproduct, items_per_page)
    try:
        product_page = paginator.page(page)
    except PageNotAnInteger:
       product_page = paginator.page(1) 
    except EmptyPage:
        product_page = paginator.page(paginator.num_pages)

    return render(request, 'reselling/resellingproduct.html', {'rcategory': rcategory, 'products': product_page , 'seller' : seller})

#######################################################################################################################

def rupdateProduct(request, rproduct_id, rcategory_id):
    rcategory = get_object_or_404(rCategory, rid=rcategory_id)
    rproduct = get_object_or_404(Resell_Product, rid=rproduct_id)

    available_sizes = ["XS", "S", "M", "L", "XL", "XXL"]  # Example sizes, replace with actual

    if request.method == 'POST':
        rform = rProductForm(request.POST, request.FILES, instance=rproduct)
        print(rform)
        if rform.is_valid():
            rproduct.rprice = rproduct.oprice - round((rproduct.oprice * rproduct.rdiscount_percentage) / 100, 2)
            rform.save()
            rSizeQuantity.objects.filter(Resell_Product=rproduct).delete()
            sizes = request.POST.getlist("sizes[]")
            quantities = request.POST.getlist("quantities[]")
            for size, quantity in zip(sizes, quantities):
                if size and quantity.isdigit():
                    rSizeQuantity.objects.create(Resell_Product=rproduct, rsize=size, rquantity=int(quantity))
            messages.success(request, 'Product updated successfully!')
            return redirect('ProductS/resellproduct', rcategory.rid)
        else:
            print('Please correct the errors below.')
    else:
        rform = rProductForm(instance=rproduct)
    size_quantity_data = rproduct.size_quantities.all()
    return render(request, 'reselling/rupdateproduct.html', {'rform': rform, 'rproduct': rproduct , 'size_quantity_data': size_quantity_data, 'available_sizes': available_sizes})


#######################################################################################################################


def rdeleteProduct(request, rproduct_id):
    rproduct = get_object_or_404(Resell_Product, rid=rproduct_id)
    rproduct.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('ProductS/resellproduct', rcategory_id=rproduct.rcategory.rid)

#######################################################################################################################


def mark_as_reselling(request, product_id, seller_id):
    product = get_object_or_404(Product, id=product_id)
    seller = get_object_or_404(SellerData, seller_id=seller_id)

    # Get the corresponding Resell Category
    try:
        resell_cat = rCategory.objects.get(rsub_category=product.category.sub_category)
    except rCategory.DoesNotExist:
        messages.error(request, "No matching Resell Category found for the product's category.")
        return redirect('ProductS/ownproduct', category_id=product.category.id)

    # Calculate reselling price
    reselling_price = product.price - round((product.price * product.discount_percentage) / 100, 2)

    # Create Resell Product
    resell_product = Resell_Product.objects.create(
        rname=product.name,
        rdescription=product.description,
        oprice=product.price,
        rprice=reselling_price,
        rbrand=product.brand,
        rcolor=product.color,
        rimage_front=product.image_front,
        rimage_side=product.image_side,
        rimage_back=product.image_back,
        rdiscount_percentage=product.discount_percentage,
        rseller=seller,
        rcategory=resell_cat
    )

    # Transfer size-quantity pairs correctly
    size_quantities = SizeQuantity.objects.filter(product=product)
    for sq in size_quantities:
        rSizeQuantity.objects.create(
            Resell_Product=resell_product,  # Correct Foreign Key
            rsize=sq.size,  # Assign proper size
            rquantity=sq.quantity  # Assign proper quantity
        )

    # Delete original product and its size-quantity records
    size_quantities.delete()
    product.delete()

    messages.success(request, f"Product '{product.name}' is now available for reselling.")
    return redirect('ProductS/ownproduct', category_id=product.category.id)


#######################################################################################################################
#######################################################################################################################