from django.shortcuts import render , get_object_or_404 , HttpResponse , redirect

from django.db.models import Q

from itertools import chain

from Seller.ProductS.models import Category, Product , SizeQuantity
from Customer.SellWithUs.models import CustomerSellerProduct ,Customerproduct_SizeQuantity
from Customer.Account.models import Review_Rating

from itertools import chain
from django.db.models import Q
from django.shortcuts import render

######################################################################################
######################################################################################


def prod_desc(request, product_id):
    try:
        product = Product.objects.get(id=product_id)

        reviews = Review_Rating.objects.filter(product=product)
        filtered_reviews = [review for review in reviews if not profanity.contains_profanity(review.review)]

        size_quantities = SizeQuantity.objects.filter(product=product)

    except Product.DoesNotExist:
        product = get_object_or_404(CustomerSellerProduct, id=product_id)

        reviews = ""  # Optional: You can skip this line if not used elsewhere
        filtered_reviews = []  # Add this to avoid the UnboundLocalError
        size_quantities = Customerproduct_SizeQuantity.objects.filter(product=product)

    size_quantity_dict = {sq.size: sq.quantity for sq in size_quantities}
    first_size, first_quantity = next(iter(size_quantity_dict.items()), ("N/A", 0))

    return render(
        request,
        'prod_desc.html',
        {
            'product': product,
            'size_quantity_dict': size_quantity_dict,
            'first_size': first_size,
            'first_quantity': first_quantity,
            'reviews': filtered_reviews
        }
    )

######################################################################################

def product(request, category_name):
    category = Category.objects.filter(sub_category=category_name).first()

    if category:
        products = Product.objects.filter(category=category)
        active_products = CustomerSellerProduct.objects.filter(category=category, status='active')

        combined_products = list(chain(products, active_products))
    else:
        combined_products = []

    sort_by = request.GET.get('sort', 'new_arrivals')  

    if sort_by == 'price_low_to_high':
        combined_products.sort(key=lambda x: x.rental_price)  
    elif sort_by == 'price_high_to_low':
        combined_products.sort(key=lambda x: x.rental_price, reverse=True)  
    else:
        combined_products.sort(key=lambda x: x.created_at, reverse=True) 

    return render(request, 'product.html', {'products': combined_products, 'category_name': category_name})

######################################################################################


def product_filter(request, category_name):
    category = Category.objects.filter(sub_category=category_name).first()

    if not category:
        return render(request, 'product.html', {'products': [], 'category_name': category_name})

    products = Product.objects.filter(category=category)
    active_products = CustomerSellerProduct.objects.filter(category=category, status='active')

    price_range = request.GET.getlist('p1')
    brand = request.GET.getlist('brand')
    color = request.GET.getlist('color')
    size = request.GET.getlist('size')
    sort_by = request.GET.get('sort', 'new_arrivals')


    query = Q()
    price_query = Q()

    if price_range and 'all' not in price_range:
        if '0-2000' in price_range:
            price_query |= Q(rental_price__gte=0, rental_price__lte=2000)
        if '2000-5000' in price_range:
            price_query |= Q(rental_price__gte=2000, rental_price__lte=5000)
        if '5000-11000' in price_range:
            price_query |= Q(rental_price__gte=5000, rental_price__lte=11000)
        if '11000+' in price_range:
            price_query |= Q(rental_price__gte=11000)
        query &= price_query

    if brand and 'all' not in brand:
        for b in brand:
            query &= Q(brand__icontains=b)

    if color and 'all' not in color:
        color_query = Q()
        for c in color:
            color_query |= Q(color__icontains=c)
        query &= color_query

    filter_prod = products.filter(query)
    filter_active_prod = active_products.filter(query)

    combined_products = list(chain(filter_prod, filter_active_prod))

    if size and 'all' not in size:
        size_product_ids = SizeQuantity.objects.filter(size__in=size).values_list('product_id', flat=True)
        size_product_ids = list(set(size_product_ids))  

        combined_products = [prod for prod in combined_products if prod.id in size_product_ids]

    if sort_by == 'price_low_to_high':
        combined_products.sort(key=lambda x: x.rental_price or 0)
    elif sort_by == 'price_high_to_low':
        combined_products.sort(key=lambda x: x.rental_price or 0, reverse=True)
    else:
        combined_products.sort(key=lambda x: x.created_at or '', reverse=True)

    return render(request, 'product.html', {
        'products': combined_products,
        'category_name': category_name
    })

######################################################################################

def product_list(request, category_name):
    category = Category.objects.filter(sub_category=category_name).first()

    if category:
        products = Product.objects.filter(category=category)
        active_products = CustomerSellerProduct.objects.filter(category=category, status='active')

        sort_by = request.GET.get('sort', 'new_arrivals') 

        combined_products = list(chain(products, active_products))

        if sort_by == 'price_low_to_high':
            combined_products.sort(key=lambda x: x.rental_price)  
        elif sort_by == 'price_high_to_low':
            combined_products.sort(key=lambda x: x.rental_price, reverse=True)  
        else:
            combined_products.sort(key=lambda x: x.created_at, reverse=True)  

        return render(request, 'product.html', {'products': combined_products, 'category_name': category_name})
    else:
        return render(request, 'product.html', {'products': [], 'category_name': category_name})

######################################################################################