from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view
from .serializer import *
from .models import *
from Users.models import Users
from datetime import date
from rest_framework import generics, status
import functools
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import base64
import binascii
import functools
import hashlib
import importlib
import math
import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.dispatch import receiver
from django.utils.crypto import (
    RANDOM_STRING_CHARS, constant_time_compare, get_random_string, pbkdf2,
)
from django.utils.module_loading import import_string
from django.utils.translation import gettext_noop as _

UNUSABLE_PASSWORD_PREFIX = '!'  # This will never be a valid encoded hash
UNUSABLE_PASSWORD_SUFFIX_LENGTH = 40  # number of random chars to add after UNUSABLE_PASSWORD_PREFIX

@api_view()
def NationalCodeLists(request):
    userL = []
    if request.user.is_superuser:
        users = Users.objects.all()
        if users is not None:
            for i in users:
                userL.append(i.national_code)

            return Response(userL)
        else:
            return Response({'message': 'there isnt any user'})

    else:
        return Response({'message': 'you are not admin'})


class Category_list(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return [Category.objects.filter(Id_id=self.request.user.id).first()]


class userOwner(APIView):
    def get(self, request):
        user_owner = UserOwner.objects.all()
        ser_userowner = UserOwnerSerializer(instance=user_owner, many=True)
        return Response(data=ser_userowner.data)


def orderb(id):
    # this order is toman

    date_now = str(datetime.datetime.now()).split(' ')[0].replace('-', ',')
    date_spilt = date_now.split(',')
    date = datetime.date(int(date_spilt[0]), int(date_spilt[1]), int(date_spilt[2]))
    orders = []
    for i in range(30):
        days = datetime.timedelta(i)
        date_week = str(date - days).split('-')
        products = MlmProductsOrders.objects.filter(shopper_id=id, payment_date__year=date_week[0],
                                                    payment_date__month=date_week[1], payment_date__day=date_week[2],
                                                    payment_status=True).order_by('id').all()


        orders.append(sum([p.price for p in products]))

    return sum(orders)

def orderbS(id):
    # this order is toman

    date_now = str(datetime.datetime.now()).split(' ')[0].replace('-', ',')
    date_spilt = date_now.split(',')
    date = datetime.date(int(date_spilt[0]), int(date_spilt[1]), int(date_spilt[2]))
    orders = []
    for i in range(30):
        days = datetime.timedelta(i)
        date_week = str(date - days).split('-')
        products = MlmProductsOrders.objects.filter(shopper_id=id, payment_date__year=date_week[0],
                                                    payment_date__month=date_week[1], payment_date__day=date_week[2],
                                                    payment_status=True).order_by('id').all()


        orders.append(sum([p.price * p.product.score for p in products]))

    return sum(orders)



def orderbTime(id, date1, date2):
    # this order is toman

    delta = (date2-date1).days
    if delta < 0:
        return 'error date2 is less than date1'

    orders = []
    for i in range(delta):
        days = datetime.timedelta(i)
        date_week = str(date2 - days).split('-')
        products = MlmProductsOrders.objects.filter(shopper_id=id, payment_date__year=date_week[0],
                                                    payment_date__month=date_week[1], payment_date__day=date_week[2],
                                                    payment_status=True).order_by('id').all()


        orders.append(sum([p.price for p in products]))

    return sum(orders)


def orderbSTime(id, date1, date2):
    # this order is toman

    delta = (date2 - date1).days

    if delta < 0:
        return 'error date2 is less than date1'

    orders = []
    for i in range(delta):
        days = datetime.timedelta(i)
        date_week = str(date2 - days).split('-')
        products = MlmProductsOrders.objects.filter(shopper_id=id, payment_date__year=date_week[0],
                                                    payment_date__month=date_week[1], payment_date__day=date_week[2],
                                                    payment_status=True).order_by('id').all()

        orders.append(sum([p.price*p.product.score for p in products]))
    return sum(orders)


class get_owner_class(APIView):
    def get(self, request):

        code = request.GET.get('code')

        if request.user.is_authenticated:
            userId = request.user.id
            ownerId0 = Users.objects.filter(identifierـcode=code).first()

            if ownerId0:
                ownerId = ownerId0.id

            else:
                return Response({'message': 'identify code is wrong'})

            if UserOwner.objects.filter(MlmUser_id=userId):
                return Response({'message': 'you have one upline'})

            if userId == ownerId:
                return Response({'message': 'you cant be in your branch'})

            if ownerId is not None:
                if UserOwner.objects.filter(MlmOwner_id=ownerId):
                    count = UserOwner.objects.filter(MlmOwner_id=ownerId).count()
                    if int(count) < 5:
                        owner_user = UserOwner.objects.create(MlmOwner_id=ownerId, MlmUser_id=userId)
                        return Response({'message': 'create..'})

                    else:
                        return Response({'message': 'you just can have 5 branches'})

                else:
                    owner_user = UserOwner.objects.create(MlmOwner_id=ownerId, MlmUser_id=userId)
                    return Response({'message': 'create..'})

            else:
                return Response({'message': 'this identification code doese not exist'})

        else:
            return Response({'message': 'first login'})


def branches(id):

    owner = Users.objects.filter(id=id).first()
    mlmuser = []

    if owner is None:
        return Response('there is no user whit this code')

    else:
        branches = UserOwner.objects.filter(MlmOwner_id=id).all()
        branches_no = UserOwner.objects.filter(MlmOwner_id=id).all().count()

        if branches is not None:
            for i in range(branches_no):
                mlmuser.append(branches[i].MlmUser)
        else:
            mlmuser = None


    return mlmuser


def Order(id):


    sum_order = orderbS(id)
    if branches(id) is not None:
        for br1 in branches(id):
            sum_order += orderbS(br1.id)
            if branches(br1.id) is not None:
                for br2 in branches(br1.id):
                    sum_order += orderbS(br2.id)
                    if branches(br2.id) is not None:
                        for br3 in branches(br2.id):
                            sum_order += orderbS(br3.id)
                            if branches(br3.id) is not None:
                                for br4 in branches(br3.id):
                                    sum_order += orderbS(br4.id)
                                    if branches(br4.id) is not None:
                                        for br5 in branches(br4.id):
                                            sum_order += orderbS(br5.id)
                                            if branches(br5.id) is not None:
                                                for br6 in branches(br5.id):
                                                    sum_order += orderbS(br6.id)


    return sum_order


def OrderSTime(id, date1, date2):


    sum_order = 0
    if branches(id) is not None:
        for br1 in branches(id):
            sum_order += orderbSTime(br1.id, date1, date2)
            if branches(br1.id) is not None:
                for br2 in branches(br1.id):
                    sum_order += orderbSTime(br2.id, date1, date2)
                    if branches(br2.id) is not None:
                        for br3 in branches(br2.id):
                            sum_order += orderbSTime(br3.id, date1, date2)
                            if branches(br3.id) is not None:
                                for br4 in branches(br3.id):
                                    sum_order += orderbSTime(br4.id, date1, date2)
                                    if branches(br4.id) is not None:
                                        for br5 in branches(br4.id):
                                            sum_order += orderbSTime(br5.id, date1, date2)
                                            if branches(br5.id) is not None:
                                                for br6 in branches(br5.id):
                                                    sum_order += orderbSTime(br6.id, date1, date2)


    return sum_order



def Orderb(id):


    sum_order = orderb(id)
    if branches(id) is not None:
        for br1 in branches(id):
            sum_order += orderb(br1.id)
            if branches(br1.id) is not None:
                for br2 in branches(br1.id):
                    sum_order += orderb(br2.id)
                    if branches(br2.id) is not None:
                        for br3 in branches(br2.id):
                            sum_order += orderb(br3.id)
                            if branches(br3.id) is not None:
                                for br4 in branches(br3.id):
                                    sum_order += orderb(br4.id)
                                    if branches(br4.id) is not None:
                                        for br5 in branches(br4.id):
                                            sum_order += orderb(br5.id)
                                            if branches(br5.id) is not None:
                                                for br6 in branches(br5.id):
                                                    sum_order += orderb(br6.id)


    return sum_order



def OrderbTime(id, date1, date2):


    sum_order = 0
    if branches(id) is not None:
        for br1 in branches(id):
            sum_order += orderbTime(br1.id, date1, date2)
            if branches(br1.id) is not None:
                for br2 in branches(br1.id):
                    sum_order += orderbTime(br2.id, date1, date2)
                    if branches(br2.id) is not None:
                        for br3 in branches(br2.id):
                            sum_order += orderbTime(br3.id, date1, date2)
                            if branches(br3.id) is not None:
                                for br4 in branches(br3.id):
                                    sum_order += orderbTime(br4.id, date1, date2)
                                    if branches(br4.id) is not None:
                                        for br5 in branches(br4.id):
                                            sum_order += orderbTime(br5.id, date1, date2)
                                            if branches(br5.id) is not None:
                                                for br6 in branches(br5.id):
                                                    sum_order += orderbTime(br6.id, date1, date2)


    return sum_order



class category_class(APIView):
    def get(self, request):

        if request.user.is_authenticated:
            Id = request.user.id

        else:
            return Response({'message': 'first login'})

        if Category.objects.filter(Id_id=Id).first():
            Category.objects.filter(Id_id=Id).all().delete()
            if branches(Id):
                for br1 in branches(Id):
                    if Category.objects.filter(Id_id=br1.id).first():
                        Category.objects.filter(Id_id=br1.id).all().delete()
                        if branches(br1.id):
                            for br2 in branches(br1.id):
                                if Category.objects.filter(Id_id=br2.id).first():
                                    Category.objects.filter(Id_id=br2.id).all().delete()
                                    if branches(br2.id):
                                        for br3 in branches(br2.id):
                                            if Category.objects.filter(Id_id=br3.id).first():
                                                Category.objects.filter(Id_id=br3.id).all().delete()
                                                if branches(br3.id):
                                                    for br4 in branches(br3.id):
                                                        if Category.objects.filter(Id_id=br4.id).first():
                                                            Category.objects.filter(Id_id=br4.id).all().delete()
                                                            if branches(br4.id):
                                                                for br5 in branches(br4.id):
                                                                    if Category.objects.filter(Id_id=br5.id).first():
                                                                        Category.objects.filter(Id_id=br5.id).all().delete()
                                                                        if branches(br5.id):
                                                                            for br6 in branches(br5.id):
                                                                                if Category.objects.filter(Id_id=br6.id).first():
                                                                                    Category.objects.filter(Id_id=br6.id).all().delete()
                                                                                    if branches(br6.id):
                                                                                        for br7 in branches(br6.id):
                                                                                            if Category.objects.filter(Id_id=br7.id).first():
                                                                                                Category.objects.filter(Id_id=br7.id).all().delete()
                                                                                                if branches(br7.id):
                                                                                                    for br8 in branches(br7.id):
                                                                                                        if Category.objects.filter(Id_id=br8.id).first():
                                                                                                            Category.objects.filter(Id_id=br8.id).all().delete()
                                                                                                            if branches(br8.id):
                                                                                                                for br9 in branches(br8.id):
                                                                                                                    if Category.objects.filter(Id_id=br9.id).first():
                                                                                                                        Category.objects.filter(Id_id=br9.id).all().delete()
                                                                                                                        if branches(br9.id):
                                                                                                                            for br10 in branches(br9.id):
                                                                                                                                if Category.objects.filter(Id_id=br10.id).first():
                                                                                                                                    Category.objects.filter(Id_id=br10.id).all().delete()

        return categoryN(Id)


def categoryId(Id):

    #similar to caegory function for pursant

    if Category.objects.filter(Id_id=Id).first():
        Category.objects.filter(Id_id=Id).all().delete()
        if branches(Id):
            for br1 in branches(Id):
                if Category.objects.filter(Id_id=br1.id).first():
                    Category.objects.filter(Id_id=br1.id).all().delete()
                    if branches(br1.id):
                        for br2 in branches(br1.id):
                            if Category.objects.filter(Id_id=br2.id).first():
                                Category.objects.filter(Id_id=br2.id).all().delete()
                                if branches(br2.id):
                                    for br3 in branches(br2.id):
                                        if Category.objects.filter(Id_id=br3.id).first():
                                            Category.objects.filter(Id_id=br3.id).all().delete()
                                            if branches(br3.id):
                                                for br4 in branches(br3.id):
                                                    if Category.objects.filter(Id_id=br4.id).first():
                                                        Category.objects.filter(Id_id=br4.id).all().delete()
                                                        if branches(br4.id):
                                                            for br5 in branches(br4.id):
                                                                if Category.objects.filter(Id_id=br5.id).first():
                                                                    Category.objects.filter(Id_id=br5.id).all().delete()
                                                                    if branches(br5.id):
                                                                        for br6 in branches(br5.id):
                                                                            if Category.objects.filter(Id_id=br6.id).first():
                                                                                Category.objects.filter(Id_id=br6.id).all().delete()
                                                                                if branches(br6.id):
                                                                                    for br7 in branches(br6.id):
                                                                                        if Category.objects.filter(Id_id=br7.id).first():
                                                                                            Category.objects.filter(Id_id=br7.id).all().delete()
                                                                                            if branches(br7.id):
                                                                                                for br8 in branches(br7.id):
                                                                                                    if Category.objects.filter(Id_id=br8.id).first():
                                                                                                        Category.objects.filter(Id_id=br8.id).all().delete()
                                                                                                        if branches(br8.id):
                                                                                                            for br9 in branches(br8.id):
                                                                                                                if Category.objects.filter(Id_id=br9.id).first():
                                                                                                                    Category.objects.filter(Id_id=br9.id).all().delete()
                                                                                                                    if branches(br9.id):
                                                                                                                        for br10 in branches(br9.id):
                                                                                                                            if Category.objects.filter(Id_id=br10.id).first():
                                                                                                                                Category.objects.filter(Id_id=br10.id).all().delete()




    return categoryN(Id)


def categoryN(id):

    # order in toman
    Id = id
    order = orderb(Id)
    order_t = Order(Id)
    order_s1 = []
    cat_s1 = []


    if branches(Id) is not None:
        for br1 in branches(Id):

            order1 = orderb(br1.id)
            order_s1.append(order1)
            cate = Category.objects.filter(Id_id=br1.id).order_by('-id').first()

            if cate is not None:
                cat_s1.append(cate.OwnerCategory)

            else:

                categoryN(br1.id)


            order1 = orderb(br1.id)
            order_s1.append(order1)
            cate = Category.objects.filter(Id_id=br1.id).order_by('-id').first()

            if cate is not None:
                cat_s1.append(cate.OwnerCategory)



    j = 0

    cat_upmoshaver = ['moshaver' ,'moshaver_arshad', 'karshenas', 'karshenas_arshad', 'modir_amozesh', 'rahbar', 'rahbar_1star', 'rahbar_2star',
                  'rahbar_arshad', 'rahbar_ejraii', 'rahbar_talaii', 'rahbar_almas', 'safir', 'safir_ejraii',
                  'safir_talaii']
    cat_upmoshaver_arshad = cat_upmoshaver[1:]
    cat_upkarshenas = cat_upmoshaver_arshad[1:]
    cat_upkarshenas_arshad = cat_upkarshenas[1:]
    cat_upmodir_amozesh = cat_upkarshenas_arshad[1:]
    cat_uprahbar = cat_upmodir_amozesh[1:]
    cat_uprahbar_1star = cat_uprahbar[1:]
    cat_uprahbar_2star = cat_uprahbar_1star[1:]
    cat_uprahbar_arshad = cat_uprahbar_2star[1:]
    cat_uprahbar_ejraii = cat_uprahbar_arshad[1:]
    cat_uprahbar_talaii = cat_uprahbar_ejraii[1:]
    cat_uprahbar_almas = cat_uprahbar_talaii[1:]
    cat_upsafir = cat_uprahbar_almas[1:]
    cat_upsafir_ejraii = cat_upsafir[1:]
    cat_upsafir_talaii = cat_upsafir_ejraii[1:]



    if order_t > 5000000000:
        if order >= 4000000:
            if cat_s1:
                for i in cat_s1:
                    if i in cat_upsafir:
                        j += 1
                        cat_s1.remove(i)

                if j >= 3:

                    if order_t/500000 <= 10000:
                        point = order_t/500000
                    else:
                        point = 10000

                    Category.objects.create(OwnerCategory='safir_talaii', Id_id=Id, points=point)
                    return Response({'message':'your group is safir_talaii'})


    j = 0
    if order_t > 3000000000:
        if order >= 4000000:
            if cat_s1:
                for i in cat_s1:
                    if i in cat_uprahbar_almas:
                        j += 1
                        cat_s1.remove(i)

                if j >= 3:
                    if order_t/500000 <= 6000:
                        point = order_t/500000
                    else:
                        point = 6000
                    Category.objects.create(OwnerCategory='safir_ejraii', Id_id=Id, points=point)
                    return Response({'message':'your group is safir_ejraii'})


    j = 0
    if order_t > 1000000000:
        if order >= 4000000:
            if cat_s1:
                for i in cat_s1:
                    if i in cat_uprahbar_talaii:
                        j += 1
                        cat_s1.remove(i)

                if j >= 3:
                    if order_t/500000 <= 4000:
                        point = order_t/500000
                    else:
                        point = 4000
                    Category.objects.create(OwnerCategory='safir', Id_id=Id, points=point)
                    return Response({'message':'your group is safir'})

    j = 0
    if order_t > 700000000:
        if order >= 3000000:
            if cat_s1:
                for i in cat_s1:
                    if i in cat_uprahbar_arshad:
                        j += 1
                        cat_s1.remove(i)

                if j >= 2:
                    if order_t/500000 <= 2000:
                        point = order_t/500000
                    else:
                        point = 2000
                    Category.objects.create(OwnerCategory='rahbar_almas', Id_id=Id, points=point)
                    return Response({'message':'your group is rahbar_almas'})

    j = 0
    if order_t > 500000000:
        if order >= 3000000:
            if cat_s1:
                for i in cat_s1:
                    if i in cat_uprahbar_2star:
                        j += 1
                        cat_s1.remove(i)

                if j >= 2:
                    if order_t/500000 <= 1500:
                        point = order_t/500000
                    else:
                        point = 1500
                    Category.objects.create(OwnerCategory='rahbar_talaii', Id_id=Id, points=point)
                    return Response({'message':'your group is rahbar_talaii'})

    j = 0
    if order_t > 300000000:
        if order >= 2000000:
            if cat_s1:
                for i in cat_s1:
                    if i in cat_uprahbar_1star:
                        j += 1
                        cat_s1.remove(i)

                if j >= 2:
                    if order_t/500000 <= 1000:
                        point = order_t/500000
                    else:
                        point = 1000
                    Category.objects.create(OwnerCategory='rahbar_ejraii', Id_id=Id, points=point)
                    return Response({'message':'your group is rahbar_ejraii'})

    j = 0
    if order_t > 200000000:
        if order >= 2000000:
            if cat_s1:
                for i in cat_s1:
                    if i in cat_uprahbar:
                        j += 1
                        cat_s1.remove(i)

                if j >= 2:
                    if order_t/500000 <= 600:
                        point = order_t/500000
                    else:
                        point = 600
                    Category.objects.create(OwnerCategory='rahbar_arshad', Id_id=Id, points=point)
                    return Response({'message':'your group is rahbar_arshad'})

    j = 0
    if order_t > 150000000:
        if order >= 2000000:
            if cat_s1:
                for i in cat_s1:
                    if i in cat_uprahbar:
                        j += 1
                        cat_s1.remove(i)

                if j >= 2:
                    if order_t/500000 <= 400:
                        point = order_t/500000
                    else:
                        point = 400
                    Category.objects.create(OwnerCategory='rahbar_2star', Id_id=Id, points=point)
                    return Response({'message':'your group is rahbar_2star'})

    j = 0
    if order_t > 70000000:
        if order >= 1500000:
            if cat_s1:
                for i in cat_s1:
                    if i in cat_upmodir_amozesh:
                        j += 1
                        cat_s1.remove(i)

                if j >= 2:
                    if order_t/500000 <= 300:
                        point = order_t/500000
                    else:
                        point = 300
                    Category.objects.create(OwnerCategory='rahbar_1star', Id_id=Id, points=point)
                    return Response({'message':'your group is rahbar_1star'})

    j = 0
    if order >= 1500000:
        if cat_s1:
            for i in cat_s1:
                if i in cat_upmodir_amozesh:
                    j += 1
                    cat_s1.remove(i)

            if j >= 2:
                if order_t/500000 <= 140:
                    point = order_t/500000
                else:
                    point = 140
                Category.objects.create(OwnerCategory='rahbar', Id_id=Id, points=point)
                return Response({'message':'your group is rahbar'})

    if order >= 1000000:
        if cat_s1:
            for i in cat_s1:
                if i in cat_upkarshenas_arshad:
                    j += 1
                    cat_s1.remove(i)

            if j >= 2:

                Category.objects.create(OwnerCategory='modir_amozesh', Id_id=Id, points=0)
                return Response({'message':'your group is modir_amozesh'})


    j = 0
    if order >= 500000:
        if cat_s1:
            for i in cat_s1:
                if i in cat_upkarshenas:
                    j += 1
                    cat_s1.remove(i)

            if j >= 2:
                Category.objects.create(OwnerCategory='karshenas_arshad', Id_id=Id, points=0)
                return Response({'message':'your group is karshenas_arshad'})

    j = 0
    if cat_s1:
        for i in cat_s1:
            if i in cat_upmoshaver_arshad:
                j += 1
                cat_s1.remove(i)

        if j >= 2:
            Category.objects.create(OwnerCategory='karshenas', Id_id=Id, points=0)
            return Response({'message':'your group is karshenas'})

    j = 0
    if cat_s1:
        for i in cat_s1:
            if i in cat_upmoshaver:
                j += 1
                cat_s1.remove(i)

        if j >= 2:
            Category.objects.create(OwnerCategory='moshaver_arshad', Id_id=Id, points=0)
            return Response({'message':'your group is moshaver_arshad'})


    if branches(Id):
        for i in branches(Id):
            if orderb(i.id) >= 200000:
                Category.objects.create(OwnerCategory='moshaver', Id_id=Id, points=0)
                return Response({'message': 'your group is moshaver'})

            elif orderb(i.id) >= 100000:
                Category.objects.create(OwnerCategory='starter', Id_id=Id, points=0)
                return Response({'message': 'your group is starter'})


            else:
                Category.objects.create(OwnerCategory='nothing', Id_id=Id, points=0)
                return Response('you,re not in ranking')
    else:
        Category.objects.create(OwnerCategory='nothing', Id_id=Id, points=0)
        return Response({'message': 'you,re not in ranking'})

    Category.objects.create(OwnerCategory='nothing', Id_id=Id, points=0)
    return Response({'message': 'youre not in this categories ...'})

class commision_class(APIView):
    def post(self, request):

    # every order that append first must run this function
    # order is toman

        if request.user.is_authenticated:
            Id = request.user.id

        else:
            return Response('firsr login')

        product_id = request.data['Pid']
        count = request.data['count']
        product = MlmProducts.objects.filter(id=product_id).first()

        orderR = product.price

        score = product.score


        orderR = orderR * 10
        order = orderR * score
        order = float(order)

        commision = 0

        if order > 0 and order <= 5000000:
            commision = 0.04

        if order > 5000000 and order <= 10000000:
            commision = 0.06

        if order > 10000000 and order <= 20000000:
            commision = 0.08

        if order > 20000000 and order <= 30000000:
            commision = 0.1

        if order > 30000000:
            commision = 0.12

        order = order/10

        user = Users.objects.filter(id=Id).first()
        user.commission += order * commision
        user.save()

        Pursant.objects.create(user_id=Id, amount=order * commision, reson='commision in product')

        price = order - (order * commision)

        orderN = MlmProductsOrders.objects.create(shopper_id=Id, product_id=product_id, price=price)



        return Response({'message': 'product with commisio add'})


class identify_pursant_class(APIView):

    def get(self, request):


        if request.user.is_authenticated:
            Id = request.user.id

        else:
            return Response('first login...')

        owner_pur = 0
        first_order = 0
        # product_id = request.GET.get('Pid')
        # order_id = request.GET.get('id')

        # product = MlmProducts.objects.filter(id=product_id).first()
        order = MlmProductsOrders.objects.filter(shopper_id=request.user.id, payment_status=False).all()
        if order is None:
            return Response({'message': 'you dont have any order'})
        for i in order:
            price = i.product.price
            score = i.product.score
            first_order += price * score
        # price_order = product.price
        # order_score = product.score
        # first_order = price_order * order_score


        order_history = MlmProductsOrders.objects.filter(shopper__id=Id, payment_status=True).first()

        if order_history:
            pass

        else:

            User = UserOwner.objects.filter(MlmUser_id=Id).first()

            if User is not None:
                ownerName = User.MlmOwner.first_name
                ownerId = User.MlmOwner.id
                order_owner = orderb(ownerId)

                cat = Category.objects.filter(Id_id=ownerId).first()

                if cat is not None:
                    pass

                else:
                    categoryN(ownerId)

                cat = Category.objects.filter(Id_id=ownerId).first()


                if cat.OwnerCategory == 'nothing' or cat.OwnerCategory == 'starter':
                    pass

                else:
                    return Response({'message': 'your owner is not starter'})


                if first_order >= 100000 and order_owner != 0:
                    owner_pur = first_order * 0.07

                    USER = GivePursant.objects.filter(user_id=Id).first()

                    TimeM = date.today().month
                    TimeY = date.today().year
                    if USER:
                        RMDate = USER.date.month
                        RYDate = USER.date.year
                        reson = USER.reson

                        if RMDate == TimeM and reson == 'identify pursant':
                            if TimeY == RYDate:
                                pass
                            		
                            else:
                                GivePursant.objects.create(user_id=Id, date=datetime.date.today(), reson='identify pursant')
                                user = Users.objects.filter(id=ownerId).first()
                                user.commission += round(owner_pur)
                                user.walletـbalance += round(owner_pur)
                                user.save()
                                Pursant.objects.create(user_id=ownerId, amount=round(owner_pur), reson='identify pursant')

                                return Response(f'{ownerName}  give  {round(owner_pur)}')

                        else:

                            GivePursant.objects.create(user_id=Id, date=datetime.date.today(), reson='identify pursant')
                            user = Users.objects.filter(id=ownerId).first()
                            user.commission += round(owner_pur)
                            user.walletـbalance += round(owner_pur)
                            user.save()
                            Pursant.objects.create(user_id=ownerId, amount=round(owner_pur), reson='identify pursant')
                            return Response(f'{ownerName}  give  {round(owner_pur)}')



                    else:
                        GivePursant.objects.create(user_id=Id, date=datetime.date.today(), reson='identify pursant')
                        user = Users.objects.filter(id=ownerId).first()
                        user.commission += round(owner_pur)
                        user.walletـbalance += round(owner_pur)
                        user.save()
                        Pursant.objects.create(user_id=ownerId, amount=round(owner_pur), reson='identify pursant')


                        return Response(f'{ownerName}  give  {round(owner_pur)}')

                else:
                    return Response({'message': 'no identify pursant'})

            else:
                return Response({'message': 'there isnt any user with this id or you dont have upline'})

        return Response({'message': 'you dont have identify pursant'})



def monthO():

    date_now = str(datetime.datetime.now()).split(' ')[0].replace('-', ',')
    date_spilt = date_now.split(',')
    date = datetime.date(int(date_spilt[0]), int(date_spilt[1]), int(date_spilt[2]))
    orders = []
    for i in range(30):
        days = datetime.timedelta(i)
        date_week = str(date - days).split('-')
        products = MlmProductsOrders.objects.filter(payment_date__year=date_week[0], payment_date__month=date_week[1],payment_date__day=date_week[2],payment_status=True).order_by('id').all()
        orders.append(sum([p.price for p in products]))
    return orders


class pursant_class(APIView):
    def get(self, request):
        order_s1 = []
        pursant_list = []
        month_sale = sum(monthO()) * 0.1
        if request.user.is_authenticated:
            Id = request.user.id

        else:
            return Response({'message': 'first login...'})

        categoryId(Id)
        category = Category.objects.filter(Id_id=Id).last().OwnerCategory

        if category in ['moshaver', 'moshaver_arshad', 'karshenas', 'karshenas_arshad', 'modir_amozesh']:

            for i in branches(Id):
                order_s1.append(Order(i.id))

            if category == 'moshaver':

                if IsMoshaver.objects.filter(user_id=Id).first():
                    return Response({'message': 'you get your pursant, for more... increase your category'})

                else:
                    IsMoshaver.objects.create(flag=1, user_id=Id)
                    pursant_p = 0.02

            if category == 'moshaver_arshad':
                pursant_p = 0.03

            if category == 'karshenas':
                pursant_p = 0.04

            if category == 'karshenas_arshad':
                pursant_p = 0.05

            if category == 'modir_amozesh':
                pursant_p = 0.06

            for j in order_s1:
                if j * pursant_p > min(order_s1) * 0.1:
                    pursant_list.append(min(order_s1) * 0.1)

                else:
                    pursant_list.append(j * pursant_p)

            USER = GivePursant.objects.filter(user_id=Id).first()

            MTime = date.today().month
            YTime = date.today().year


            if USER:
                RYDate = USER.date.year
                RMDate = USER.date.month
                typeP = USER.reson

                if RMDate == MTime and typeP == 'month pursant':
                    if RYDate == YTime:
                        pass
                    	
                    else:
                        GivePursant.objects.create(user_id=Id, date=datetime.date.today(), reson='month pursant')
                        user = Users.objects.filter(id=Id).first()
                        user.commission += sum(pursant_list)
                        user.walletـbalance += sum(pursant_list)
                        user.save()
                        Pursant.objects.create(user_id=Id, amount=sum(pursant_list), reson='month pursant')
                    	

                else:

                    GivePursant.objects.create(user_id=Id, date=datetime.date.today(), reson='month pursant')
                    user = Users.objects.filter(id=Id).first()
                    user.commission += sum(pursant_list)
                    user.walletـbalance += sum(pursant_list)
                    user.save()
                    Pursant.objects.create(user_id=Id, amount=sum(pursant_list), reson='month pursant')

            else:
                GivePursant.objects.create(user_id=Id, date=datetime.date.today(), reson='month pursant')
                user = Users.objects.filter(id=Id).first()
                user.commission += sum(pursant_list)
                user.walletـbalance += sum(pursant_list)
                user.save()
                Pursant.objects.create(user_id=Id, amount=sum(pursant_list), reson='month pursant')

            return Response({'pursant': sum(pursant_list)})

        if category in ['rahbar', 'rahbar_1star', 'rahbar_2star',
                        'rahbar_arshad', 'rahbar_ejraii', 'rahbar_talaii', 'rahbar_almas', 'safir', 'safir_ejraii',
                        'safir_talaii']:

            point = Category.objects.filter(Id_id=Id).first().points

            all_categories = Category.objects.all()
            category_list = []
            sum_points = 0

            for i in all_categories:
                if i.Id.national_code in category_list:
                    pass
                else:
                    category_list.append(i.Id.national_code)

            for j in category_list:
                sum_points += Category.objects.filter(Id__national_code=j).first().points

            USER = GivePursant.objects.filter(user_id=Id).first()

            MTime = date.today().month
            YTime = date.today().year
            if USER:
                RYDate = USER.date.year
                RMDate = USER.date.month
                typeP = USER.reson

                if RMDate == MTime and typeP == 'month pursant':
                    if YTime == RYDate:
                        pass
                    else:
                        GivePursant.objects.create(user_id=Id, date=datetime.date.today(), reson='month pursant')
                        user = Users.objects.filter(id=Id).first()
                        user.commission += round((month_sale / sum_points) * point)
                        user.walletـbalance += round((month_sale / sum_points) * point)
                        user.save()
                        Pursant.objects.create(user_id=Id, amount=round((month_sale / sum_points) * point),
                                               reson='month pursant')

                else:
                    GivePursant.objects.create(user_id=Id, date=datetime.date.today(), reson='month pursant')
                    user = Users.objects.filter(id=Id).first()
                    user.commission += round((month_sale / sum_points) * point)
                    user.walletـbalance += round((month_sale / sum_points) * point)
                    user.save()
                    Pursant.objects.create(user_id=Id, amount=round((month_sale / sum_points) * point), reson='month pursant')

            else:
                GivePursant.objects.create(user_id=Id, date=datetime.date.today(), reson='month pursant')
                user = Users.objects.filter(id=Id).first()
                user.commission += round((month_sale / sum_points) * point)
                user.walletـbalance += round((month_sale / sum_points) * point)
                user.save()
                Pursant.objects.create(user_id=Id, amount=round((month_sale / sum_points) * point), reson='month pursant')

            return Response({'pursant': round((month_sale / sum_points) * point)})

        return Response({'message': 'your CATEGORY has nothing'})


class seeBranches(APIView):
    def get(self, request):

        if request.user.is_authenticated:
            Id = request.user.id

        else:
            return Response({'message': 'first login...'})

        branch_t_list = []
        Branch = []
        branchs1 = []
        branchs2 = []
        branchs3 = []
        branchs4 = []
        branchs5 = []
        branchs6 = []
        branchs7 = []
        branchs8 = []
        branchs9 = []
        branchs10 = []

        b1 = 0
        b2 = 0
        b3 = 0
        b4 = 0
        b5 = 0
        b6 = 0
        b7 = 0
        b8 = 0
        b9 = 0
        b10 = 0

        categoryId(Id)

        if branches(Id):
            for br1 in branches(Id):
                branch_t_list = []
                branchs1 = []
                branchs2 = []
                branchs3 = []
                branchs4 = []
                branchs5 = []
                branchs6 = []
                branchs7 = []
                branchs8 = []
                branchs9 = []
                branchs10 = []

                category = Category.objects.filter(Id_id=br1.id).last().OwnerCategory
                branchs1.append({'first_name': br1.first_name,'category': category})


                if branches(br1.id):
                    for br2 in branches(br1.id):
                        branchs3 = []
                        branchs4 = []
                        branchs5 = []
                        branchs6 = []
                        branchs7 = []
                        branchs8 = []
                        branchs9 = []
                        branchs10 = []
                        category = Category.objects.filter(Id_id=br2.id).last().OwnerCategory
                        branchs2.append({'first_name': br2.first_name, 'category': category})


                        if branches(br2.id):
                            for br3 in branches(br2.id):
                                branchs4 = []
                                branchs5 = []
                                branchs6 = []
                                branchs7 = []
                                branchs8 = []
                                branchs9 = []
                                branchs10 = []
                                category = Category.objects.filter(Id_id=br3.id).last().OwnerCategory
                                branchs3.append({'first_name': br3.first_name, 'category': category})



                                if branches(br3.id):
                                    for br4 in branches(br3.id):
                                        branchs5 = []
                                        branchs6 = []
                                        branchs7 = []
                                        branchs8 = []
                                        branchs9 = []
                                        branchs10 = []
                                        category = Category.objects.filter(Id_id=br4.id).last().OwnerCategory
                                        branchs4.append({'first_name': br4.first_name, 'category': category})



                                        if branches(br4.id):
                                            for br5 in branches(br4.id):
                                                branchs6 = []
                                                branchs7 = []
                                                branchs8 = []
                                                branchs9 = []
                                                branchs10 = []
                                                category = Category.objects.filter(Id_id=br5.id).last().OwnerCategory
                                                branchs5.append({'first_name': br5.first_name, 'category': category})



                                                if branches(br5.id):
                                                    for br6 in branches(br5.id):
                                                        branchs7 = []
                                                        branchs8 = []
                                                        branchs9 = []
                                                        branchs10 = []
                                                        category = Category.objects.filter(Id_id=br6.id).last().OwnerCategory
                                                        branchs6.append({'first_name': br6.first_name, 'category': category})



                                                        if branches(br6.id):
                                                            for br7 in branches(br6.id):
                                                                branchs8 = []
                                                                branchs9 = []
                                                                branchs10 = []
                                                                category = Category.objects.filter(Id_id=br7.id).last().OwnerCategory
                                                                branchs7.append({'first_name': br7.first_name, 'category': category})



                                                                if branches(br7.id):
                                                                    for br8 in branches(br7.id):
                                                                        branchs9 = []
                                                                        branchs10 = []
                                                                        category = Category.objects.filter(Id_id=br8.id).last().OwnerCategory
                                                                        branchs8.append({'first_name': br8.first_name, 'category': category})



                                                                        if branches(br8.id):
                                                                            for br9 in branches(br8.id):
                                                                                branchs10 = []
                                                                                category = Category.objects.filter(Id_id=br9.id).last().OwnerCategory
                                                                                branchs9.append({'first_name': br9.first_name, 'category': category})



                                                                                if branches(br9.id):
                                                                                    for br10 in branches(br9.id):
                                                                                        category = Category.objects.filter(Id_id=br10.id).last().OwnerCategory
                                                                                        branchs10.append({'first_name': br10.first_name, 'category': category})

                                                                                    branchs9.append(branchs10)

                                                                            branchs8.append(branchs9)

                                                                    branchs7.append(branchs8)

                                                            branchs6.append(branchs7)

                                                    branchs5.append(branchs6)

                                            branchs4.append(branchs5)

                                    branchs3.append(branchs4)

                            branchs2.append(branchs3)

                    branchs1.append(branchs2)

                # branch_t_list.append(branchs1)

                Branch.append(branchs1)


        return Response(Branch)


class seeBranchesN(APIView):
    def get(self, request):

        if request.user.is_authenticated:
            Id = request.user.id

        else:
            return Response({'message': 'first login...'})

        Branch = []


        categoryId(Id)
        ownerA = Users.objects.filter(id=Id).first()

        Branch.append({'first_name': ownerA.first_name, 'id': Id})

        if branches(Id):
            for br1 in branches(Id):

                category = Category.objects.filter(Id_id=br1.id).last().OwnerCategory

                Branch.append({'first_name': br1.first_name,'category': category, 'id': br1.id, 'pid': Id, 'owner_name': ownerA.first_name })


                if branches(br1.id):
                    for br2 in branches(br1.id):

                        category = Category.objects.filter(Id_id=br2.id).last().OwnerCategory
                        Branch.append({'first_name': br2.first_name, 'category': category, 'id': br2.id,'pid': br1.id, 'owner_name': br1.first_name})


                        if branches(br2.id):
                            for br3 in branches(br2.id):

                                category = Category.objects.filter(Id_id=br3.id).last().OwnerCategory
                                Branch.append({'first_name': br3.first_name, 'category': category, 'id': br3.id,'pid': br2.id, 'owner_name': br2.first_name})



                                if branches(br3.id):
                                    for br4 in branches(br3.id):

                                        category = Category.objects.filter(Id_id=br4.id).last().OwnerCategory
                                        Branch.append({'first_name': br4.first_name, 'category': category, 'id': br4.id, 'pid': br3.id, 'owner_name': br3.first_name})



                                        if branches(br4.id):
                                            for br5 in branches(br4.id):

                                                category = Category.objects.filter(Id_id=br5.id).last().OwnerCategory
                                                Branch.append({'first_name': br5.first_name, 'category': category, 'id': br5.id,'pid': br4.id, 'owner_name': br4.first_name})



                                                if branches(br5.id):
                                                    for br6 in branches(br5.id):

                                                        category = Category.objects.filter(Id_id=br6.id).last().OwnerCategory
                                                        Branch.append({'first_name': br6.first_name, 'category': category, 'id': br6.id, 'pid': br5.id, 'owner_name': br5.first_name})



                                                        if branches(br6.id):
                                                            for br7 in branches(br6.id):

                                                                category = Category.objects.filter(Id_id=br7.id).last().OwnerCategory
                                                                Branch.append({'first_name': br7.first_name, 'category': category, 'id': br7.id, 'pid': br6.id, 'owner_name': br6.first_name})



                                                                if branches(br7.id):
                                                                    for br8 in branches(br7.id):

                                                                        category = Category.objects.filter(Id_id=br8.id).last().OwnerCategory
                                                                        Branch.append({'first_name': br8.first_name, 'category': category,'id': br8.id,'pid': br7.id, 'owner_name': br7.first_name})



                                                                        if branches(br8.id):
                                                                            for br9 in branches(br8.id):
                                                                                category = Category.objects.filter(Id_id=br9.id).last().OwnerCategory
                                                                                Branch.append({'first_name': br9.first_name, 'category': category, 'id': br9.id,'pid': br8.id, 'owner_name': br8.first_name})



                                                                                if branches(br9.id):
                                                                                    for br10 in branches(br9.id):
                                                                                        category = Category.objects.filter(Id_id=br10.id).last().OwnerCategory
                                                                                        Branch.append({'first_name': br10.first_name, 'category': category,'id': br10.id, 'pid': br9.id, 'owner_name': br9.first_name})




        return Response(Branch)




########needs for wallet
@api_view()
def Requests(request):
    if request.user.is_authenticated:
        Id = request.user.id

    else:
        return Response({'message': 'first login'})

    info = []

    if UserWalletRequest.objects.filter(user_id=Id):


        userwalletInfo = UserWalletRequest.objects.filter(user__id=Id).all()

        for i in userwalletInfo:

            info.append({'store': i.store, 'request': i.requests, 'type': i.type, 'status': i.status, 'date': i.date})

    else:
        return Response({'message': 'you dont have any request'})

    return Response(info)

@api_view()
def store(request):
    if request.user.is_authenticated:
        Id = request.user.id
        user = Users.objects.filter(id=Id).first()
        userStore = user.walletـbalance

        return Response({'message': f'your store is {userStore}'})

    else:
        return Response({'message': 'first login'})


@api_view()
def Pickup(request):

    if request.user.is_authenticated:
        Id = request.user.id

    else:
        return Response({'message': 'first login'})

    pickup = int(request.GET.get('pickup'))

    user = Users.objects.filter(id=Id).first()
    userStore = user.walletـbalance

    if pickup <= userStore:

        user.walletـbalance -= pickup
        user.save()

        UserWalletRequest.objects.create(store=user.walletـbalance, requests=pickup, user_id=Id, type='pickup')

        return Response({'message':'request for pickup add...'})

    else:
        return Response({'message': 'your request for pickup is more than your supply'})

# @api_view(['post'])
# def settle(request):
#     if request.user.is_authenticated:
#         Id = request.user.id
#
#     else:
#         return Response({'message': 'first login'})
#
#     settle = int(request.data['settle'])
#     status1 = request.data['status']
#     user = Users.objects.filter(id=Id).first()
#
#     # wallet_info = UserWalletRequest.objects.filter(id=Sid).first()
#
#     if status1 == 'True':
#
#         user.walletـbalance += settle
#         user.save()
#         wallet_info = UserWalletRequest.objects.create(store=user.walletـbalance, requests=settle, user_id=Id,
#                                                        type='settle', status=True)
#
#         return Response({'message': 'request for settle add...'})
#
#     wallet_info = UserWalletRequest.objects.create(store=user.walletـbalance, requests=settle, user_id=Id, type='settle')
#
#
#     return Response({'message': 'settle incomplete'})

@api_view()
def adjust(request):
    if request.user.is_authenticated:
        Id = request.user.id

    else:
        return Response({'message': 'first login'})


    user = Users.objects.filter(id=Id).first()
    userStore = user.walletـbalance

    user.walletـbalance = 0
    user.save()
    UserWalletRequest.objects.create(store=user.walletـbalance, requests=userStore, user_id=Id, type='adjust')
    return Response({'message': 'request for adjust add...'})

@api_view(['post'])
def transmition(request):
    if request.user.is_authenticated:
        Id = request.user.id

    else:
        return Response({'message': 'first login...'})

    national_code = int(request.data['national_code'])
    trans_order = int(request.data['trans_order'])
    T_user = Users.objects.filter(national_code=national_code).first()

    if T_user is not None:
        pass
    else:
        return Response({'message': 'wrong national code'})

    user = Users.objects.filter(id=Id).first()

    if trans_order <= user.walletـbalance:
        user.walletـbalance -= trans_order
        user.save()
        UserWalletRequest.objects.create(store=user.walletـbalance, requests=trans_order, type='Transmition', user_id=Id, status=True)
        T_user = Users.objects.filter(national_code=national_code).first()
        T_user.walletـbalance += trans_order
        T_user.save()
        UserWalletRequest.objects.create(store=user.walletـbalance, requests=trans_order, type='Transmition', user_id=T_user.id, status=True)

        return Response({'message': f'transmition done for: {national_code}'})

    else:
        return Response({'message': 'your request for transmition is more than your supply'})


@api_view(['post'])
def SumOfOrders(request):
    if request.user.is_authenticated:
        Id = request.user.id

    else:
        return Response({'message': 'first login'})



    date1 = request.data['date1']
    date2 = request.data['date2']


    orders = orderbTime(Id, date1, date2)
    orderbS = orderbSTime(Id, date1, date2)
    branch_order = OrderbTime(Id, date1, date2)
    branch_score = OrderSTime(Id, date1, date2)


    return Response({'user_order': orders, 'score': orderbS,'branch_order': branch_order, 'branch_score': branch_score})


@api_view(['post'])
def admin_wallet_change(request):

    if request.user.is_authenticated and request.user.is_superuser:
        Id = request.user.id

        user = Users.objects.filter(id=Id).first()

        payment = int(request.data['payment'])
        national_code = int(request.data['national_code'])

        ch_user = Users.objects.filter(national_code=national_code).first()

        if ch_user:
            if payment == 0:
                UserWalletRequest.objects.create(store=0, requests=ch_user.walletـbalance, user_id=ch_user.id, type='admin adjust')
                ch_user.walletـbalance = 0
                ch_user.save()
                return Response({'message': 'user wallet adjust'})

            if payment > 0:

                ch_user.walletـbalance += payment
                ch_user.save()
                UserWalletRequest.objects.create(store=ch_user.walletـbalance, requests=payment, user_id=ch_user.id, type='admin payment')


                return Response({'message': 'user wallet change'})

            else:
                return Response({'message': 'payment is incorrect'})
        else:
            return Response({'message': 'this national code is not exist'})

    else:
        return Response({'message': 'first login'})


#######list of products
@api_view()
def list_online_products(request):
    if request.user.is_authenticated:
        Id = request.user.id

    else:
        return Response({'message': 'first login'})


    productL = []
    products = MlmProducts.objects.filter(user_id=Id).all()

    if products:
        for i in products:
            productL.append({'title': i.title, 'price': i.price, 'imageUrl': i.image.url, 'id': i.id})

        return Response(productL)
    else:
        return Response({'message': 'you dont hve any order'})

@api_view()
def list_personal_products(request):
    if request.user.is_authenticated:
        Id = request.user.id

    else:
        return Response({'message':'first login'})
    proL = []

    products = MlmProducts.objects.filter(user_id=Id).all()
    if products:
        for i in products:
            proL.append({'title': i.title, 'price': i.price,'imag_url': i.image.url, 'id': i.id})
            return Response()
    else:
        return Response({'message': 'you dont hve any order'})

@api_view()
def listOnlineProductsA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        proL = []

        products = MlmProducts.objects.all()
        if products:

            for i in products:
                if i.user is not None:

                    proL.append({'title': i.title, 'price': i.price, 'userPhone': i.user.phone, 'id': i.id})

                else:

                    proL.append({'title': i.title, 'price': i.price, 'id': i.id})


            return Response(proL)

        else:
            return Response({'message': 'your user dont hve any product'})

    else:
        return Response({'message': 'first login or you are admin'})



@api_view()
def listPersonalProductsA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        proL = []

        products = MlmProductsPersonal.objects.all()
        if products:
            for i in products:
                proL.append({'title': i.title, 'price': i.price, 'userPhone': i.user.phone, 'id': i.id})

            return Response(proL)

        else:
            return Response({'message': 'your user dont hve any order'})

    else:
        return Response({'message': 'first login or you are admin'})

@api_view(['post'])
def change_Status_Online_ProductsA(request):
    if request.user.is_authenticated:
        Id = request.user.id

    else:
        return Response({'message': 'first login'})

    user = Users.objects.filter(id=Id).first()

    IdPro = int(request.data['id'])
    # status = request.data['status']

    if request.user.is_superuser:
        products = MlmProducts.objects.filter(id=IdPro).first()
        if products:
            if products.status == False:
                status = True
            else:
                status = False

            products.status = status
            products.save()
            return Response({'message': 'status save'})

        else:
            return Response({'message': 'there is no products'})

    else:
        return Response({'message': 'you are not admin'})

@api_view()
def change_Status_Personal_ProductsA(request):

    if request.user.is_authenticated and request.user.is_superuser:
        Id = request.user.id
        user = Users.objects.filter(id=Id).first()

        IdPro = int(request.data['id'])
        status = request.data['status']

        products = MlmProductsPersonal.objects.filter(id=IdPro).first()
        if products:
            products.status = status
            products.save()
            return Response({'message': 'status save'})

        else:
            return Response({'message': 'there is no products'})

    else:
        return Response({'message': 'first login or you are not admin'})


######### seminars
@api_view()
def participateSeminar(request):

    if request.user.is_authenticated:
        Id = request.user.id

    else:
        return Response({'message': 'first login...'})

    seminarId = int(request.GET.get('seminar'))

    seminar = Seminars.objects.filter(id=seminarId).first()

    if seminar:
        ParticipatSeminar.objects.create(info_id=seminarId, user_id=Id)

        return Response({'message': 'you add to this seminar'})

    else:
        return Response({'message': 'there isnt any seminar with this id'})

@api_view()
def listSeminar(request):
    if request.user.is_authenticated:
        Id = request.user.id

    else:
        return Response({'message': 'first login...'})

    listP = ParticipatSeminar.objects.filter(user_id=Id).all()

    seminarL = []

    if listP:
        for i in listP:
            seminarL.append({'name': i.info.name, 'date': i.info.date})

        return Response(seminarL)

    else:
        return Response({'message': 'you dont have any seminars'})

@api_view()
def deleteSeminarAdmin(request):
    if request.user.is_authenticated and request.user.is_superuser:

        seminarId = request.GET.get('seminar')

        seminar = Seminars.objects.filter(id=seminarId).first()
        if seminar:
            seminar.delete()
            return Response({'message': 'seminar delete...'})

        else:
            return Response({'message': 'there isnt any seminar with this id'})

    else:
        return Response({'message': 'first login or you are not admin'})

@api_view(['post'])
def addSeminarAdmin(request):
    if request.user.is_authenticated or request.user.is_superuser:
        name = request.data['name']
        seminarDate = request.data['date']
        image = request.FILES['image']
        description = request.data['description']

        Seminars.objects.create(date=seminarDate, name=name, image=image, description=description)

        return Response({'message': 'seminar created'})

    else:
        return Response({'message': 'first login or you are not admin'})

@api_view()
def seminarEndA(request):
    if request.user.is_superuser:
        seminarId = request.GET.get('id')
        seminar = Seminars.objects.filter(id=seminarId).first()

        if seminar is None:
            return Response({'message': 'seminar id is wrong'})

        seminar.status = True
        seminar.save()

        return Response({'message': 'status change'})

    return Response({'message': 'you are not admin'})



@api_view()
def seminarListA(request):
    if request.user.is_authenticated:
        Id = request.user.id
        listA = []
        listSeminar = Seminars.objects.all()

        if listSeminar:
            for i in listSeminar:
                participate = ParticipatSeminar.objects.filter(info_id=i.id, user_id=Id).first()
                if participate is not None:
                    participate = 'yes'
                else:
                    participate = 'no'


                listA.append({'name': i.name, 'date': i.date, 'id': i.id, 'image': i.image.url, 'description': i.description,'status': i.status, 'participate': participate})

            return Response(listA)

        else:
            return Response({'message': 'there isnt any seminar'})

    else:
        return Response({'message': 'first login... or you are not admin'})


@api_view()
def seminarListUserA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        Id = request.GET.get('id')
        seminarId = request.GET.get('seminar')

        seminar = Seminars.objects.filter(id=seminarId).first()

        if seminar:
            pass
        else:
            return Response({'message': 'there isnt any seminar'})

        participate = ParticipatSeminar.objects.filter(user_id=Id, info_id=seminarId).first()


        if participate:
            return Response({'status': True})

        else:
            return Response({'status': False})


    else:
        return Response({'message': 'first login... or you are not admin'})


########## copons
@api_view()
def copons(request):
    if request.user.is_authenticated:
        Id = request.user.id

    else:
        return Response({'message': 'first login...'})

    coponsList = []

    copons = Copons.objects.filter(user_id=Id).all()

    if copons:
        for i in copons:
            coponsList.append({'name': i.name, 'percentage': i.percentage, 'id': i.id})

        return Response(coponsList)

    else:
        return Response({'message': 'you dont have any copons'})


@api_view(['post'])
def addCoponsA(request):
    if request.user.is_authenticated and request.user.is_superuser:
        userId = request.data['user_id']
        name = request.data['name']
        persentage = request.data['persentage']

        Copons.objects.create(user_id=userId, name=name, percentage=persentage)
        return Response({'message': 'copon create...'})

    else:
        return Response({'message': 'first login or you are not admin'})


######### katalogs
@api_view()
def catalogs(request):
    listCatalogs = []
    catalogs = Catalogs.objects.all()

    if catalogs:
        for i in catalogs:
            listCatalogs.append({'title': i.title, 'file': i.file.url, 'id': i.id})

        return Response(listCatalogs)

    else:
        return Response({'message': 'there isnt any catalogs'})

@api_view(['post'])
def addCatalogsA(request):

    if request.user.is_authenticated and request.user.is_superuser:

        title = request.data['title']
        file = request.FILES.get('file')

        Catalogs.objects.create(title=title, file=file)

        return Response({'message': 'catalog create'})

    else:
        return Response('first login... or you are not admin')

@api_view()
def deleteCatalogsA(request):

    if request.user.is_authenticated and request.user.is_superuser:

        catId = request.GET.get('catId')

        catalog = Catalogs.objects.filter(id=catId).first()

        if catalog:
            catalog.delete()
            return Response({'message': 'catalog delete'})

        else:
            return Response({'message': 'there isnt any catalog'})

    else:
        return Response({'message': 'first login'})


########### comments
@api_view()
def commentLists(request):

    commentL = []

    comment1 = Comments.objects.first()

    if comment1:
        comments = Comments.objects.all()
        for i in comments:


            commentL.append({'title': i.title, 'id': i.id})

        return Response(commentL)

    else:
        return Response({'message': 'there isnt any comment'})


@api_view()
def responseList(request):

    commentId = request.GET.get('id')
    responseL = []
    response = ResponseC.objects.filter(IdT=commentId).all()
    if response:
        for j in response:
            responseL.append({'response': j.response, 'numbers': j.numbers, 'id': j.id})
            return Response(responseL)

    else:
        return Response({'message': 'there isnt any response'})



@api_view(['post'])
def paComments(request):

    if request.user.is_authenticated:
        Id = request.user.id
    else:
        return Response({'message': 'first login'})

    titleId = request.data['title']
    responseId = int(request.data['resp'])
    comment = CommentsPa.objects.filter(user_id=Id, comment_id=titleId).first()

    if comment is not None:
        return Response({'message': 'you cant vote again'})
    else:
        CommentsPa.objects.create(user_id=Id, comment_id=titleId)


    title = Comments.objects.filter(id=titleId).first()
    responses = ResponseC.objects.filter(IdT=titleId).all()

    if title and responses:
        for i in responses:
            if i.id == responseId:
                i.numbers += 1
                i.save()
                return Response({'message': 'thanks for your comment'})

        return Response({'message': 'no such response'})

    else:
        return Response({'message': 'there isnt title or response'})


@api_view(['post'])
def addTitleA(request):

    if request.user.is_authenticated and request.user.is_superuser:

        title = request.data['title']
        Comments.objects.create(title=title)
        return Response('title add')

    else:
        return Response({'message': 'first login... or you are not admin'})


@api_view(['post'])
def addResponseA(request):

    if request.user.is_authenticated and request.user.is_superuser:

        response = request.data['response']
        titleId = request.data['title']

        comment = Comments.objects.filter(id=titleId).first()

        if comment:
            ResponseC.objects.create(response=response, IdT=titleId, numbers=0)

            return Response({'message': 'create...'})

        else:
            return Response({'message': 'there isnt any comments'})

    else:
        return Response({'message': 'first login or you are not admin'})


@api_view()
def deleteCommentA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        commentId = request.GET.get('cmtId')

        comment = Comments.objects.filter(id=commentId).first()
        response = ResponseC.objects.filter(IdT=commentId).all()

        if comment:
            comment.delete()
            if response:
                response.delete()

            return Response({'message': 'comment delete'})

        else:
            return Response({'message': 'there isnt any comment'})

    else:
        return Response({'message': 'first login... or you are not admin'})


@api_view()
def deleteRespA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        respId = request.GET.get('id')

        response = ResponseC.objects.filter(id=respId).first()

        if response:
            response.delete()

            return Response({'message': 'response delete'})

        return Response({'message': 'there isnt response'})


    else:
        return Response({'message': 'first login... or you are not admin'})


@api_view()
def seeTitlesId(request):
    if request.user.is_authenticated and request.user.is_superuser:
        comments = Comments.objects.all()
        titleL = []

        for i in comments:
            titleL.append({'title': i.title, 'id': i.id})

        return Response(titleL)

@api_view()
def seeResponseId(request):
    if request.user.is_authenticated and request.user.is_superuser:
        response = ResponseC.objects.all()
        respL = []

        for i in response:
            respL.append({'title': i.response, 'numbers': i.numbers,'id': i.id})

        return Response(respL)



@api_view()
def seeResultsA(request):
    if request.user.is_authenticated:

        titleId = request.GET.get('title')
        resultL = []

        title = Comments.objects.filter(id=titleId).first()
        responses = ResponseC.objects.filter(IdT=titleId).all()


        if title and responses:
            for i in responses:
                resultL.append({'response': i.response, 'numer of vote': i.numbers, 'id': i.id})

            return Response(resultL)

        return Response({'message': 'there is no title or response'})
    else:
        return Response('first login... or you are not admin')


############# consultation
@api_view()
def reqCons(request):
    if request.user.is_authenticated:
        Id = request.user.id

        proId = request.GET.get('id')

        product = MlmProducts.objects.filter(id=proId).first()

        if product:
            Consultation.objects.create(product_id=proId, user_id=Id)
            return Response({'message': 'your request send'})

        else:
            return Response({'message': 'there isnt any product with this code'})

    else:
        return Response({'message': 'first login... or you are not admin'})

@api_view()
def consListA(request):
    if request.user.is_authenticated and request.user.is_authenticated:
        consL = []
        cons = Consultation.objects.all()
        if cons:
            for i in cons:
                consL.append({'user_phone': i.user.phone, 'national_code': i.user.national_code,'product': i.product.title, 'id': i.id})

            return Response(consL)

        return Response({'message': 'there isnt any consulation'})

    else:
        return Response({'message': 'first login... or you are not admin'})


#############ticket
@api_view()
def ticketList(request):
    if request.user.is_authenticated:
        Id = request.user.id

        ticket = Ticket.objects.filter(user_id=Id).all()
        ticketL = []

        if ticket:
            for i in ticket:
                ticketL.append({'title': i.title, 'id': i.id})
            return Response(ticketL)

        else:
            return Response({'message': 'you dont have any ticket'})

    else:
        return Response({'message': 'first login...'})

@api_view()
def messageTicketL(request):
    if request.user.is_authenticated:
        Id = request.user.id

    else:
        return Response({'message': 'first login...'})

    titleId = request.GET.get('title')

    titles = Ticket.objects.filter(id=titleId).first()
    if titles.user.id == Id:
        pass
    else:
        return Response({'message': 'this is not your title for ticket'})

    messageL = []

    message = TicketMessage.objects.filter(IdT=titleId).all()

    if message:
        for i in message:
            messageL.append({'message': i.messages, 'id': i.id})

        return Response(messageL)

    return Response({'message': 'no message yet'})

@api_view(['post'])
def sendTitle(request):

    if request.user.is_authenticated:
        Id = request.user.id
        title = request.data['title']
        Ticket.objects.create(user_id=Id, title=title)

        return Response({'message': 'send'})

    else:
        return Response({'message': 'first login'})

@api_view(['post'])
def sendMessage(request):

    if request.user.is_authenticated:
        Id = request.user.id

        titleId = request.data['id']
        message = request.data['message']
        file = request.FILES.get('file')

        ticket = Ticket.objects.filter(id=titleId).first()


        if ticket:

            if ticket.user.id == Id:
                pass
            else:
                return Response({'message': 'error'})

            if file:
                TicketMessage.objects.create(messages=message, IdT=titleId, file=file)

            else:

                TicketMessage.objects.create(messages=message, IdT=titleId)

            return Response({'message': 'send'})

        else:
            return Response({'message': 'there isnt any ticket'})


    else:
        return Response({'message': 'first login'})

@api_view()
def ticketListA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        ticket = Ticket.objects.all()
        ticketL = []

        if ticket:
            for i in ticket:
                ticketL.append({'user_phone': i.user.phone, 'user_national_code': i.user.national_code,'title': i.title, 'is Admin': i.IsAdmin , 'id': i.id})
            return Response(ticketL)

        else:
            return Response({'message': 'user dosent have any ticket'})

    else:
        return Response({'message': 'first login... or you are not admin'})

@api_view()
def messageTicketLA(request):

    if request.user.is_authenticated and request.user.is_superuser:

        titleId = int(request.GET.get('title'))


        messageL = []

        message = TicketMessage.objects.filter(IdT=titleId).all()

        if message:
            for i in message:

                messageL.append({'message': i.messages, 'id': i.id})

            return Response(messageL)

        return Response({'message': 'no message yet'})

    else:
        return Response({'message': 'first login... or you are not admin'})

@api_view(['post'])
def sendTitleA(request):

    if request.user.is_authenticated and request.user.is_superuser:

        national_code = request.data['code']
        title = request.data['title']

        userId = Users.objects.filter(national_code=national_code).first().id

        Ticket.objects.create(user_id=userId, title=title, IsAdmin=True)

        return Response({'message': 'title send'})

    else:
        return Response({'message': 'first login or you are not admin'})

@api_view(['post'])
def sendMessageA(request):

    if request.user.is_authenticated and request.user.is_superuser:

        message = request.data['message']
        titleId = request.data['id']


        ticket = Ticket.objects.filter(id=titleId).first()

        if ticket:
            TicketMessage.objects.create(messages=message, IdT=titleId)

            return Response({'message': 'send'})

        else:
            return Response({'message': 'there isnt any ticket'})

    else:
        return Response({'message': 'first login or you are not admin'})


@api_view(['post'])
def sendTitleAllA(request):

    if request.user.is_authenticated and request.user.is_superuser:

        title = request.data['title']

        user = Users.objects.all()

        for i in user:

            Ticket.objects.create(user_id=i.id, title=title, IsAdmin=True)

        return Response({'message': 'title send to all'})

    else:
        return Response({'message': 'first login or you are not admin'})



################# offers
@api_view()
def seeOffers(request):

    if request.user.is_authenticated:
        Id = request.user.id
        offers = Offers.objects.filter(user_id=Id).all()
        offerL = []

        if offers:
            for i in offers:
                offerL.append({'text': i.text, 'id': i.id})

            return Response(offerL)
        else:
            return Response({'message': 'there isnt any offer'})

    else:
        return Response({'message': 'first login...'})

@api_view(['post'])
def addOffers(request):

    if request.user.is_authenticated:
        Id = request.user.id

        text = request.data['text']

        Offers.objects.create(text=text, user_id=Id)
        return Response({'message': 'offer send'})

    else:
        return Response({'message': 'first login...'})

@api_view()
def seeOffersA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        offers = Offers.objects.all()
        offerL = []

        if offers:
            for i in offers:
                offerL.append({'name': i.user.first_name, 'national_code': i.user.national_code, 'phone': i.user.phone, 'offer': i.text})

            return Response(offerL)

        return Response({'message': 'there isnt any offer'})


    else:
        return Response({'message': 'first login... or you are not admin'})


############# payment report
@api_view()
def paymentReport(request):

    if request.user.is_authenticated:
        Id = request.user.id
        pursL = []

        pursant = Pursant.objects.filter(user_id=Id).all()

        if pursant:
            for i in pursant:
                pursL.append({'amount': i.amount,'reson': i.reson,'status': i.status, 'date': i.date, 'id': i.id})

            return Response(pursL)

        return Response({'message': 'you dont have any pursant'})

    else:
        return Response({'message': 'first login'})


############# agency
@api_view()
def agencyRequest(request):
    if request.user.is_authenticated:
        Id = request.user.id
        Agency.objects.create(user_id=Id)
        return Response({'message': 'your request send'})

    else:
        return Response({'message': 'first login...'})

@api_view()
def agencyListA(request):
    if request.user.is_authenticated and request.user.is_superuser:
        agency = Agency.objects.all()
        agencyL = []

        if request.user.is_superuser:
            if agency:
                for i in agency:
                    agencyL.append({'user_phone': i.user.phone, 'user_national_code': i.user.national_code, 'id': i.id})

                return Response(agencyL)

            return Response({'message': 'there isnt any agency'})

    else:
        return Response({'message': 'first login... or you are not admin'})

@api_view()
def deleteAgencyA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        agencyId = request.GET.get('id')

        agency = Agency.objects.filter(id=agencyId).first()

        if agency:
            agency.delete()

            return Response({'message': 'agency deleted'})

        return Response({'message': 'there isnt any agency with this information'})


    else:
        return Response({'message': 'first login... or you are not admin'})

@api_view()
def confirmAgencyA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        agencyId = request.GET.get('id')

        agency = Agency.objects.filter(id=agencyId).first()

        if agency:
            agency.status = True
            agency.save()

            return Response({'message': 'done'})

        return Response({'message': 'there isnt any agency'})

    else:
        return Response({'message': 'first login or you are not admin'})

@api_view()
def confirmAgencyListA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        confirmL = []

        agency = Agency.objects.filter(status=True).all()

        if agency:
            for i in agency:
                confirmL.append({'user_phone': i.user.phone, 'user_national_code': i.user.national_code, 'id': i.id})

            return Response(confirmL)

        return Response({'message': 'there isnt any agency'})

    else:
        return Response({'message': 'first login'})


@api_view()
def AgencyListA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        confirmL = []

        agency = Agency.objects.filter(status=False).all()

        if agency:
            for i in agency:
                confirmL.append({'user_phone': i.user.phone, 'user_national_code': i.user.national_code, 'status': i.status, 'id': i.id})

            return Response(confirmL)

        return Response({'message': 'there isnt any agency'})

    else:
        return Response({'message': 'first login'})



############### enrol again

@functools.lru_cache()
def get_hashers_by_algorithm():
    return {hasher.algorithm: hasher for hasher in get_hashers()}


def is_password_usable(encoded):
    """
    Return True if this password wasn't generated by
    User.set_unusable_password(), i.e. make_password(None).
    """
    return encoded is None or not encoded.startswith(UNUSABLE_PASSWORD_PREFIX)

@functools.lru_cache()
def get_hashers():
    hashers = []
    for hasher_path in settings.PASSWORD_HASHERS:
        hasher_cls = import_string(hasher_path)
        hasher = hasher_cls()
        if not getattr(hasher, 'algorithm'):
            raise ImproperlyConfigured("hasher doesn't specify an "
                                       "algorithm name: %s" % hasher_path)
        hashers.append(hasher)
    return hashers

@receiver(setting_changed)
def reset_hashers(**kwargs):
    if kwargs['setting'] == 'PASSWORD_HASHERS':
        get_hashers.cache_clear()
        get_hashers_by_algorithm.cache_clear()


def get_hasher(algorithm='default'):
    """
    Return an instance of a loaded password hasher.

    If algorithm is 'default', return the default hasher. Lazily import hashers
    specified in the project's settings file if needed.
    """
    if hasattr(algorithm, 'algorithm'):
        return algorithm

    elif algorithm == 'default':
        return get_hashers()[0]

    else:
        hashers = get_hashers_by_algorithm()
        try:
            return hashers[algorithm]
        except KeyError:
            raise ValueError("Unknown password hashing algorithm '%s'. "
                             "Did you specify it in the PASSWORD_HASHERS "
                             "setting?" % algorithm)


def identify_hasher(encoded):
    """
    Return an instance of a loaded password hasher.

    Identify hasher algorithm by examining encoded hash, and call
    get_hasher() to return hasher. Raise ValueError if
    algorithm cannot be identified, or if hasher is not loaded.
    """
    # Ancient versions of Django created plain MD5 passwords and accepted
    # MD5 passwords with an empty salt.
    if ((len(encoded) == 32 and '$' not in encoded) or
            (len(encoded) == 37 and encoded.startswith('md5$$'))):
        algorithm = 'unsalted_md5'
    # Ancient versions of Django accepted SHA1 passwords with an empty salt.
    elif len(encoded) == 46 and encoded.startswith('sha1$$'):
        algorithm = 'unsalted_sha1'
    else:
        algorithm = encoded.split('$', 1)[0]
    return get_hasher(algorithm)


def mask_hash(hash, show=6, char="*"):
    """
    Return the given hash, with only the first ``show`` number shown. The
    rest are masked with ``char`` for security reasons.
    """
    masked = hash[:show]
    masked += char * len(hash[show:])
    return masked


def must_update_salt(salt, expected_entropy):
    # Each character in the salt provides log_2(len(alphabet)) bits of entropy.
    return len(salt) * math.log2(len(RANDOM_STRING_CHARS)) < expected_entropy


class BasePasswordHasher:
    """
    Abstract base class for password hashers

    When creating your own hasher, you need to override algorithm,
    verify(), encode() and safe_summary().

    PasswordHasher objects are immutable.
    """
    algorithm = None
    library = None
    salt_entropy = 128

    def _load_library(self):
        if self.library is not None:
            if isinstance(self.library, (tuple, list)):
                name, mod_path = self.library
            else:
                mod_path = self.library
            try:
                module = importlib.import_module(mod_path)
            except ImportError as e:
                raise ValueError("Couldn't load %r algorithm library: %s" %
                                 (self.__class__.__name__, e))
            return module
        raise ValueError("Hasher %r doesn't specify a library attribute" %
                         self.__class__.__name__)

def check_password(password, encoded, setter=None, preferred='default'):
    """
    Return a boolean of whether the raw password matches the three
    part encoded digest.

    If setter is specified, it'll be called when you need to
    regenerate the password.
    """
    if password is None or not is_password_usable(encoded):
        return False

    preferred = get_hasher(preferred)
    try:
        hasher = identify_hasher(encoded)
    except ValueError:
        # encoded is gibberish or uses a hasher that's no longer installed.
        return False

    hasher_changed = hasher.algorithm != preferred.algorithm
    must_update = hasher_changed or preferred.must_update(encoded)
    is_correct = hasher.verify(password, encoded)

    # If the hasher didn't change (we don't protect against enumeration if it
    # does) and the password should get updated, try to close the timing gap
    # between the work factor of the current encoded password and the default
    # work factor.
    if not is_correct and not hasher_changed and must_update:
        hasher.harden_runtime(password, encoded)

    if setter and is_correct and must_update:
        setter(password)
    return is_correct

@api_view(['post'])
def enrolAgain(request):

    if request.user.is_authenticated:
        Id = int(request.user.id)
        password = request.data['password']
        user = Users.objects.filter(id=Id).first()

        if check_password(password, user.password):
            pass
        else:
            return Response({'message': 'incorrect password'},  status=status.HTTP_400_BAD_REQUEST)

        user = Users.objects.filter(id=Id).first()

        if user:
            user.delete()
            return Response({'message': 'delete'})

        return Response({'message': 'there isnt any user with this information'}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response({'message': 'first login...'}, status=status.HTTP_400_BAD_REQUEST)



############### didactic file
@api_view()
def didacticFiles(request):

    files = DidacticFile.objects.all()
    fileL = []

    if files:
        for i in files:
            fileL.append({'title': i.title, 'file': i.files.url, 'id': i.id})

        return Response(fileL)

    return Response({'message': 'no files here yet'})

@api_view(['post'])
def addFilesA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        title = request.data['title']
        file = request.FILES.get('file')

        if request.method == 'POST':
            DidacticFile.objects.create(title=title, files=file)

            return Response({'message': 'file add'})

        return Response({'message': 'error'})

    else:
        return Response({'message': 'first login...or you are not admin'})

@api_view()
def deleteFilesA(request):
    if request.user.is_authenticated:

        fileId = request.GET.get('id')

        file = DidacticFile.objects.filter(id=fileId).first()

        if file:

            file.delete()
            return Response({'message': 'file delete'})

        return Response({'message': 'there isnt any file'})

    else:
        return Response('first login... or you are not admin')


############## Product comments
@api_view(['post'])
def addProComment(request):

    if request.user.is_authenticated:
        Id = request.user.id

        proId = request.data['id']
        comment = request.data['comment']

        ProductComment.objects.create(user_id=Id, product_id=proId, comment=comment)

        return Response({'message': 'comment add'})

    else:
        return Response({'message': 'first login...'})

@api_view()
def newProCommentA(request):
    if request.user.is_authenticated and request.user.is_superuser:


        commentL = []

        comments = ProductComment.objects.all()

        if comments:
            for i in comments:
                if i.status == 'not seen':
                    commentL.append({'first_name': i.user.first_name, 'comment': i.comment, 'status': i.status, 'id': i.id})
            return Response(commentL)

        return Response({'message': 'there isnt any comments for this product'})

@api_view()
def confirmProCommentLA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        commentL = []

        comments = ProductComment.objects.all()

        if comments:
            for i in comments:
                if i.status == 'confirm':
                    commentL.append({'first_name': i.user.first_name, 'comment': i.comment, 'status': i.status, 'id': i.id})
            return Response(commentL)

        return Response({'message': 'there isnt any comments for this product'})

    else:
        return Response({'message': 'first login... or you are not admin'})

@api_view()
def ProCommentLA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        commentL = []

        comments = ProductComment.objects.all()

        if comments:
            for i in comments:
                commentL.append({'first_name': i.user.first_name, 'phone_number': i.user.phone,'comment': i.comment, 'product': i.product.title ,'status': i.status, 'id': i.id})
            return Response(commentL)

        return Response({'message': 'there isnt any comments for this product'})

    else:
        return Response({'message': 'first login... or you are not admin'})

@api_view()
def confirmProCommentA(request):

    if request.user.is_authenticated:

        commentId = request.GET.get('id')

        comment = ProductComment.objects.filter(id=commentId).first()

        if comment:
            comment.status = 'confirm'
            comment.save()

            return Response({'message': 'comment confirm'})

        return Response({'message': 'there isnt any comment'})

    else:
        return Response({'message': 'first login...'})



@api_view()
def CommentId(request):
    if request.user.is_authenticated:
        comments = ProductComment.objects.all()
        commentL = []

        for i in comments:
            commentL.append({'comment': i.comment, 'comment id': i.id})




@api_view()
def rejectProCommentA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        commentId = request.GET.get('id')

        comment = ProductComment.objects.filter(id=commentId).first()

        if comment:
            comment.status = 'reject'
            comment.save()

            return Response({'message': 'comment reject'})

        return Response({'message': 'there isnt any comment'})

    else:
        return Response({'message': 'first login... or you are not admin'})


class procommentList(generics.ListAPIView):
    serializer_class = MlmProductsCommentsSerializers

    def get_queryset(self):
        id = self.kwargs['id']
        return ProductComment.objects.filter(product_id=id, status='confirm').all()


############### Products
@api_view()
def OnlineProductsListA(request):

    if request.user.is_authenticated and request.user.is_superuser:

        productL = []

        products = MlmProducts.objects.all()

        if products:
            for i in products:
                productL.append({'title': i.title, 'price': i.price, 'image': i.image.url,'id': i.id})

            return Response(productL)

        return Response({'message': 'there isnt any product'})

    else:
        return Response({'message': 'first login... or you are not admin'})


class addOnlineProductA(generics.CreateAPIView):
    serializer_class = MlmProductsSerializers
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        data = MlmProductsSerializers(data=request.data)
        if data.is_valid():
            data.save()
            data.instance.user = request.user
            data.save()
            return Response({'message': 'product add'})

        else:
            return Response(data.errors)

# @api_view(['post'])
# def addOnlineProductA(request):
#     if request.user.is_authenticated and request.user.is_superuser:
#
#         title = request.data['title']
#         slug = request.data['slug']
#         description = request.data['description']
#         image = request.FILES.get('image')
#         price = request.data['price']
#         # maincategories = request.POST.get('maincategories')
#         # subCategories1 = request.POST.get('subCategories1')
#         # subCategories2 = request.POST.get('subCategories2')
#         volume = request.data['volume']
#         compounds = request.data['compounds']
#         licenseـissuer = request.data['licenseـissuer']
#         date = request.data['date']
#         limit = request.data['limit']
#         status = request.data['status']
#         nameC2 = request.data['nameC2']
#         nameC1 = request.data['nameC1']
#         nameM = request.data['nameM']
#         iamgeM = request.FILES.get('imageM')
#
#         mlmProduct = MlmProducts.objects.create(title=title, slug=slug, descriptions=description, image=image, price=price,
#                                    volume=volume, compounds=compounds,
#                                    licenseـissuer=licenseـissuer, date=date, limit=limit, status=status)
#
#         subCat2 = MlmProductSubCategories_2.objects.create(name=nameC2)
#
#         subCat1 = MlmProductSubCategories_1.objects.create(name=nameC1)
#
#         mainC = MlmProductMainCategories.objects.create(name=nameM, image=iamgeM)
#
#         subCat1.sub_categories2.add(subCat2)
#
#         mainC.sub_categories1.add(subCat1)
#
#         mlmProduct.maincategories.add(mainC)
#         mlmProduct.subCategories1.add(subCat1)
#         mlmProduct.subCategories2.add(subCat2)
#
#
#
#
#         return Response('product add...')
#
#     else:
#         return Response('first login... or you are not admin')

@api_view()
def deleteOnlineProductA(request):

    if request.user.is_authenticated and request.user.is_superuser:

        proId = request.GET.get('id')

        product = MlmProducts.objects.filter(id=proId).first()

        if product:
            product.delete()

            return Response({'message': 'product delete'})

        return Response({'message': 'there isnt any product'})

    else:
        return Response({'message': 'first login... or you are not admin'})


@api_view()
def PersonalProductsListA(request):

    if request.user.is_authenticated and request.user.is_superuser:

        productL = []

        products = MlmProductsPersonal.objects.all()

        if products:
            for i in products:
                productL.append([i.title, i.price])

            return Response(productL)

        return Response({'message': 'there isnt any product'})

    else:
        return Response({'message': 'first login... or you are not admin'})


@api_view(['post'])
def addPersonalProductA(request):
    if request.user.is_authenticated and request.user.is_superuser:

        title = request.data['title']
        slug = request.data['slug']
        description = request.data['description']
        image = request.FILES.get('image')
        price = request.data['price']
        # maincategories = request.POST.get('maincategories')
        # subCategories1 = request.POST.get('subCategories1')
        # subCategories2 = request.POST.get('subCategories2')
        volume = request.data['volume']
        compounds = request.data['compounds']
        licenseـissuer = request.data['licenseـissuer']
        date = request.data['date']
        limit = request.data['limit']
        status = request.data['status']
        nameC2 = request.data['nameC2']
        nameC1 = request.data['nameC1']
        nameM = request.data['nameM']
        iamgeM = request.FILES.get('imageM')

        mlmProduct = MlmProductsPersonal.objects.create(title=title, slug=slug, descriptions=description, image=image, price=price,
                                   volume=volume, compounds=compounds,
                                   licenseـissuer=licenseـissuer, date=date, limit=limit, status=status)

        subCat2 = MlmProductSubCategories_2.objects.create(name=nameC2)

        subCat1 = MlmProductSubCategories_1.objects.create(name=nameC1)

        mainC = MlmProductMainCategories.objects.create(name=nameM, image=iamgeM)

        subCat1.sub_categories2.add(subCat2)

        mainC.sub_categories1.add(subCat1)

        mlmProduct.maincategories.add(mainC)
        mlmProduct.subCategories1.add(subCat1)
        mlmProduct.subCategories2.add(subCat2)

        return Response('product add...')

    else:
        return Response('first login... or you are not admin')

@api_view()
def deletePersonalProductA(request):

    if request.user.is_authenticated and request.user.is_superuser:

        proId = request.GET.get('id')

        product = MlmProductsPersonal.objects.filter(id=proId).first()

        if product:
            product.delete()

            return Response({'message': 'product delete'})

        return Response({'message': 'there isnt any product'})

    else:
        return Response({'message': 'first login... or you are not admin'})



from Users.models import Users
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import Ismlm
from .serializer import *
from .models import *
from random import choices
from string import ascii_lowercase,ascii_letters
from django.shortcuts import get_object_or_404
import datetime

from rest_framework.permissions import IsAuthenticated
from .serializer import UsersSerializers



class user_info(generics.ListAPIView):
    serializer_class = UsersSerializers
    permission_classes = [Ismlm]

    def get(self, request, *args, **kwargs):
        user = Users.objects.filter(id=request.user.id).first()
        owner = UserOwner.objects.filter(MlmUser_id=request.user.id).first()
        #card = Cards.objects.filter(user_id=token_info.user.id).first()
        # walletـbalance  = [p.price_drsd for p in MlmProductsOrders.objects.filter(payment_status=True,shopper_id=token_info.user.id).all()]
        if owner is not None:
            owner_info = Users.objects.filter(id=owner.MlmOwner.id).first()
            return Response({'info': {'first_name': user.first_name, 'last_name': user.last_name,'national_code': user.national_code, 'user_status': user.status,'phone': user.phone ,'mobile1': user.mobile1,'mobile2': user.mobile2,'vocher': user.benـkala,'porsant': user.commission,'status': user.status,'identifierـcode': user.identifierـcode, 'address': user.address, 'date_of_birth': user.dateـofـbirth, 'email': user.email, 'gender': user.gender, 'education': user.education, 'postal_code': user.postalـcode, 'date': user.date_joined, 'owner_national_code': owner_info.national_code, 'marital': user.marital_status, 'father_name': user.father_name, 'wallet_balance': user.walletـbalance, 'bank_account': user.Bank_account_number, 'Sheba': user.Sheba_number}})
        if user is not None:
            return Response({'info': {'first_name': user.first_name, 'last_name': user.last_name, 'national_code': user.national_code,'user_status': user.status,'phone': user.phone ,'mobile1': user.mobile1,'mobile2': user.mobile2,'vocher': user.benـkala,'porsant': user.commission,'status': user.status,'identifierـcode': user.identifierـcode, 'address': user.address, 'date_of_birth': user.dateـofـbirth, 'email': user.email, 'gender': user.gender, 'education': user.education, 'postal_code': user.postalـcode, 'date': user.date_joined, 'marital': user.marital_status, 'father_name': user.father_name, 'wallet_balance': user.walletـbalance, 'bank_account': user.Bank_account_number, 'Sheba': user.Sheba_number}})
        else:
            return Response({'info': 'empty'})
            
            
class cards_add(generics.CreateAPIView):
    serializer_class = MlmProductsCarts
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = MlmProductsCarts(data=request.data)
        if data.is_valid():
            user_token = str(request.headers['Authorization']).split('Token')[1].strip()
            token_info = Token.objects.filter(key=user_token).first()
            cards_check = MlmProductsCarts.objects.filter(user_id=token_info.user.id).first()
            if cards_check is None:
                data.save()
                data.instance.user = token_info.user
                data.save()
                return Response({'message': 'با موفقیت اضافه شد'})
            else:
                return Response({'message': ' از قبل اضافه شده'},status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data.errors)
            
            
class profile_update(generics.UpdateAPIView):
    serializer_class = UsersSerializers
    permission_classes = [Ismlm]

    def update(self, request, *args, **kwargs):
        data = UsersSerializers(data=request.data)
        if data.is_valid():
            # user_token = str(self.request.headers['Authorization']).split('Token')[1].strip()
            # token_info = Token.objects.filter(key=user_token).first()
            # user = Users.objects.filter(id=token_info.user.id).first()
            user = Users.objects.filter(id=request.user.id).first()
            data.update(user, data.validated_data)
            return Response({'message': 'بروز شد'})
        else:
            return Response(data.errors)


# class UserSerializer(serializers.ModelSerializer):
#     profile = ProfileSerializer()
#
#     def update(self, instance, validated_data):
#         """Override update method because we need to update
#         nested serializer for profile
#         """
#         if validated_data.get('profile'):
#             profile_data = validated_data.get('profile')
#             profile_serializer = ProfileSerializer(data=profile_data)
#
#             if profile_serializer.is_valid():
#                 profile = profile_serializer.update(instance=instance.profile)
#                 validated_data['profile'] = profile
#
#         return super(UserSerializer, self).update(instance, validated_data)
#
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'first_name', 'last_name', 'profile')

            

class orders_list(generics.ListAPIView):
    serializer_class = MlmOrdersSerializers
    permission_classes = [Ismlm]

    def get_queryset(self):
        #user_token = str(self.request.headers['Authorization']).split('Token')[1].strip()
        
        #print(str(self.request.headers['Authorization']).split('Token')[1:2])
        #token_info = Token.objects.filter(key=user_token).first()
        return MlmProductsOrders.objects.filter(shopper_id=self.request.user.id, payment_status=True).all().order_by('id')






class carts_add(generics.CreateAPIView):
    serializer_class = MlmOrdersSerializers

    def post(self, request, *args, **kwargs):
        data = MlmOrdersSerializers(data=request.data)
        if data.is_valid():
            # user_token = str(self.request.headers['Authorization']).split('Token')[1].strip()
            # token_info = Token.objects.filter(key=user_token).first()
            cart = MlmProductsCarts.objects.filter(user_id=request.user.id).first()
            if cart is None:
                cart_create = MlmProductsCarts.objects.create(user_id=request.user.id)
            else: pass
            cart = MlmProductsCarts.objects.filter(user_id=request.user.id).first()
            product = MlmProducts.objects.filter(id=data.validated_data['product'].id).first()
            MlmProductsOrders.objects.create(shopper_id=request.user.id, title=product.title, count=data.validated_data['count'],description=product.descriptions,price=product.price,cart_id=cart.id,product_id=product.id)
            return Response({'message': 'اضافه شد'})
        else:
            return Response(data.errors)


class carts_remove(generics.CreateAPIView):
    serializer_class = MlmOrdersSerializers


    def post(self, request, *args, **kwargs):
        data = MlmOrdersSerializers(data=request.data)
        if data.is_valid():
            id = request.data.get('id',False)
            if id:
                # user_token = str(self.request.headers['Authorization']).split('Token')[1].strip()
                # token_info = Token.objects.filter(key=user_token).first()
                # cart = MlmProductsCarts.objects.filter(user_id=request.user.id).first()
                order = MlmProductsOrders.objects.filter(id=id, product_id=data.validated_data['product'].id,payment_status=False).first()
                if order is not None:
                    order.delete()
                    return Response({'message': 'حذف شد'})
                else:
                    return Response({'message': 'error'})
            else:
                return Response({'id': 'این فیلد الزامی است'})
        else:
            return Response(data.errors)


class carts_list(generics.ListAPIView):
    serializer_class = MlmOrdersSerializers

    def get_queryset(self):
        # user_token = str(self.request.headers['Authorization']).split('Token')[1].strip()
        # token_info = Token.objects.filter(key=user_token).first()

        return MlmProductsOrders.objects.filter(shopper_id=self.request.user.id, payment_status=False).all().order_by('id')




class products_list(generics.ListAPIView):
    serializer_class = MlmProductsSerializers

    def get_queryset(self):
        return MlmProducts.objects.filter(status=True).all()


class products_comments_list(generics.ListAPIView):
    serializer_class = MlmProductsCommentsSerializers

    def get_queryset(self):
        product_id = self.request.query_params.get('id',False)
        return MlmProductsComments.objects.filter(product_id=product_id, status=True).all()




class products_comments_add(generics.CreateAPIView):
    serializer_class = MlmProductsCommentsSerializers
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = MlmProductsComments(data=request.data)
        if data.is_valid():
            user_token = str(request.headers['Authorization']).split('Token')[1].strip()
            token_info = Token.objects.filter(key=user_token).first()
            productComments_check = MlmProductsComments.objects.filter(user_id=token_info.user.id,product_id=data.validated_data['product'].id,status=False).first()
            if productComments_check is None:
                MlmProductsComments(user_id=token_info.user.id, product_id=data.validated_data['product'].id,comment=data.validated_data['comment'], status=False).save()
                return Response({'message': 'دیدگاه ثبت شد'})
            else:
                return Response({"message": "کاربر قبلا برای این محصول دیدگاه ثبت کرده است"})
        else:
            return Response(data.errors)



class products_filter_maincategory_list(generics.ListAPIView):
    serializer_class = MlmProductsSerializers

    def get_queryset(self):
        id = self.request.query_params.get('id', False)
        return MlmProducts.objects.filter(maincategories__id=id, status=True).all()



class product_details(generics.ListAPIView):
    serializer_class = MlmProductsSerializers

    def get_queryset(self):

        id = self.kwargs['id']
        return MlmProducts.objects.filter(id=id)



@api_view()
def MainCat(request):

    mainCat = MlmProductMainCategories.objects.all()
    mainCatL = []

    if mainCat:
        for i in mainCat:
            mainCatL.append([{'name': i.name, 'id': i.id}])

    return Response(mainCatL)

@api_view()
def SubCat1(request, id):

    subCat1 = MlmProductSubCategories_1.objects.filter(id=id).first()
    subCat1L = []

    if subCat1:
        SubCat1 = subCat1.sub_categories2.all()

        for i in SubCat1:
            subCat1L.append({'name': i.name, 'id': i.id})

    return Response(subCat1L)


@api_view()
def SubCat2(request, id):
    subCat2 = MlmProductSubCategories_2.objects.filter(id=id).first()
    subCat2L = []

    if subCat2:
        SubCat2 = subCat2.sub_categories2.all()

        for i in SubCat2:
            subCat2L.append({'name': i.name, 'id': i.id})

    return Response(subCat2L)

