from django.shortcuts import render , HttpResponse , redirect

from Customer.SellWithUs.models import CustomerSellerReq
from Customer.Account.models import Register
from .models import CustomerSellerProduct , Customersell_SizeQuantity

######################################################################################
######################################################################################

def sellwithus(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    register = Register.objects.get(customer_id=user_id)
    email = register.email

    if request.method == 'POST':
        csname = request.POST.get('name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        addr = request.POST.get('addr')
        pincode = request.POST.get('pincode')
        name = request.POST.get('pname')
        brand = request.POST.get('brand')
        description = request.POST.get('description')
        price = request.POST.get('price')
        color = request.POST.get('color')
        category = request.POST.get('category').title()
        image_front = request.FILES.get('image_front')
        image_back = request.FILES.get('image_back')
        image_side = request.FILES.get('image_side')
        boutique = request.POST.get('boutique')

        CustomerSellerRequest = CustomerSellerReq.objects.create(
            csname=csname,
            email=email,
            number=number,
            addr=addr,
            pincode=pincode,
            boutique=boutique,
            name=name,
            brand=brand,
            description=description,
            price=price,
            color=color,
            category=category,
            image_front=image_front,
            image_back=image_back,
            image_side=image_side,
            status="Pending"
        )

        sizes = request.POST.getlist('size[]')
        quantities = request.POST.getlist('quantity[]')

        for size, quantity in zip(sizes, quantities):
            if size and quantity:
                custom = Customersell_SizeQuantity.objects.create(
                    product=CustomerSellerRequest,
                    size=size,
                    quantity=int(quantity)
                )
    return render(request, 'sellwithus.html' , {'email':email})

######################################################################################
######################################################################################