from django.shortcuts import render , redirect , get_object_or_404
from Seller.models import SellerData
from Seller.ProductS.models import Product , Category

# Create your views here.
def offer(request):
    return render(request, 'offer.html')

def brand(request):
    seller_id = request.session.get('seller_id')
    if not seller_id :
        return redirect('seller_login')
    seller = get_object_or_404(SellerData , seller_id = seller_id)
    product = Product.objects.all()
    unique_brands = product.values_list('brand', flat=True).distinct() 
    return render(request, 'brand.html' , {'brand' : unique_brands})

from decimal import Decimal

def brand_view(request, brand_name):
    products = Product.objects.filter(brand=brand_name)

    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        discount = request.POST.get('discount')

        print("Selected IDs:", product_ids)
        print("Discount:", discount)

        if discount and product_ids:
            discount = Decimal(discount)

            for pid in product_ids:
                try:
                    product = Product.objects.get(id=pid)
                    original_price = product.rental_price
                    product.rental_price = original_price - (original_price * discount / Decimal('100'))
                    product.discount = discount  # Optional, only if you have a discount field
                    product.save()
                except Product.DoesNotExist:
                    print(f"Product with ID {pid} does not exist.")

    return render(request, 'brand_view.html', {
        'brand_name': brand_name,
        'products': products
    })


def category(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')
    
    seller = get_object_or_404(SellerData, seller_id=seller_id)
    
    # Get all products uploaded by this seller
    products = Product.objects.filter(seller=seller)
    
    # Extract unique category objects from products
    category_ids = products.values_list('category', flat=True).distinct()
    print(category_ids)
    unique_categories = Category.objects.filter(id__in=category_ids)
    print(unique_categories)
    return render(request, 'category.html', {'categories': unique_categories})


from decimal import Decimal

def category_view(request, category_name):
    # Get the Category object based on category_name (sub_category)
    category = get_object_or_404(Category, sub_category=category_name)

    # Get all products under this category
    products = Product.objects.filter(category=category)

    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        discount = request.POST.get('discount')

        print("Selected IDs:", product_ids)
        print("Discount:", discount)

        if discount and product_ids:
            discount = Decimal(discount)

            for pid in product_ids:
                try:
                    product = Product.objects.get(id=pid)
                    original_price = product.rental_price
                    product.rental_price = original_price - (original_price * discount / Decimal('100'))
                    product.discount = discount  # Save discount percentage
                    product.save()
                except Product.DoesNotExist:
                    print(f"Product with ID {pid} does not exist.")

    return render(request, 'category_view.html', {
        'category_name': f"{category.main_category} - {category.sub_category}",
        'products': products
    })