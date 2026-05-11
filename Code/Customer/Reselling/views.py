from django.shortcuts import render , get_object_or_404 

from django.db.models import Q

from Seller.ProductS.models import rCategory, Resell_Product , rSizeQuantity
from Customer.Account.models import Review_Rating

from django.db.models import Q
from django.shortcuts import render

######################################################################################
######################################################################################

def resell(request) :
    return render(request , 'resell.html')

######################################################################################

def rmen(request) :
    category = rCategory.objects.filter(rmain_category="Men").first()
    men_resell_products = Resell_Product.objects.all()
    return render(request , 'rmen.html' , {'men_resell_products': men_resell_products})

######################################################################################

def rwomen(request) :
    category = rCategory.objects.filter(rmain_category="Women").first()
    women_resell_products = Resell_Product.objects.filter(rcategory=category) 
    return render(request , 'rwomen.html' , {'women_resell_products': women_resell_products})

######################################################################################

def men_product_filter(request):
    products = Resell_Product.objects.all()

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
            category_query |= Q(rcategory__rmain_category__icontains=cat)
        query &= category_query
     
    if price_range and 'all' not in price_range:
        if '0-2000' in price_range:
            price_query |= Q(rprice__gte=0.00, rprice__lte=2000.00)
        if '2000-5000' in price_range:
            price_query |= Q(rprice__gte=2000.00, rprice__lte=5000.00)
        if '5000-11000' in price_range:
            price_query |= Q(rprice__gte=5000.00, rprice__lte=11000.00)
        if '11000+' in price_range:
            price_query |= Q(rprice__gte=11000.00)
        query &= price_query
        
    if brand and 'all' not in brand:
        brand_query = Q()
        for b in brand:
            brand_query |= Q(rbrand__icontains=b)
        query &= brand_query
       
    if color and 'all' not in color:
        color_query = Q()
        for c in color:
            color_query |= Q(rcolor__icontains=c)
        query &= color_query
      
    filtered_products = products.filter(query)
   
    if size and 'all' not in size:
        size_product_ids = rSizeQuantity.objects.filter(rsize__in=size).values_list('Resell_Product_id', flat=True)
        size_product_ids = list(set(size_product_ids))  # remove duplicates if any
        filtered_products = filtered_products.filter(rid__in=size_product_ids)

    if sort_by == 'price_low_to_high':
        filtered_products = filtered_products.order_by('rprice')
    elif sort_by == 'price_high_to_low':
        filtered_products = filtered_products.order_by('-rprice')
    else:
        filtered_products = filtered_products.order_by('-created_at')

    return render(request, 'rmen.html', {
        'men_resell_products': filtered_products
    })


######################################################################################

def men_product_list(request):

    category = rCategory.objects.filter(rmain_category="Men").first()
    products = Resell_Product.objects.filter(rcategory=category)
   

    sort_by = request.GET.get('sort', 'new_arrivals')  
    if sort_by == 'price_low_to_high':
        products = products.order_by('rprice')  
    elif sort_by == 'price_high_to_low':
        products = products.order_by('-rprice') 
    else:
        products = products

    return render(request, 'rmen.html', {'men_resell_products': products})

######################################################################################

def women_product_filter(request):

    category = rCategory.objects.filter(rmain_category="Women").first()
    products = Resell_Product.objects.filter(rcategory=category)

    price_range = request.GET.getlist('p1')
    brand = request.GET.getlist('brand')
    color = request.GET.getlist('color')
    size = request.GET.getlist('size')

    query = Q()

    price_query = Q()
    if 'all' not in price_range:  
        if '0-2000' in price_range:
            price_query |= Q(rprice__gte=0.00, rprice__lte=2000.00)
        
        if '2000-5000' in price_range:
            price_query |= Q(rprice__gte=2000.00, rprice__lte=5000.00)
        
        if '5000-11000' in price_range:
            price_query |= Q(rprice__gte=5000.00, rprice__lte=11000.00)
        
        if '11000+' in price_range:
            price_query |= Q(rprice__gte=11000.00)
    
    query &= price_query  

    if brand and 'all' not in brand:  
        for b in brand:
            query &= Q(rbrand__icontains=b)

    if size and 'all' not in size:
        size_query = Q()
        for s in size:
            size_query |= Q(rsize__icontains=s)  
        query &= size_query  

    if color:
        color_query = Q()
        for c in color:
            color_query |= Q(rcolor__icontains=c)
        query &= color_query  

    filter_prod = products.filter(query)

    
    return render(request, 'rwomen.html', {'women_resell_products': filter_prod})

######################################################################################

def women_product_list(request):

    category = rCategory.objects.filter(rmain_category="Women").first()
    products = Resell_Product.objects.filter(rcategory=category)
    sort_by = request.GET.get('sort', 'new_arrivals')  
   
    if sort_by == 'price_low_to_high':
        products = products.order_by('rprice')  
    elif sort_by == 'price_high_to_low':
        products = products.order_by('-rprice')  
    else:
        products = products

    return render(request, 'rwomen.html', {'women_resell_products': products})

######################################################################################

def Rprod_desc(request, Resell_Product_rid):
    product = get_object_or_404(Resell_Product, rid=Resell_Product_rid)


    reviews = Review_Rating.objects.filter(resell_product=product)

    size_quantities = rSizeQuantity.objects.filter(Resell_Product=product)
    size_quantity_dict = {sq.rsize: sq.rquantity for sq in size_quantities}

    # Default to first available size and quantity
    first_size, first_quantity = next(iter(size_quantity_dict.items()), ("N/A", 0))

    return render(request, 'Rprod_desc.html', {
           'product': product,
            'size_quantity_dict': size_quantity_dict,
            'first_size': first_size,
            'first_quantity': first_quantity,
             'reviews': reviews})

######################################################################################

def Reselling(request) : 
    RProducts = Resell_Product.objects.all()
    return render(request , 'Reselling.html' , {'RProducts' : RProducts})

######################################################################################

def RProductList(request) : 
    products = Resell_Product.objects.all()
    sort_by = request.GET.get('sort', 'new_arrivals') 
    if sort_by == 'price_low_to_high':
        products = products.order_by('rprice')  
    elif sort_by == 'price_high_to_low':
        products = products.order_by('-rprice')  
    else:
        products = products

    return render(request, 'Reselling.html', {'RProducts': products})

######################################################################################

def RProductFilter(request):
    products = Resell_Product.objects.all()

    price_range = request.GET.getlist('p1')
    brand = request.GET.getlist('brand')
    color = request.GET.getlist('color')
    size = request.GET.getlist('size')

    query = Q()

    price_query = Q()
    if 'all' not in price_range:  
        if '0-2000' in price_range:
            price_query |= Q(rprice__gte=0.00, rprice__lte=2000.00)
        
        if '2000-5000' in price_range:
            price_query |= Q(rprice__gte=2000.00, rprice__lte=5000.00)
        
        if '5000-11000' in price_range:
            price_query |= Q(rprice__gte=5000.00, rprice__lte=11000.00)
        
        if '11000+' in price_range:
            price_query |= Q(rprice__gte=11000.00)
    
    query &= price_query  

    if brand and 'all' not in brand:  
        for b in brand:
            query &= Q(rbrand__icontains=b)

    if size and 'all' not in size:
        size_query = Q()
        for s in size:
            size_query |= Q(rsize__icontains=s)  
        query &= size_query  

    if color:
        color_query = Q()
        for c in color:
            color_query |= Q(rcolor__icontains=c)
        query &= color_query  

    filter_prod = products.filter(query)

    return render(request, 'Reselling.html', {'RProducts': filter_prod})

######################################################################################