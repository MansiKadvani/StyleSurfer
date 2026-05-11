

from django.shortcuts import render, get_object_or_404, redirect , HttpResponse
from Customer.Order.models import Order , OrderItem
from Seller.ProductS.models import Product , Resell_Product
from Seller.models import SellerData

#######################################################################################################################
#######################################################################################################################


def view_order(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')

    seller = SellerData.objects.filter(seller_id=seller_id).first()
    if not seller:
        return redirect('seller_dashboard')

    # Fetch Own Products
    own_products = Product.objects.filter(seller=seller)
    own_product_names = own_products.values_list('name', flat=True)

    # Fetch Resell Products
    resell_products = Resell_Product.objects.filter(rseller=seller)
    resell_product_names = resell_products.values_list('rname', flat=True)

    # Get OrderItems for both product types
    order_items = OrderItem.objects.filter(name__in=own_product_names)
    rorder_items = OrderItem.objects.filter(name__in=resell_product_names)

    # Combine all item names related to this seller
    seller_item_names = list(own_product_names) + list(resell_product_names)

    # Get orders that include items with those names
    orders = Order.objects.filter(
        items__name__in=seller_item_names,
        payment_method__isnull=False,
        order_status__isnull=False
    ).distinct().order_by('-created_at').prefetch_related("items")

    context = {
        'own_products': own_products,
        'resell_products': resell_products,
        'order_items': order_items,
        'rorder_items': rorder_items,
        'orders': orders,
    }

    return render(request, 'view_order.html', context)


#######################################################################################################################


def order_detail(request, order_id):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')

    seller = SellerData.objects.filter(seller_id=seller_id).first()
    if not seller:
        return redirect('seller_dashboard')

    order = get_object_or_404(Order, order_id=order_id)
    all_order_items = OrderItem.objects.filter(order=order)

    # Get this seller's own and resell product names
    own_products = Product.objects.filter(seller=seller)
    own_product_names = own_products.values_list('name', flat=True)

    resell_products = Resell_Product.objects.filter(rseller=seller)
    resell_product_names = resell_products.values_list('rname', flat=True)

    # Filter only items from this seller
    own_order_items = all_order_items.filter(name__in=own_product_names)
    resell_order_items = all_order_items.filter(name__in=resell_product_names)

    context = {
        'order': order,
        'own_order_items': own_order_items,
        'resell_order_items': resell_order_items,
    }

    return render(request, 'detail_order.html', context)


#######################################################################################################################

def detail_resell(request, order_id):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')

    seller = SellerData.objects.filter(seller_id=seller_id).first()
    if not seller:
        return redirect('seller_dashboard')

    order = get_object_or_404(Order, order_id=order_id)
    all_order_items = OrderItem.objects.filter(order=order)

    # Get this seller's own and resell product names
    own_products = Product.objects.filter(seller=seller)
    own_product_names = own_products.values_list('name', flat=True)

    resell_products = Resell_Product.objects.filter(rseller=seller)
    resell_product_names = resell_products.values_list('rname', flat=True)

    # Filter only items from this seller
    own_order_items = all_order_items.filter(name__in=own_product_names)
    resell_order_items = all_order_items.filter(name__in=resell_product_names)

    context = {
        'order': order,
        'own_order_items': own_order_items,
        'resell_order_items': resell_order_items,
    }

    return render(request, 'detail_resell.html', context)

#######################################################################################################################
#######################################################################################################################

