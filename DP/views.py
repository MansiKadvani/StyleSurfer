from django.shortcuts import render, redirect , HttpResponse
from django.contrib.auth.hashers import check_password
from .models import DPData
from django.contrib import messages
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.timezone import now
import datetime
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from .forms import DPForm
from DP.OrderD.models import DPOrder

######################################################################################
######################################################################################

def Dset_password(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        return render(request, 'Dset_password.html', {'email': email})
    
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            DP = DPData.objects.get(Demail=email)
            DP.Dpassword = password  
            DP.is_active = True  
            DP.save()
        except DPData.DoesNotExist:
            return redirect('/Dset_password/?error=Invalid email') 
        
    return render(request, 'Dset_password.html') 

######################################################################################

def DP_login(request):
    if request.method == 'POST':
        email = request.POST['your_email']
        password = request.POST['your_pass']
        
        duser = DPData.objects.filter(Demail=email).first()

        if not duser:
            return redirect('/DP_login/?error=Invalid email or password.')
        
        if not duser.is_active:
            return redirect('/DP_login/?error=Account not active! Please contact admin.')
        
        if not duser.check_password(password):  # Assuming you have a custom password check
            return redirect('/DP_login/?error=Password is incorrect.')

        request.session['DP_id'] = duser.DP_id  # Use the object, not the class
        request.session['DP_name'] = duser.Dname

        # Set session expiry
        request.session.set_expiry(0)  # Session expires on browser close
    
    return render(request, 'DP_login.html')

######################################################################################

tokens = {}

def Dforgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        users = DPData.objects.filter(Demail=email)
        user = users.first()
        username = user.Dname

        if not users.exists():
            return redirect('/Dforgot_password/?error=Username does not exist.')

        token = get_random_string(length=32)
        tokens[email] = {'token': token, 'expires_at': now() + datetime.timedelta(minutes=30)}

        reset_link = request.build_absolute_uri(reverse('Dreset_password', args=[token]))

        try:
            html_message = render_to_string('emails/Dforgot_psw_email.html', {
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
            
            messages.success(request, "Password reset link has been sent to your email.")
        except Exception as e:
           return redirect('/Dforgot_password/?error=error in sending email.')

        return redirect('DP_login')

    return render(request, 'Dforgot_password.html')

######################################################################################

def Dreset_password(request, token):

    email = None
    for key, value in tokens.items():
        if value['token'] == token and value['expires_at'] > now():
            email = key
            break

    if not email:
        return redirect('/Dreset_password/?error=Invalid or expired token.')

    if request.method == 'POST':
        password = request.POST.get('password')

        
        user = DPData.objects.filter(Demail=email).first()
        if user:
            user.Dpassword = password
            user.save()
            messages.success(request, "Password reset successfully.")
            del tokens[email]  

    return render(request, 'Dreset_password.html', {'token': token})

######################################################################################

def Dlogout(request):
    request.session.flush()
    return redirect('DP_login')

######################################################################################

# def Ddashboard(request):
#     dp_id = request.session.get('DP_id')
#     if not dp_id:
#         return redirect('DP_login')
#
#     dp_instance = DPData.objects.get(DP_id=dp_id)
#
#     dp_orders = DPOrder.objects.filter(dp=dp_instance)
#
#
#     return render(request, 'Ddashboard.html', {'order_details': dp_orders})

from Customer.Order.models import OrderItem

def Ddashboard(request):
    dp_id = request.session.get('DP_id')
    if not dp_id:
        return redirect('DP_login')

    dp_instance = DPData.objects.get(DP_id=dp_id)
    dp_orders = DPOrder.objects.filter(dp=dp_instance)

    # Get all OrderItems related to this DP's orders
    order_items = OrderItem.objects.filter(order__in=[o.order for o in dp_orders])

    total_delivered = order_items.filter(product_order_status='delivered').count()
    total_returned = order_items.filter(product_order_status='Returned').count()

    context = {
        'order_details': dp_orders,
        'total_delivered': total_delivered,
        'total_returned': total_returned
    }

    return render(request, 'Ddashboard.html', context)


######################################################################################

def base_dp(request):
    return render(request, 'base_dp.html') 

######################################################################################

def Dprofile(request):

    DP_id = request.session.get('DP_id')
    if not DP_id:
        return redirect('DP_login')
    else: 
        Duser = DPData.objects.get(DP_id=DP_id)
        if request.method == 'POST':
            Dform = DPForm(request.POST, request.FILES, instance=Duser)
            if Dform.is_valid():
                Dform.save()
                return redirect('Dprofile')
            else:
                print("Form errors:", Dform.errors)
        else:
            Dform = DPForm(instance=Duser)

    return render(request, 'Dprofile.html' , {'Dform': Dform, 'Duser': Duser})

######################################################################################

def Daccount(request):
    return render(request, 'Daccount.html')

######################################################################################

def Dpasword(request):

    DP_id = request.session.get('DP_id')
    if not DP_id:
        return redirect('DP_login')
    else : 
        Duser = DPData.objects.get(DP_id=DP_id)
        DP_psw = Duser.Dpassword
        if request.method == 'POST':
            new_psw = request.POST.get('npsw')
            Duser.Dpassword = new_psw
            Duser.save()            

    return render(request, 'Dpasword.html' , {'oldPSW':DP_psw})


######################################################################################
######################################################################################
