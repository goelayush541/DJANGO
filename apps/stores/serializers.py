from rest_framework import serializers
from .models import Store, Inventory
from products.serializers import ProductSerializer

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'location']

class InventorySerializer(serializers.ModelSerializer):
    product_title = serializers.ReadOnlyField(source='product.title')
    price = serializers.ReadOnlyField(source='product.price')
    category_name = serializers.ReadOnlyField(source='product.category.name')

    class Meta:
        model = Inventory
        fields = ['id', 'product_title', 'price', 'category_name', 'quantity']
