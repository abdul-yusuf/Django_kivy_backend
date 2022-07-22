from lib2to3 import refactor
from os import access
import random
import string
from weakref import ref

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from django.views import View
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer, ItemSerializer, OrderSerializer, AddressSerializer, LikesSerializer
from . import models
from rest_framework import generics, viewsets
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from django.conf import settings

from core import serializers

# Create your views here.

# from django.contrib.auth import get_user_model
# User = get_user_model()

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

# class UserCreate(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = (AllowAny, )

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = models.Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = ['pk']
    # Response()

    # def get(self, request, format):
    #     """get method"""

    # def post(self, request, format):
    #     """post method"""


@api_view(['GET'])
def ItemDetailView(request, slug):
    item = models.Item.objects.filter(slug=slug)
    serializer = ItemSerializer(item, many=True)
    print(slug)
    return Response(serializer.data)

def CheckoutView():
    pass

# @api_view(['GET'])
class AddressRegView(generics.CreateAPIView):
    queryset = models.Address
    serializer_class = AddressSerializer
    # return Response(serializer.data)


@api_view(['GET'])
def HomeView(request):
    item = models.Item.objects.all()
    serializer = ItemSerializer(item, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@login_required
def OrderSummaryView(request):
    try:
        order = models.Order.objects.get(user=request.user, ordered=False)
        serializer = OrderSerializer(order, many=False)
        return Response(serializer.data)

    except ObjectDoesNotExist:
        messages.warning(request, "You do not have an active order")
        return redirect("/")


@api_view(['GET'])
@login_required
def FavouritesView(request):
    items = models.Likes.objects.get(user=request.user)
    serializer = LikesSerializer(items, many=True)
    return Response(serializer.data)

# @api_view(['GET'])
# @login_required
# def UserDetailView(request):
#     items = models.MyUser.objects.get(user=request.user)
#     serializer = UserSerializer(items, many=False)
#     return Response(serializer.data)

@api_view(['GET'])
@login_required
def add_to_cart(request, slug):
    print(request.user)
    item = get_object_or_404(models.Item, slug=slug)
    order_item, created = models.OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    # print(slug)
    order_qs = models.Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return Response('Item Updated')

        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return Response('Item Added Succesfull')
    else:
        ordered_date = timezone.now()
        order = models.Order.objects.create(
            user=request.user, ordered_date=ordered_date, ref_code=create_ref_code())
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return Response('Item Added Succesfull')




def remove_from_cart():
    pass


# @api_view(['GET','POST'])
@api_view(['GET'])
@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(models.Item, slug=slug)
    order_qs = models.Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        print(order)
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = models.OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return Response("This item quantity was updated.")
        else:
            messages.info(request, "This item was not in your cart")
            return Response("This item was not in your cart")
    else:
        messages.info(request, "You do not have an active order")
        return Response("You do not have an active order")

@api_view(['GET','POST'])
@login_required
def PaymentView(request, payment_option):

    # print(request.user)
    order_qs = models.Order.objects.filter(
        user=request.user,
        ordered=False,
        ref_code=payment_option
    )
    
    
    link='not created'
    if order_qs.exists():
        totalx = int(order_qs[0].total)*100
        ref_no = payment_option
        if request.user.is_authenticated:
            total = totalx

            paystack_secret_key = settings.PAYSTACK_SECRET_KEY
            paystack = Paystack(secret_key=paystack_secret_key)
            network = True
            try:
                response = Transaction.initialize(reference=ref_no,
                                        # authorization_code='authorization_code',
                                        email=request.user.username,
                                        amount=total)
                
            except:
                response={
                    'status': True,
                    'message': 'TRuely connected',
                    'data': {
                        'authorization_url': 'ayugklia.akjak.com',
                        'access_code': 'alkjadfl',
                        'reference': payment_option
                    }
                }
                # response["status"]==True
                # response["status"]==True
                network =False
                network =True
                print("test error")

            # print(response)
            # to use payment url "data['payment_link']['data']['authorization_url']"
            if network == True and response["status"]==True:
                massage = response['message']
                url = response['data']['authorization_url']
                access_code = response['data']['access_code']
                reference = response['data']['reference']

                time = timezone.now()
                payment = models.Payment.objects.get_or_create(
                    ref_id=reference,
                    user=request.user,
                    authorization = url,
                    amount=float(totalx/100),
                    timestamp=time
                )
                print(order_qs[0].payment)
                print(payment)
                order_qs[0].payment = payment
                order_qs[0].save()
                # except:
                #     massage = 'massage'
                #     response=''    
                #     print("test error")

            
            elif response['message'] == "Duplicate Transaction Reference":
                massage = response['message']
                ref_no = ref_no
                time = timezone.now()
                payment = models.Payment.objects.filter(
                    ref_id=payment_option,
                    # user=request.user,
                    # amount=float(totalx/100),
                    # timestamp=time
                )
                if payment.exists():
                    payment=payment[0]
                    response=payment.authorization



        else:
            response=""
            massage = "No Response"
            print('not authenticated')

    else:
        response = ""
        massage = "Order dose not exist"


    

    return Response({"payment_link":response,"massage":massage})

@api_view()
def PaymentVerify(request, payment_ref):

    try:
        response = Transaction.verify(reference=payment_ref)
        print(response)
        try:
            status2 = response['data']['status'] 
        except UnboundLocalError as err:
            print(err)

    except:
        print('TimeoutError')
        response = {}
        response['status'] = False
    
    payment_data = models.Payment.objects.filter(
                # user=request.user,
                ref_id=payment_ref,
                # is_payed=False
            )
    print(payment_data[0].is_payed)
    status = response['status'] 
    if status == True:
        try:
            if status2 == 'success':
                payment_data = models.Payment.objects.filter(
                    # user=request.user,
                    ref_id=payment_ref,
                    is_payed=False
                )
                # print(payment_data)
            
                if payment_data.exists():
                    payment = payment_data[0]
                    time = timezone.now()
                    # if payment.is_payed == False:
                    payment.is_payed = True
                    payment.timestamp = time
                    payment.save()
                    
                    order = models.Order.objects.filter(
                        ref_code = payment_ref,
                        ordered = False
                    )
                    print(order[0].ordered)

                    order[0].ordered = True
                    order[0].save()
                    print(order[0].ordered)
                    print('Order successful')                
                # else:
                #     print('Already ordered')
                else:
                    print('Order Dose not exist')
            else:
                print('Order not successful')
        except:
            print('Error')

    return Response(response)

def AddCouponView():
    pass
def RequestRefundView():
    pass