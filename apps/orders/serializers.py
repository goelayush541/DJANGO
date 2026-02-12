from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    
    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity_requested']

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    store_id = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ['store_id', 'items']

class OrderListSerializer(serializers.ModelSerializer):
    total_items = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'created_at', 'total_items']
