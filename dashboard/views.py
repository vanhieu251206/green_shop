from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from products.models import Product


@staff_member_required(login_url='/admin/login/')
def dashboard_home(request):
    products = Product.objects.all().order_by('-id')[:5]
    total_products = Product.objects.count()

    return render(request, 'dashboard/home.html', {
        'total_products': total_products,
        'recent_products': products,
    })