from django.shortcuts import render, HttpResponse
from .models import *
from Users.models import Users
import datetime
from django.http import HttpResponse
from django.shortcuts import redirect
import requests
import json
from .models import MlmProducts
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
from .Api_view import orderb, categoryN
from datetime import date


# MERCHANT = f'cce85bdd-9845-4e11-b313-d933eda3a975'
MERCHANT = f'92fbb122-2393-4b29-937c-06af7b8c7659'
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
#amount = 11000  # Rial / Required
description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
email = f'5555'  # Optional
# mobile = f'miras@gmail.com'  # Optional
mobile = f'm@gmail.com'  # Optional
# Important: need to edit for realy server.
CallbackURL = f'http://127.0.1:8000/mlm/payment/verify/' #ALLOWED_HOSTS[0]




def send_request(request):
    if request.user.is_authenticated:
        orders = [orders.price for orders in MlmProductsOrders.objects.filter(shopper_id=request.user.id,payment_status=False).all()]
        global amount
        amount = f'{sum(orders)}0'
        req_data = {
            "merchant_id": MERCHANT,
            "amount": amount,
            "callback_url": CallbackURL,
            "description": description,
            "metadata": {"mobile": mobile, "email": email}
        }
        req_header = {"accept": "application/json","content-type": "application/json'"}
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



def verify(request):
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

                first_order = 0
                order = MlmProductsOrders.objects.filter(shopper_id=request.user.id, payment_status=False).all()
                for i in order:
                    price = i.product.price
                    score = i.product.score
                    count = i.count
                    first_order += ((price * score) * count)

                order_history = MlmProductsOrders.objects.filter(shopper_id=request.user.id, payment_status=True).first()

                if order_history is None:
                    User = UserOwner.objects.filter(MlmUser_id=request.user.id).first()

                    if User is not None:
                        ownerId = User.MlmOwner.id
                        order_owner = orderb(ownerId)
                        cat = Category.objects.filter(Id_id=ownerId).first()

                        if cat is not None:
                            pass

                        else:
                            categoryN(ownerId)

                        cat = Category.objects.filter(Id_id=ownerId).first()

                        if cat.OwnerCategory == 'nothing' or cat.OwnerCategory == 'starter':


                            if first_order >= 1000 and order_owner != 0:

                                owner_pur = first_order * 0.07
                                user = Users.objects.filter(id=ownerId).first()
                                user.commission += round(owner_pur)
                                user.walletـbalance += round(owner_pur)
                                user.save()
                                Pursant.objects.create(user_id=ownerId, amount=round(owner_pur), reson='identify pursant')



                products = MlmProductsOrders.objects.filter(shopper_id=request.user.id, payment_status=False).all()
                for p in products:
                    p.payment_status = True
                    p.save()
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



def products_page(request):
    products = MlmProducts.objects.filter(status=True).all()
    context = {
        'products': products,
    }
    return render(request, 'Mlm/products_page/products_page.html', context)



def products_detail_page(request,id,slug):
    product = get_object_or_404(MlmProducts, id=id, slug=slug)
    similars = MlmProducts.objects.filter(maincategories__id__in=[p.id for p in product.maincategories.all()])[:3]
    user_token = Token.objects.filter(user_id=request.user.id).first()
    context = {
        'product': product,
        'similars': similars,
        'user_token': user_token,
    }
    return render(request, 'Mlm/products_detail_page/products_detail_page.html', context)




def carts_page(request):
    if request.user.is_authenticated:
        user = Users.objects.filter(id=request.user.id).first()
        user_token = Token.objects.filter(user_id=user.id).first()
        if user.role == 'mlm':
            context = {
                'user_token': user_token,
            }
            return render(request, 'Mlm/carts/shoping-bag.html', context)
        else:
            return redirect('/')
    else:
        return redirect('/')





