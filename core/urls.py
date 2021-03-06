from django.urls import path
from .views import (
    ItemDetailView,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    PaymentVerify,
    UserDetailView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    AddCouponView,
    RequestRefundView,
    # UserCreate,
    AddressRegView
)

app_name = 'core'

urlpatterns = [
    path('', HomeView, name='home'),
    path('checkout/', CheckoutView, name='checkout'),
    path('user-detail/', UserDetailView.as_view(), name='user-detail'),
    path('order-summary/', OrderSummaryView, name='order-summary'),
    path('product/<slug>/', ItemDetailView, name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('add-coupon/', AddCouponView, name='add-coupon'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart,
         name='remove-sinClock.schedule_once(self.add_rv)gle-item-from-cart'),
    # path('register/', UserCreate.as_view(), name='register-new-user'),
    path('payment/<payment_option>/', PaymentView, name='payment'),
    path('payment/verify/<payment_ref>/', PaymentVerify, name='payment-verify'),
    path('request-refund/', RequestRefundView, name='request-refund'),
    path('address/', AddressRegView.as_view(), name='address-page')
]
