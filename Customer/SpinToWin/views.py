import json
import uuid

from django.shortcuts import render , redirect
from django.utils.timezone import now
from django.utils import timezone
from django.http import JsonResponse

from Customer.Account.models import Register
from .models import SpinReward , Voucher ,RedeemedVoucher , UserSpin

######################################################################################
######################################################################################

def check_spin_limit(request):
    user_id = request.session.get('user_id')
    
    if request.method == "POST" and user_id:
        current_month = now().month
        current_year = now().year
        
        try:
            user_instance = Register.objects.get(customer_id=user_id)
        except Register.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found.'})

        user_spin, created = UserSpin.objects.get_or_create(
            user=user_instance, 
            date__month=current_month, 
            date__year=current_year
        )

        if user_spin.count < 2:
            user_spin.count += 1

            data = json.loads(request.body.decode("utf-8"))
            reward_coins = data.get('reward_coins', 0)
            user_spin.reward = int(user_spin.reward) + int(reward_coins)
            user_spin.save()

            return JsonResponse({'status': 'success', 'message': 'Spin logged successfully!'})
        else:
            return JsonResponse({'status': 'error', 'message': 'No spins remaining for this month.'})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'})

######################################################################################

def spin_voucher(request) : 
    user_id = request.session.get('user_id')
    if not user_id : 
        return redirect('login')
    
    user = Register.objects.get(customer_id=user_id)
    coin = UserSpin.objects.filter(user=user).first()

    vouchers = Voucher.objects.filter(expires_at__gte=timezone.now())

    rewards = SpinReward.objects.all().values('label', 'value', 'question')
    rewards_json = json.dumps(list(rewards))  # Convert to JSON string

    return render(request , 'spin_voucher.html',{'rewards_json': rewards_json , 'coin' : coin , 'vouchers':vouchers})

######################################################################################

def redeem_voucher(request, voucher_id):
    user_id = request.session.get('user_id')
    user = Register.objects.get(customer_id=user_id)
    voucher = Voucher.objects.get(id=voucher_id)

    if voucher.is_expired():
        return redirect('/SpinToWin/spin_voucher/?error=this Voucher has been expired and it cannot be redeemed!!')

    try :
        user_coin = UserSpin.objects.get(user=user)
    except :
        return redirect('/SpinToWin/spin_voucher/?error=You have not spin the wheel for any time Please first spin the wheel!!')


    if user_coin.reward >= voucher.vprice:
        user_coin.reward -= voucher.vprice
        user_coin.save()
        unique_code = f"{user.customer_id}-{voucher.id}-{uuid.uuid4().hex[:6].upper()}"

        redeemed_voucher = RedeemedVoucher.objects.create(
            user=user,
            voucher=voucher,
            code=unique_code,
            redeemed_at=now()
        )
        redeemed_voucher.save()
        return redirect('/SpinToWin/spin_voucher/?success=Voucher Is Reddemed Successfully! You can see your vouchers in account section under the voucher section!!')
    else:
        return redirect('/SpinToWin/spin_voucher/?error=Sorry! You dont have enough coins to redeem the voucher')

######################################################################################
