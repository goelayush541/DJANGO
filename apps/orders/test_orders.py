import pytest
from django.urls import reverse
from rest_framework import status
from products.models import Category, Product
from stores.models import Store, Inventory
from orders.models import Order

from rest_framework.test import APIClient
import json

@pytest.mark.django_db
class TestOrderAPI:
    def setup_method(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Electronics")
        self.product = Product.objects.create(
            title="Laptop", price=1000, category=self.category
        )
        self.store = Store.objects.create(name="Tech Store", location="New York")
        self.inventory = Inventory.objects.create(
            store=self.store, product=self.product, quantity=10
        )
        self.url = reverse('order-create')

    def test_create_order_success(self):
        data = {
            "store_id": self.store.id,
            "items": [
                {"product_id": self.product.id, "quantity_requested": 5}
            ]
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['status'] == 'CONFIRMED'
        
        # Check stock deduction
        self.inventory.refresh_from_db()
        assert self.inventory.quantity == 5

    def test_create_order_insufficient_stock(self):
        data = {
            "store_id": self.store.id,
            "items": [
                {"product_id": self.product.id, "quantity_requested": 15}
            ]
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'REJECTED'
        
        # Check stock not deducted
        self.inventory.refresh_from_db()
        assert self.inventory.quantity == 10

    def test_create_order_atomic_rollback(self):
        # Create another product with limited stock
        product2 = Product.objects.create(
            title="Mouse", price=20, category=self.category
        )
        Inventory.objects.create(store=self.store, product=product2, quantity=2)
        
        data = {
            "store_id": self.store.id,
            "items": [
                {"product_id": self.product.id, "quantity_requested": 5}, # Sufficient
                {"product_id": product2.id, "quantity_requested": 5}     # Insufficient
            ]
        }
        response = self.client.post(self.url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'REJECTED'
        
        # Verify first item's stock was NOT deducted due to atomicity (even though it was sufficient)
        self.inventory.refresh_from_db()
        assert self.inventory.quantity == 10
