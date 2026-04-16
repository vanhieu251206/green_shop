from django.shortcuts import render, get_object_or_404
from .models import Product


def product_list(request):
    products = Product.objects.all()

    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(name__icontains=q)

    return render(request, 'products/list.html', {
        'products': products,
        'q': q,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/detail.html', {
        'product': product
    })