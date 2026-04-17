from django.shortcuts import render, get_object_or_404
from .models import Product


def product_list(request):
    products = Product.objects.all()

    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '').strip()

    if q:
        products = products.filter(name__icontains=q)

    if sort == 'name_asc':
        products = products.order_by('name')
    elif sort == 'name_desc':
        products = products.order_by('-name')
    elif sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-id')

    return render(request, 'products/list.html', {
        'products': products,
        'q': q,
        'sort': sort,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/detail.html', {
        'product': product
    })