from django.db import transaction
from django.db.models import Count
from rest_framework import generics, status, response
from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderListSerializer
from stores.models import Inventory, Store
from products.models import Product

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        store_id = serializer.validated_data['store_id']
        items_data = serializer.validated_data['items']
        
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return response.Response({"error": "Store not found"}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():
            # Create Order with PENDING status initially
            order = Order.objects.create(store=store, status='PENDING')
            
            insufficient_stock = False
            order_items = []
            
            for item in items_data:
                product_id = item['product_id']
                qty_requested = item['quantity_requested']
                
                try:
                    product = Product.objects.get(id=product_id)
                    inventory = Inventory.objects.select_for_update().get(store=store, product=product)
                    
                    if inventory.quantity < qty_requested:
                        insufficient_stock = True
                        break
                    
                    inventory.quantity -= qty_requested
                    inventory.save()
                    
                    order_items.append(OrderItem(order=order, product=product, quantity_requested=qty_requested))
                    
                except (Product.DoesNotExist, Inventory.DoesNotExist):
                    insufficient_stock = True
                    break

            if insufficient_stock:
                # If any product has insufficient stock, mark as REJECTED and do NOT save items or deduct stock
                # Note: The stock deduction above will be rolled back by transaction.atomic if we raise an exception
                # But the requirement says "No stock should be deducted" and create order with REJECTED status.
                # So we roll back the stock changes by NOT saving them if we detect failure.
                # Actually, select_for_update and then rolling back is better.
                transaction.set_rollback(True)
                
                # Create a NEW order with REJECTED status outside the rolled back transaction or just create it here and don't rollback?
                # Requirement: "Order must be created with REJECTED status". 
                # To guarantee no stock deducted, we use a second atomic block or a non-atomic creation.
                pass

        # If insufficient stock, created REJECTED order separately
        if insufficient_stock:
            order = Order.objects.create(store=store, status='REJECTED')
            return response.Response({
                "id": order.id,
                "status": order.status,
                "message": "Order rejected due to insufficient stock"
            }, status=status.HTTP_200_OK)

        # Otherwise, finalize the order
        OrderItem.objects.bulk_create(order_items)
        order.status = 'CONFIRMED'
        order.save()
        
        # Trigger Celery task
        from .tasks import send_order_confirmation
        send_order_confirmation.delay(order.id)

        return response.Response({
            "id": order.id,
            "status": order.status,
            "message": "Order confirmed successfully"
        }, status=status.HTTP_201_CREATED)

class OrderListView(generics.ListAPIView):
    serializer_class = OrderListSerializer

    def get_queryset(self):
        store_id = self.kwargs['store_id']
        return Order.objects.filter(store_id=store_id).annotate(
            total_items=Count('items')
        ).order_by('-created_at')
