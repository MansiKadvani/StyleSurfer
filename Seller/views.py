from django.shortcuts import render, redirect 
from .models import SellerData
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.utils.timezone import now
import datetime
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from .forms import sellerForm
from Seller.ProductS.models import Product,Resell_Product
from Customer.Order.models import OrderItem

########################################################################################################################
########################################################################################################################

def Sset_password(request):

    if request.method == 'GET':
        email = request.GET.get('email')
        return render(request, 'Sset_password.html', {'email': email})
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            seller = SellerData.objects.get(semail=email)
            print(seller)
            seller.spassword = password  
            print(seller.spassword)
            seller.is_active = True  
            seller.save()
        except SellerData.DoesNotExist:
            return redirect('/Sset_password/?error=Invalid email') 
        
    return render(request, 'Sset_password.html') 


########################################################################################################################

def seller_login(request):

    if request.method == 'POST':
        email = request.POST.get('your_email')  
        password = request.POST.get('your_pass')
        
        suser = SellerData.objects.filter(semail=email).first()

        if not suser:
            return redirect('/seller_login/?error=Invalid email or password.')

        if not suser.is_active:
            return redirect('/seller_login/?error=Account not active! Please contact admin.')

        if not suser.check_password(password):  
            return redirect('/seller_login/?error=Password is incorrect.')

        request.session['seller_id'] = suser.seller_id  
        request.session['seller_name'] = suser.sname

        request.session.set_expiry(0)  # Session expires on browser close

    return render(request, 'seller_login.html')


########################################################################################################################

tokens = {}

def Sforgot_password(request):

    if request.method == 'POST':
        email = request.POST.get('email')
        users = SellerData.objects.filter(semail=email)
        user = users.first()
        username = user.sname

        if not users.exists():
            return redirect('/Sforgot_password/?error=Username does not exist.')

        token = get_random_string(length=32)
        tokens[email] = {'token': token, 'expires_at': now() + datetime.timedelta(minutes=30)}

        reset_link = request.build_absolute_uri(reverse('Sreset_password', args=[token]))

        try:
            
            html_message = render_to_string('emails/Sforgot_psw_email.html', {
            'forgot': reset_link,
            'username': username,
            'email': email,
        })

            subject = 'Reset Password'
            from_email = 'stylesurfer3@gmail.com'
            to_email = [email]

            email_message = EmailMultiAlternatives(subject, '', from_email, to_email)
            email_message.attach_alternative(html_message, "text/html")
            email_message.send()

        
        except Exception as e:
           
           return redirect('/Sforgot_password/?error=error in sending email.')

    return render(request, 'Sforgot_password.html')


#######################################################################################################################

def Sreset_password(request, token):

    email = None
    for key, value in tokens.items():
        if value['token'] == token and value['expires_at'] > now():
            email = key
            break

    if not email:
        return redirect('/Sreset_password/?error=Invalid or expired token.')

    if request.method == 'POST':
        password = request.POST.get('password')

        user = SellerData.objects.filter(semail=email).first()
        if user:
            user.spassword = password
            user.save()
            del tokens[email]  

    return render(request, 'Sreset_password.html', {'token': token})

########################################################################################################################


def Slogout(request):
    request.session.flush()
    return redirect('seller_login')

#########################################################################################################################

def dashboard(request):
    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')
    
    seller = SellerData.objects.get(seller_id=seller_id)
    
    product_queryset = Product.objects.filter(seller=seller)  # Keep QuerySet
    products = product_queryset.count()  # Get total product count
    resell_products = Resell_Product.objects.filter(rseller=seller).count()

    product_names = [item.name for item in product_queryset]  # Now it's iterable

    if products == 0:
        order_items = []# Empty list triggers "No orders found" in template
    else:
        # Filter OrderItem based on product names
        order_items = OrderItem.objects.filter(name__in=product_names).count()
       
    return render(request, 'Sdashboard.html', {
        'products': products, 
        'resell_products': resell_products, 
        'order_items': order_items
    })


#########################################################################################################################

def base_seller(request):
    return render(request, 'base_seller.html')


##########################################################################################################################

def Sprofile(request):

    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')
    else: 
        Suser = SellerData.objects.get(seller_id=seller_id)
        if request.method == 'POST':
            Sform = sellerForm(request.POST, request.FILES, instance=Suser)
            if Sform.is_valid():
                Sform.save()
                return redirect('Sprofile')


        else:
            Sform = sellerForm(instance=Suser)

    return render(request, 'Sprofile.html' , {'Sform': Sform, 'Suser': Suser})


#########################################################################################################################

def Saccount(request):
    return render(request, 'Saccount.html')

#########################################################################################################################

def Spasword(request):

    seller_id = request.session.get('seller_id')
    if not seller_id:
        return redirect('seller_login')
    else : 
        Suser = SellerData.objects.get(seller_id=seller_id)
        seller_psw = Suser.spassword
        if request.method == 'POST':
            new_psw = request.POST.get('npsw')
            Suser.spassword = new_psw
            Suser.save()            

    return render(request, 'Spasword.html' , {'oldPSW':seller_psw})


#########################################################################################################################
########################################################################################################################