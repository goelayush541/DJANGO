from rest_framework import generics, response, status
from django.db.models import Q, F
from products.models import Product
from products.serializers import ProductSerializer
from stores.models import Inventory

class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        category = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        store_id = self.request.query_params.get('store_id')
        in_stock = self.request.query_params.get('in_stock')
        sort_by = self.request.query_params.get('sort', 'newest')

        queryset = Product.objects.all()

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(category__name__icontains=query)
            )

        if category:
            queryset = queryset.filter(category__name__iexact=category)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        if store_id:
            if in_stock == 'true':
                queryset = queryset.filter(inventory__store_id=store_id, inventory__quantity__gt=0)
            else:
                queryset = queryset.filter(inventory__store_id=store_id)
        
        # Sorting
        if sort_by == 'price_low':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_high':
            queryset = queryset.order_by('-price')
        elif sort_by == 'newest':
            queryset = queryset.order_by('-id')
        
        return queryset.distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        store_id = self.request.query_params.get('store_id')
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = serializer.data
            if store_id:
                for item in data:
                    inv = Inventory.objects.filter(product_id=item['id'], store_id=store_id).first()
                    item['inventory_quantity'] = inv.quantity if inv else 0
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        if store_id:
            for item in data:
                inv = Inventory.objects.filter(product_id=item['id'], store_id=store_id).first()
                item['inventory_quantity'] = inv.quantity if inv else 0
        return response.Response(data)

class AutocompleteView(generics.GenericAPIView):
    def get(self, request, *args, **kwargs):
        q = request.query_params.get('q', '')
        if len(q) < 3:
            return response.Response({"error": "Minimum 3 characters required"}, status=status.HTTP_400_BAD_REQUEST)

        # Prefix matches first, then general matches
        prefix_matches = Product.objects.filter(title__istartswith=q)[:10]
        titles = list(prefix_matches.values_list('title', flat=True))
        
        if len(titles) < 10:
            remaining = 10 - len(titles)
            other_matches = Product.objects.filter(title__icontains=q).exclude(id__in=prefix_matches)[:remaining]
            titles.extend(list(other_matches.values_list('title', flat=True)))

        return response.Response(titles[:10])
