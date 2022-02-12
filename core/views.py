import random
import string

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
from .serializers import UserSerializer, ItemSerializer, OrderSerializer, AddressSerializer
from . import models
from rest_framework import generics, viewsets
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny


# Create your views here.



def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

class UserCreate(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )

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
            return Response()
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return Response()
    else:
        ordered_date = timezone.now()
        order = models.Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return Response()




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
            return Response()
        else:
            messages.info(request, "This item was not in your cart")
            return Response()
    else:
        messages.info(request, "You do not have an active order")
        return Response()


def PaymentView():
    pass
def AddCouponView():
    pass
def RequestRefundView():
    pass