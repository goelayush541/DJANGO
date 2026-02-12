from django.db import models
from products.models import Product

class Store(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    store = models.ForeignKey(Store, related_name='inventory', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='inventory', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('store', 'product')
        verbose_name_plural = "Inventories"

    def __str__(self):
        return f"{self.store.name} - {self.product.title}: {self.quantity}"
