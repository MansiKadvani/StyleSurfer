from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, get_object_or_404 ,  render
from django.contrib import messages
from django.utils.timezone import now

from datetime import datetime, timedelta


from Customer.SpinToWin.models import RedeemedVoucher
from Seller.ProductS.models import Product , Resell_Product , SizeQuantity , rSizeQuantity

from .models import Cart, CartItem, Register, Product, CustomerSellerProduct, Resell_Product, Customedesign, SizeQuantity

from decimal import Decimal
from datetime import datetime, timedelta, date
from django.shortcuts import get_object_or_404, redirect
from .models import Cart, CartItem
from Customer.SellWithUs.models import CustomerSellerProduct , Customerproduct_SizeQuantity

######################################################################################
######################################################################################

def cart_detail(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login')

    user = get_object_or_404(Register, customer_id=user_id)
    cart = Cart.objects.filter(user=user).first()

    if not cart or not cart.items.exists():
        return render(request, 'cart.html', {
            'cart_items': [],
            'item_count': 0,
            'total_price': 0,
            'total_security': 0,
            'Grand_total': 0,
            'discount': 0,
            'message': "Your cart is empty.",
        })

    cart_items = cart.items.all()

    for item in cart_items:
        if item.return_date and item.return_date < now().date():
            try:
                product = Product.objects.get(name=item.name)  
                product.quantity += item.quantity  
                product.save()
                item.delete()  
            except Product.DoesNotExist:
                pass  

    discount = Decimal(request.session.get('discount', 0))
    grand_total = cart.get_grand_total() - discount

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'item_count': cart.get_item_count(),
        'total_price': cart.get_total_price(),
        'total_security': cart.get_total_security(),
        'discount': discount,
        'Grand_total': grand_total, 
    })

######################################################################################




def add_to_cart(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    user = get_object_or_404(Register, customer_id=user_id)
    cart, _ = Cart.objects.get_or_create(user=user)

    product_id = request.POST.get('product_id')
    rid = request.POST.get('rid')
    buyback_id = request.POST.get('buyback_id')
    name = request.POST.get('name')
    brand = request.POST.get('brand')
    base_price = request.POST.get('price')
    image = request.POST.get('image')
    size = request.POST.get('selectsize', '').strip()
    color = request.POST.get('color')
    prod_type = request.POST.get('ptype')
    days = request.POST.get('days', 1)
    stock = request.POST.get('stock')

    delivery_date_raw = request.POST.get('delivery_date')
    rental_dates_raw = request.POST.get('rental_dates')
    return_date_raw = request.POST.get('return_date')

    delivery_date = delivery_date_raw.split(',')[0].strip() if delivery_date_raw else None
    rental_dates = [date.strip() for date in rental_dates_raw.split(',') if date.strip()] if rental_dates_raw else []
    return_date = return_date_raw.split(',')[0].strip() if return_date_raw else None

    if not size:
        return redirect(f'/Product/prod_desc/{product_id}/?error=Size not received')



    try:
        base_price = Decimal(base_price) if base_price else Decimal(0)

        if prod_type == "resell_product" or rid:
            days = 0
            delivery_date = date.today() + timedelta(days=2)
            rental_dates = []
            return_date = None
            security = 0
        else:
            days = int(days)
            delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
            rental_dates = [datetime.strptime(d, '%Y-%m-%d').date() for d in rental_dates]
            return_date = datetime.strptime(return_date, '%Y-%m-%d').date()
            security = base_price * Decimal('0.5')
    except (ValueError, TypeError):
        if prod_type == "own_product" and prod_type == "sell_with_us" : 
            return redirect(f'/Product/prod_desc/{product_id}/?error=Invalid input format.')
        elif prod_type == "Buy_back" : 
            return redirect(f'/Account/buyback_detail/{buyback_id}/?error=Invalid input format.')
        else : 
            return redirect(f'/Reselling/Rprod_desc/{rid}/?error=Invalid input format.')


    total_price = base_price
    size_entry = None

    if prod_type == "own_product":
        product = get_object_or_404(Product, id=product_id)
        size_entry = SizeQuantity.objects.filter(product=product, size=size).first()


    elif prod_type == "sell_with_us":
        product = get_object_or_404(CustomerSellerProduct, id=product_id)
        size_entry = Customerproduct_SizeQuantity.objects.filter(product=product, size=size).first()


    elif rid:
        rproduct = get_object_or_404(Resell_Product, rid=rid)
        size_entry = rSizeQuantity.objects.filter(Resell_Product=rproduct, rsize=size).first()
        if not size_entry or size_entry.rquantity <= 0:
            return redirect(f'/Reselling/Rprod_desc/{rid}/?error=Selected size out of stock')
        security = 0

    elif buyback_id:
        custom_design = get_object_or_404(Customedesign, buyback__buyback_id=str(buyback_id))
        if custom_design.size != size:
            return redirect(f'/Account/buyback_detail/{buyback_id}/?error=Selected size not available')

            # Check quantity
        if custom_design.quantity <= 0:
            return redirect(f'/Account/buyback_detail/{buyback_id}/?error=Out of stock')

        size_entry = custom_design

    if size_entry:
        if hasattr(size_entry, 'quantity') and size_entry.quantity <= 0:
            redirect_url = f'/Product/prod_desc/{product_id}/'
            return redirect(f'{redirect_url}?error=Selected size out of stock')
        if hasattr(size_entry, 'rquantity') and size_entry.rquantity <= 0:
            return redirect(f'/Reselling/Rprod_desc/{rid}/?error=Selected size out of stock')

    rental_date_str = ', '.join([d.strftime('%d %B %Y') for d in rental_dates]) if rental_dates else None

    filter_kwargs = {
        'cart': cart,
        'name': name,
        'size': size,
        'rental_date': rental_date_str,
    }
    filter_kwargs['rental_date'] = rental_date_str if rental_date_str else None

    existing_item = CartItem.objects.filter(**filter_kwargs).first()
    if existing_item:
        existing_item.quantity += 1
        existing_item.price = total_price
        existing_item.security = security
        existing_item.save()

        if size_entry:
            if hasattr(size_entry, 'quantity'):
                size_entry.quantity -= 1
            elif hasattr(size_entry, 'rquantity'):
                size_entry.rquantity -= 1
            size_entry.save()

        if prod_type == "resell_product":
            success_url = f'/Reselling/Rprod_desc/{rid}/'
        elif prod_type == "Buy_back":
            success_url = f'/Account/buyback_detail/{buyback_id}/'
        else:
            success_url = f'/Product/prod_desc/{product_id}/'

        return redirect(f'{success_url}?success=Quantity Updated')

    if size_entry:
        if hasattr(size_entry, 'quantity'):
            size_entry.quantity -= 1
        elif hasattr(size_entry, 'rquantity'):
            size_entry.rquantity -= 1
        size_entry.save()

    cart_item = CartItem.objects.create(
        cart=cart,
        product_id=product_id if product_id else None,
        rid=rid if rid else None,
        buyback_id=buyback_id if buyback_id else None,
        name=name,
        brand=brand,
        size=size,
        rental_date=rental_date_str,
        return_date=return_date,
        delivery_date=delivery_date,
        price=total_price,
        image=image,
        color=color,
        days=days,
        security=security,
        quantity=1,
        stoke=stock,
        prod_type=prod_type,
    )

    if prod_type == "resell_product":
        success_url = f'/Reselling/Rprod_desc/{rid}/'
    elif prod_type == "Buy_back":
        success_url = f'/Account/buyback_detail/{buyback_id}/'
    else:
        success_url = f'/Product/prod_desc/{product_id}/'
    return redirect(f'{success_url}?success=Added to cart')

######################################################################################

from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import CartItem, Product, CustomerSellerProduct, Resell_Product, SizeQuantity

@require_POST
def update_cart(request):
    item_id = request.POST.get('item_id')
    new_quantity = request.POST.get('quantity')

    try:
        new_quantity = int(new_quantity)
        if new_quantity < 1:
            return redirect(f'/Cart/cart_detail/?error=Selected size out of stock')
    except (ValueError, TypeError):
        return redirect(f'/Cart/cart_detail/?error=Invalid quantity format')
    try:
        cart_item = CartItem.objects.get(id=item_id)
        size = cart_item.size
        prod_type = cart_item.prod_type
        quantity_diff = new_quantity - cart_item.quantity

        size_entry = None

        if prod_type == "own_product":
            product = get_object_or_404(Product, id=cart_item.product_id)
            size_entry = SizeQuantity.objects.filter(product=product, size=size).first()

        elif prod_type == "sell_with_us":
            product = get_object_or_404(CustomerSellerProduct, id=cart_item.product_id)
            size_entry = Customerproduct_SizeQuantity.objects.filter(product=product, size=size).first()

        elif prod_type == "resell_product":
            product = get_object_or_404(Resell_Product, rid=cart_item.rid)
            size_entry = rSizeQuantity.objects.filter(Resell_Product=product, rsize=size).first()

        elif prod_type == "Buy_back":
            product = get_object_or_404(Customedesign, buyback__buyback_id=cart_item.buyback_id)
            size_entry = SizeQuantity.objects.filter(product=product, size=size).first()

        else:
            return redirect(f'/Cart/cart_detail/?error=Invalid product type')

        if quantity_diff > 0:
            if not size_entry or getattr(size_entry, 'quantity', getattr(size_entry, 'rquantity', 0)) < quantity_diff:
                return redirect(f'/Cart/cart_detail/?error=Not enough stock available')
            if hasattr(size_entry, 'quantity'):
                size_entry.quantity -= quantity_diff
            elif hasattr(size_entry, 'rquantity'):
                size_entry.rquantity -= quantity_diff

        elif quantity_diff < 0:
            if hasattr(size_entry, 'quantity'):
                size_entry.quantity += abs(quantity_diff)
            elif hasattr(size_entry, 'rquantity'):
                size_entry.rquantity += abs(quantity_diff)

        if size_entry:
            size_entry.save()

        cart_item.quantity = new_quantity
        cart_item.price = (cart_item.price / cart_item.quantity) * new_quantity if cart_item.quantity else 0
        cart_item.security = (cart_item.security / cart_item.quantity) * new_quantity if cart_item.security else 0
        cart_item.stoke = getattr(size_entry, 'quantity', getattr(size_entry, 'rquantity', 0)) if size_entry else 0
        cart_item.save()

    except CartItem.DoesNotExist:
        return redirect(f'/Cart/cart_detail/?error=Cart item not found')
    except Exception as e:
        return redirect(f'/Cart/cart_detail/?error=Error')

    return redirect(f'/Cart/cart_detail/?success=Cart updated successfully')

######################################################################################

@require_POST
def remove_from_cart(request):
    item_id = request.POST.get('item_id')

    try:
        cart_item = CartItem.objects.get(id=item_id)
        size = cart_item.size
        prod_type = cart_item.prod_type
        size_entry = None

        if prod_type == "own_product":
            product = get_object_or_404(Product, id=cart_item.product_id)
            size_entry = SizeQuantity.objects.filter(product=product, size=size).first()

        elif prod_type == "sell_with_us":
            product = get_object_or_404(CustomerSellerProduct, id=cart_item.product_id)
            size_entry = Customerproduct_SizeQuantity.objects.filter(product=product, size=size).first()

        elif prod_type == "resell_product":
            product = get_object_or_404(Resell_Product, rid=cart_item.rid)
            size_entry = rSizeQuantity.objects.filter(Resell_Product=product, rsize=size).first()

        elif prod_type == "Buy_back":
            product = get_object_or_404(Customedesign, buyback__buyback_id=cart_item.buyback_id)

            if product.size != size:
                return redirect(f'/Cart/cart_detail/?error=Size mismatch in Buy_back product')


            size_entry = product

        else:
            return redirect(f'/Cart/cart_detail/?error=Invalid product type')


        # Restore stock
        if size_entry:
            if hasattr(size_entry, 'quantity'):
                size_entry.quantity += cart_item.quantity
            elif hasattr(size_entry, 'rquantity'):
                size_entry.rquantity += cart_item.quantity
            size_entry.save()

        cart_item.delete()

    except CartItem.DoesNotExist:
        return redirect(f'/Cart/cart_detail/?error=Cart item not found')

    except Exception as e:
        return redirect(f'/Cart/cart_detail/?error=Error')

    return redirect(f'/Cart/cart_detail/?success=Item removed from cart successfully')

######################################################################################

@require_POST  
def apply_voucher(request):

    user_id = request.session.get('user_id')

    voucher_code = request.POST.get('voucher_code', '').strip()
    print(voucher_code)

    if not user_id:
        return redirect('cart_detail')  
    
    user = get_object_or_404(Register, customer_id=user_id)

    cart = Cart.objects.filter(user=user).first()

    if not cart or not cart.items.exists():
        return redirect(f'/Cart/cart_detail/?error=Your cart is empty.')

    redeemed_voucher = RedeemedVoucher.objects.filter(user=user, code=voucher_code, is_active=True).first()

    if not redeemed_voucher:
        request.session['discount'] = 0
        return redirect(f'/Cart/cart_detail/?error=Invalid or expired voucher code.')

    if redeemed_voucher.voucher.expires_at and redeemed_voucher.voucher.expires_at < now():
        request.session['discount'] = 0
        redeemed_voucher.is_active = False
        redeemed_voucher.save(update_fields=["is_active"])
        return redirect(f'/Cart/cart_detail/?error=This voucher has expired and cannot be used.')

    discount_percentage = Decimal(redeemed_voucher.voucher.discount)
    print(discount_percentage)

    grand_total = Decimal(cart.get_grand_total())
    print(grand_total)

    discount_amount = grand_total * (discount_percentage / Decimal(100))
    print(discount_amount)

    request.session['discount'] = float(round(discount_amount, 2))

    request.session['voucher_applied'] = voucher_code

    redeemed_voucher.is_active = False
    redeemed_voucher.save(update_fields=["is_active"])

    messages.success(request, f"Voucher applied! You saved ₹{discount_amount:.2f}.")

    return redirect('cart_detail')

######################################################################################

@require_POST
def checkout_cart(request):
    user_id = request.session.get('user_id')

    if not user_id:
        return redirect('login')

    user = get_object_or_404(Register, customer_id=user_id)
    cart = Cart.objects.filter(user=user).first()

    if not cart or not cart.items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect('cart_detail')

    discount = Decimal(request.session.get('discount', 0))  

    cart.save_checkout_data(discount)

    messages.success(request, "Checkout data saved. Proceed to payment.")
    return redirect('order_form')

######################################################################################