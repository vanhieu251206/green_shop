from django.shortcuts import render
from products.models import Product
from django.contrib.auth.models import User
from accounts.decorators import admin_required


@admin_required
def admin_dashboard_view(request):
    products = Product.objects.all()[:5]

    context = {
        'products': products,
        'total_products': Product.objects.count(),
        'total_users': User.objects.count(),
    }

    return render(request, 'admin_panel/dashboard.html', context)