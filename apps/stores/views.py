from rest_framework import generics
from .models import Inventory
from .serializers import InventorySerializer
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class InventoryListView(generics.ListAPIView):
    serializer_class = InventorySerializer

    def get_queryset(self):
        store_id = self.kwargs['store_id']
        return Inventory.objects.filter(store_id=store_id).select_related(
            'product', 'product__category'
        ).order_by('product__title')

    @method_decorator(cache_page(60 * 15)) # Cache for 15 minutes
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
