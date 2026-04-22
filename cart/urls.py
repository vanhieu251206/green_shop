from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('increase/<int:product_id>/', views.cart_increase, name='cart_increase'),
    path('decrease/<int:product_id>/', views.cart_decrease, name='cart_decrease'),

    path('vnpay/payment/', views.vnpay_payment, name='vnpay_payment'),
    path('vnpay/return/', views.vnpay_return, name='vnpay_return'),
    path('vnpay/ipn/', views.vnpay_ipn, name='vnpay_ipn'),
]