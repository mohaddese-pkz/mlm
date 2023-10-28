from Users.models import Users
from django.http import HttpResponse
from django.shortcuts import redirect
import requests
import json
from mlm.models import UserWalletRequest


MERCHANT = f'cce85bdd-9845-4e11-b313-d933eda3a975'
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
#amount = 11000  # Rial / Required
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
email = f'5555'  # Optional
mobile = f'miras@gmail.com'  # Optional
# Important: need to edit for realy server.
CallbackURL = f'/wallet/verify/' #ALLOWED_HOSTS[0]


global amount

def wallet_send_request(request,price):
    if request.user.is_authenticated:

        amount = f'{price}0'
        req_data = {
            "merchant_id": MERCHANT,
            "amount": amount,
            "callback_url": CallbackURL,
            "description": description,
            "metadata": {"mobile": mobile, "email": email}
        }
        req_header = {"accept": "application/json", "content-type": "application/json'"}
        req = requests.post(url=ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header)
        authority = req.json()['data']['authority']
        if len(req.json()['errors']) == 0:
            return redirect(ZP_API_STARTPAY.format(authority=authority))
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
    else:
        return redirect('/')



def wallet_verify(request):
    t_status = request.GET.get('Status')
    t_authority = request.GET['Authority']
    if request.GET.get('Status') == 'OK':
        req_header = {"accept": "application/json", "content-type": "application/json'"}
        req_data = {
            "merchant_id": MERCHANT,
            "amount": amount,
            "authority": t_authority
        }
        req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']
            if t_status == 100:
                user = Users.objects.filter(id=request.user.id).first()
                UserWalletRequest.objects.create(store=user.walletـbalance, requests=amount, user_id=request.user.id, type='settle')
                user.wallet_balance += amount
                user.save()
                return HttpResponse('Transaction success.\nRefID: ' + str(req.json()['data']['ref_id']))
            elif t_status == 101:
                return HttpResponse('Transaction submitted : ' + str(req.json()['data']['message']))
            else:
                return HttpResponse('Transaction failed.\nStatus: ' + str(req.json()['data']['message']))
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
    else:
        return HttpResponse('Transaction failed or canceled by user')