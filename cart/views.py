from decimal import Decimal
from django.shortcuts import redirect, render, get_object_or_404
from products.models import Product

CART_SESSION_ID = 'cart'


def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get(CART_SESSION_ID, {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'image': product.image.url if product.image else '',
        }

    request.session[CART_SESSION_ID] = cart
    request.session.modified = True
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = request.session.get(CART_SESSION_ID, {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session[CART_SESSION_ID] = cart
        request.session.modified = True

    return redirect('cart_detail')


def cart_increase(request, product_id):
    cart = request.session.get(CART_SESSION_ID, {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
        request.session[CART_SESSION_ID] = cart
        request.session.modified = True

    return redirect('cart_detail')


def cart_decrease(request, product_id):
    cart = request.session.get(CART_SESSION_ID, {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] -= 1

        if cart[product_id_str]['quantity'] <= 0:
            del cart[product_id_str]

        request.session[CART_SESSION_ID] = cart
        request.session.modified = True

    return redirect('cart_detail')


def cart_detail(request):
    cart = request.session.get(CART_SESSION_ID, {})
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

    return render(request, 'cart/detail.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })