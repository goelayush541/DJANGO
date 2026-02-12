from django.db import models
from stores.models import Store
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('REJECTED', 'Rejected'),
    ]
    
    store = models.ForeignKey(Store, related_name='orders', on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status} ({self.store.name})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_requested = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity_requested}x {self.product.title} in Order #{self.order.id}"
