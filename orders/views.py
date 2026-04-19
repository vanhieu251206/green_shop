from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from cart.models import Cart

CART_SESSION_ID = 'cart'

@login_required(login_url='login')
def checkout(request):
    try:
        cart = request.user.cart
    except Cart.DoesNotExist:
        return redirect('cart_detail')

    cart_items = cart.items.select_related('product')

    if not cart_items.exists():
        return redirect('cart_detail')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_name=item.product.name,
                price=item.product.price,
                quantity=item.quantity,
            )

        cart.items.all().delete()

        return redirect('order_success')

    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

@login_required(login_url='login')
def order_success(request):
    return render(request, 'orders/success.html')