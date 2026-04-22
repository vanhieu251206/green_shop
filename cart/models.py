from django.db import models
from django.contrib.auth.models import User
from products.models import Product


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart - {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class PaymentTransaction(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Chờ thanh toán'),
        (STATUS_SUCCESS, 'Thanh toán thành công'),
        (STATUS_FAILED, 'Thanh toán thất bại'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_transactions')
    order_ref = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=15, decimal_places=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    order_info = models.CharField(max_length=255, blank=True)
    response_code = models.CharField(max_length=10, blank=True)
    transaction_no = models.CharField(max_length=50, blank=True)
    bank_code = models.CharField(max_length=50, blank=True)
    bank_tran_no = models.CharField(max_length=100, blank=True)
    pay_date = models.CharField(max_length=30, blank=True)

    raw_response = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_ref} - {self.user.username} - {self.status}"