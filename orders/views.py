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
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        note = request.POST.get('note')

        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            full_name=full_name,
            phone=phone,
            address=address,
            note=note,
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