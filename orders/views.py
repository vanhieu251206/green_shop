from decimal import Decimal
from django.shortcuts import render, redirect
from .models import Order, OrderItem
from django.contrib.auth.decorators import login_required

CART_SESSION_ID = 'cart'

@login_required(login_url='login')
def checkout(request):
    cart = request.session.get(CART_SESSION_ID, {})

    if not cart:
        return redirect('cart_detail')

    cart_items = []
    total_price = Decimal('0')

    for product_id, item in cart.items():
        item_total = Decimal(item['price']) * item['quantity']
        total_price += item_total

        cart_items.append({
            'product_id': int(product_id),
            'name': item['name'],
            'price': Decimal(item['price']),
            'quantity': item['quantity'],
            'image': item['image'],
            'total': item_total,
        })

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if name and phone and address:
            order = Order.objects.create(
                name=name,
                phone=phone,
                address=address,
                total_price=total_price,
            )

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product_name=item['name'],
                    price=item['price'],
                    quantity=item['quantity'],
                )

            request.session[CART_SESSION_ID] = {}
            request.session.modified = True

            return redirect('order_success')

        return render(request, 'orders/checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price,
            'error': 'Vui lòng nhập đầy đủ thông tin.',
            'old_name': name,
            'old_phone': phone,
            'old_address': address,
        })

    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

@login_required(login_url='login')
def order_success(request):
    return render(request, 'orders/success.html')