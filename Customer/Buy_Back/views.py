import random
import string

from django.shortcuts import render, get_object_or_404, redirect

from .models import Buyback, Customedesign, SellerRequest
from Seller.models import SellerData
from Seller.ProductS.models import Product , Resell_Product , Category , SizeQuantity
from Customer.Account.models import Register
from decimal import Decimal
from itertools import chain
from django.db.models import Q

######################################################################################
######################################################################################

def Buydesc(request, product_id):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login')

    user = get_object_or_404(Register, customer_id=user_id)
    product = get_object_or_404(Product, id=product_id, buyback=True)

    category = get_object_or_404(Category, id=product.category.id)
    sub_category = category.sub_category

    categories = Category.objects.filter(main_category=category.main_category)

    size_quantities = SizeQuantity.objects.filter(product=product)
    size_quantity_dict = {sq.size: sq.quantity for sq in size_quantities}

    first_size, first_quantity = next(iter(size_quantity_dict.items()), ("N/A", 0))

    context = {
        'product': product,
        'size_quantity_dict': size_quantity_dict,
        'first_size': first_size,
        'first_quantity': first_quantity,
        'categories': categories,  
        'default_gender': category.main_category,  
        'sub_category': sub_category,  
    }
    return render(request, 'Buyback.html', context)

######################################################################################




def submit_custom_design(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = get_object_or_404(Register, customer_id=user_id)

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        name = request.POST.get("name") or "Unnamed Product"
        brand = request.POST.get("brand") or "Unnamed Brand"
        price = request.POST.get("price") or "0"
        color = request.POST.get("color")

        fimage = request.POST.get("fimage")
        simage = request.POST.get("simage")
        bimage = request.POST.get("bimage")
        sizes = request.POST.get("selectsize")
        uploaded_file = request.FILES.get("upload")

        gender = request.POST.get("gender")
        clothing = request.POST.get("category")
        embroidery_type = request.POST.get("embroidery_type")
        placement = request.POST.get("placement")
        thread_option = request.POST.get("thread_option")
        density = request.POST.get("density")
        addons = request.POST.get("addons")   # Might be empty string
        mirror_shape = request.POST.get("shape") or ""
        mirror_size = request.POST.get("mirror_size") or ""
        border_color = request.POST.get("border_color") or ""
        design_style = request.POST.get("design_style") or ""


        seller = SellerData.objects.filter(products__id=product_id).first()
        if not seller:
            return render(request, "Buyback.html", {"error": "Seller not found for this product."})

        buyback_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        buyback = Buyback.objects.create(user=user, buyback_id=buyback_id)

        custom_design = Customedesign.objects.create(
            buyback=buyback,
            name=name,
            brand=brand,
            fimage=fimage,
            simage=simage,
            bimage=bimage,
            price=Decimal(price),
            color=color,
            size=sizes,
            gender=gender,
            clothing=clothing,
            embroidery_style=embroidery_type,
            placement=placement,
            thread_option=thread_option,
            density=density,
            addons=addons,
            mirror_shape=mirror_shape,
            mirror_size=mirror_size,
            border_color=border_color,
            design_style=design_style,
            uploaded_file=uploaded_file,
            seller=seller,
            Customer_status="Buy Request"
        )

        SellerRequest.objects.create(
            buyback=buyback,
            seller=seller,
            product_id=product_id,
            custom_design=custom_design,
            status="Pending"
        )
        success_url = f'/Buy_Back/Buydesc/{product_id}/'
        return redirect(f'{success_url}?success=Request Submitted Successfully')
    return render(request, "Buyback.html")

######################################################################################

def buy_back_prod(request):
    buyback_products = Product.objects.filter(buyback=True)
    return render(request, 'buy_back_prod.html', {'buyback_products': buyback_products})


def buy1(request, product_id):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login')

    user = get_object_or_404(Register, customer_id=user_id)
    product = get_object_or_404(Product, id=product_id, buyback=True)

    category = get_object_or_404(Category, id=product.category.id)
    sub_category = category.sub_category

    categories = Category.objects.filter(main_category=category.main_category)

    size_quantities = SizeQuantity.objects.filter(product=product)
    size_quantity_dict = {sq.size: sq.quantity for sq in size_quantities}

    first_size, first_quantity = next(iter(size_quantity_dict.items()), ("N/A", 0))

    context = {
        'product': product,
        'size_quantity_dict': size_quantity_dict,
        'first_size': first_size,
        'first_quantity': first_quantity,
        'categories': categories,  
        'default_gender': category.main_category,  
        'sub_category': sub_category,  
    }
    return render(request, 'buy1.html', context)

####################################################################################



def buyback_products(request):
    products = Product.objects.filter(buyback=True)

    price_range = request.GET.getlist('p1')
    brand = request.GET.getlist('brand')
    color = request.GET.getlist('color')
    size = request.GET.getlist('size')
    sort_by = request.GET.get('sort', 'new_arrivals')
    Category = request.GET.getlist('cat1')


    query = Q()
    price_query = Q()

    
    if Category and 'all' not in Category:
        category_query = Q()
        for cat in Category:
            category_query |= Q(category__main_category__icontains=cat)
        query &= category_query

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
        brand_query = Q()
        for b in brand:
            brand_query |= Q(brand__icontains=b)
        query &= brand_query

    if color and 'all' not in color:
        color_query = Q()
        for c in color:
            color_query |= Q(color__icontains=c)
        query &= color_query

    filtered_products = products.filter(query)

    if size and 'all' not in size:
        size_product_ids = SizeQuantity.objects.filter(size__in=size).values_list('product_id', flat=True)
        filtered_products = filtered_products.filter(id__in=size_product_ids)


    if sort_by == 'price_low_to_high':
        filtered_products = sorted(filtered_products, key=lambda x: x.rental_price or 0)
    elif sort_by == 'price_high_to_low':
        filtered_products = sorted(filtered_products, key=lambda x: x.rental_price or 0, reverse=True)
    else:  
        filtered_products = sorted(filtered_products, key=lambda x: x.created_at or '', reverse=True)


    return render(request, 'buy_back_prod.html', {
        'buyback_products': filtered_products,
        'filter_type': 'buy_back'
    })

######################################################################################
######################################################################################