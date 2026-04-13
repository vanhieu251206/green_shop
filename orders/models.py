from django.db import models


class Order(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"Đơn hàng #{self.id} - {self.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=0)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"