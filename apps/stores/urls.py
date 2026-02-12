from django.urls import path
from .views import InventoryListView
from orders.views import OrderListView

urlpatterns = [
    path('stores/<int:store_id>/inventory/', InventoryListView.as_view(), name='inventory-list'),
    path('stores/<int:store_id>/orders/', OrderListView.as_view(), name='order-list'),
]
