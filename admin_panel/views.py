from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product, Category
from products.forms import ProductForm
from accounts.decorators import admin_required
from django.contrib.auth.models import User


@admin_required
def admin_dashboard_view(request):
    context = {
        'total_products': Product.objects.count(),
        'total_users': User.objects.count(),
        'total_featured': Product.objects.filter(is_featured=True).count(),
        'total_flash_sale': Product.objects.filter(is_flash_sale=True).count(),
    }
    return render(request, 'admin_panel/dashboard.html', context)


@admin_required
def admin_product_list(request):
    products = Product.objects.all().order_by('-id')

    return render(request, 'admin_panel/products_list.html', {
        'products': products
    })


@admin_required
def admin_product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        form.save()
        return redirect('admin_product_list')

    return render(request, 'admin_panel/product_form.html', {
        'form': form,
        'title': 'Thêm sản phẩm'
    })


@admin_required
def admin_product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    form = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if form.is_valid():
        form.save()
        return redirect('admin_product_list')

    return render(request, 'admin_panel/product_form.html', {
        'form': form,
        'title': 'Sửa sản phẩm'
    })


@admin_required
def admin_product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        product.delete()
        return redirect('admin_product_list')

    return render(request, 'admin_panel/product_delete.html', {
        'product': product
    })

@admin_required
def admin_category_list(request):
    categories = Category.objects.all().order_by('-id')
    return render(request, 'admin_panel/categories_list.html', {
        'categories': categories
    })


@admin_required
def admin_category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Category.objects.create(name=name)
    return redirect('admin_category_list')


@admin_required
def admin_category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            category.name = name
            category.save()

    return redirect('admin_category_list')


@admin_required
def admin_category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        category.delete()

    return redirect('admin_category_list')