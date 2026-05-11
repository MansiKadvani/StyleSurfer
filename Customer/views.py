import json

from django.shortcuts import render
from django.db.models import Q

from .models import FAQ 
from Customer.SpinToWin.models import SpinReward 
from Seller.ProductS.models import Product
from Customer.SellWithUs.models import CustomerSellerProduct
from Customer.Account.models import Review_Rating
from Seller.ProductS.models import Category , Product
from Customer.Cart.models import CartItem , Cart

from itertools import chain

from Seller.ProductS.models import Resell_Product, rSizeQuantity , SizeQuantity
from Customer.SellWithUs.models import Customerproduct_SizeQuantity

from django.db.models import Q
from itertools import chain
from django.shortcuts import render

from django.shortcuts import render
from django.db.models import Q
from itertools import chain
import re

######################################################################################
######################################################################################

def base(request):
    user_id = request.session.get('user_id')
    total_items = 0
    if user_id:
        try:
            cart = Cart.objects.get(user=user_id)
            cart_items = CartItem.objects.filter(cart=cart)

            total_items = sum(item.quantity for item in cart_items)
        except Cart.DoesNotExist:
            total_items = 0
    return render(request, 'base.html',{'total_items': total_items})

######################################################################################

def home(request):
    faq = FAQ.objects.all()
    rewards = SpinReward.objects.all().values('label', 'value', 'question')
    rewards_json = json.dumps(list(rewards))  
    products = Product.objects.all().order_by('-created_at')[:10]  # Latest 10 products

    return render(request, 'home.html' , {'faq' : faq  , 'rewards_json': rewards_json , 'products': products})

######################################################################################

def women(request):
    return render(request , 'women.html')

######################################################################################

def men(request):
    return render(request,'men.html')

######################################################################################

def bridal(request):
    products = Product.objects.filter(
        category__main_category='Bride' 
    ).order_by('?')[:10]

    reviews = Review_Rating.objects.filter(
        product__category__main_category__in=['Women', 'Bride']  
    ).distinct()[:10] 
    return render(request,'bridal.html',{'products': products , 'reviews' : reviews})

######################################################################################

def groom(request):   
    products = Product.objects.filter(
        category__main_category='Groom'  
    ).order_by('?')[:10]

    reviews = Review_Rating.objects.filter(
        product__category__main_category__in=['Men', 'Groom'] 
    ).distinct()[:10]  
    return render(request,'groom.html',{'products': products , 'reviews' : reviews})

######################################################################################

def privacy_policy(request) : 
    return render(request,'privacy_policy.html')

######################################################################################

def terms_condition(request) :
    return render(request,'terms_condition.html')

######################################################################################

def order(request):
    return render(request, 'orderc.html')

######################################################################################

def base1(request):
    products = Product.objects.filter(
        category__main_category='Bride'  
    ).order_by('?')[:10]

    reviews = Review_Rating.objects.filter(
        product__category__main_category__in=['Women', 'Bride']  
    ).distinct()[:10]
    return render(request, 'base1.html',{'products': products , 'reviews' : reviews})

######################################################################################

def brand_products(request, brand_name):
    products = Product.objects.filter(
        Q(brand__iexact=brand_name) 
    )
    return render(request, 'search.html', {'products': products, 'brand_name': brand_name})

def ocassion(request, ocassion_name):
    bride_sub = f'Bride{ocassion_name}'
    groom_sub = f'Groom{ocassion_name}'
    bride_products = Product.objects.filter(
        category__sub_category__iexact=bride_sub
    )

    groom_products = Product.objects.filter(
        category__sub_category__iexact=groom_sub
    )
    products = bride_products | groom_products
    return render(request, 'search.html', {'products': products, 'occasion_name': ocassion_name})


def cart_item_count(request):
    user_id = request.session.get('user_id')
    total_items = 0
    if user_id:
        try:
            cart = Cart.objects.get(user=user_id)
            cart_items = CartItem.objects.filter(cart=cart)

            total_items = sum(item.quantity for item in cart_items)
        except Cart.DoesNotExist:
            total_items = 0
    return {'cart_count': total_items}


######################################################################################

def search(request):
    query_text = request.GET.get('q', '').strip().lower()
    price_range = request.GET.getlist('p1')
    brand = request.GET.getlist('brand')
    color = request.GET.getlist('color')
    size = request.GET.getlist('size')
    category = request.GET.getlist('cat1')
    sort_by = request.GET.get('sort', 'new_arrivals')

    product_query = Q()
    resell_query = Q()
    customer_query = Q()

 
    if query_text:
        keyword_q = Q()

        keyword_q |= Q(name__icontains=query_text) | Q(category__main_category__icontains=query_text) | Q(category__sub_category__icontains=query_text) | Q(brand__icontains=query_text)
        product_query |= keyword_q

        keyword_q_resell = Q(rname__icontains=query_text) | Q(rcategory__rsub_category__icontains=query_text) | Q(rbrand__icontains=query_text)
        resell_query |= keyword_q_resell

        keyword_q_customer = Q(csname__icontains=query_text) | Q(category__icontains=query_text) | Q(brand__icontains=query_text)
        customer_query |= keyword_q_customer

        if query_text.isdigit():
            value = int(query_text)
            product_query |= Q(price__lte=value)
            resell_query |= Q(rprice__lte=value)
            customer_query |= Q(price__lte=value)

        if 'discount' in query_text or 'off' in query_text:
            discount_percent = re.findall(r'(\d+)%', query_text)
            if discount_percent:
                percent = int(discount_percent[0])
                resell_query |= Q(rdiscount_percentage=percent)
            else:
                resell_query |= Q(rdiscount_percentage__gt=0)

    if category and 'all' not in category:
        category_q = Q()
        for cat in category:
            category_q |= Q(category__sub_category__icontains=cat) | Q(rcategory__rsub_category__icontains=cat) | Q(category__icontains=cat)
        product_query &= category_q
        resell_query &= category_q
        customer_query &= category_q

    if price_range and 'all' not in price_range:
        price_q = Q()
        for pr in price_range:
            if pr == '0-2000':
                price_q |= Q(price__lte=2000) | Q(rprice__lte=2000)
            elif pr == '2000-5000':
                price_q |= Q(price__gte=2000, price__lte=5000) | Q(rprice__gte=2000, rprice__lte=5000)
            elif pr == '5000-11000':
                price_q |= Q(price__gte=5000, price__lte=11000) | Q(rprice__gte=5000, rprice__lte=11000)
            elif pr == '11000+':
                price_q |= Q(price__gte=11000) | Q(rprice__gte=11000)
        product_query &= price_q
        resell_query &= price_q
        customer_query &= price_q

    if brand and 'all' not in brand:
        brand_q = Q()
        for b in brand:
            brand_q |= Q(brand__icontains=b) | Q(rbrand__icontains=b)
        product_query &= brand_q
        resell_query &= brand_q
        customer_query &= brand_q

    if color and 'all' not in color:
        color_q = Q()
        for c in color:
            color_q |= Q(color__icontains=c) | Q(rcolor__icontains=c)
        product_query &= color_q
        resell_query &= color_q
        customer_query &= color_q

    own_products = Product.objects.filter(product_query)
    resell_products = Resell_Product.objects.filter(resell_query)
    customer_products = CustomerSellerProduct.objects.filter(customer_query, status='active')

    if size and 'all' not in size:
        own_ids = SizeQuantity.objects.filter(size__in=size).values_list('product_id', flat=True)
        resell_ids = rSizeQuantity.objects.filter(rsize__in=size).values_list('Resell_Product_id', flat=True)
        customer_ids = Customerproduct_SizeQuantity.objects.filter(size__in=size).values_list('product_id', flat=True)

        own_products = own_products.filter(id__in=own_ids)
        resell_products = resell_products.filter(rid__in=resell_ids)
        customer_products = customer_products.filter(id__in=customer_ids)

    if sort_by == 'price_low_to_high':
        own_products = own_products.order_by('price')
        resell_products = resell_products.order_by('rprice')
        customer_products = customer_products.order_by('price')
    elif sort_by == 'price_high_to_low':
        own_products = own_products.order_by('-price')
        resell_products = resell_products.order_by('-rprice')
        customer_products = customer_products.order_by('-price')
    else:
        own_products = own_products.order_by('-created_at')
        resell_products = resell_products.order_by('-created_at')
        customer_products = customer_products.order_by('-created_at')

    combined_products = list(chain(own_products, resell_products, customer_products))

    return render(request, 'search.html', {
        'products': combined_products
    })

######################################################################################
######################################################################################
