from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView , ListAPIView
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from products.filters import ProductFilter
from decimal import Decimal
from django.db.models import Sum
# Create your views here.


class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    filterset_class = ProductFilter 

    # allow searching on "name" (partial, case‑insensitive)
    search_fields = ['name','description']


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'
    
class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class DiscountedProductListView(ListAPIView):
    queryset = Product.objects.exclude(discount_price__isnull=True).exclude(discount_price=Decimal('0.00'))
    serializer_class = ProductSerializer

class NewProductListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        from django.utils import timezone
        from datetime import timedelta
        days = 7  # Same as above
        cutoff = timezone.now() - timedelta(days=days)
        return Product.objects.filter(created_at__gte=cutoff)

class TopOrderedProductsView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.order_by('-sold')[:10]

# class ProductVariationListView(ListAPIView):
#     serializer_class = ProductVariantSerializer

#     def get_queryset(self):
#         return ProductVariant.objects.filter(product__id=self.kwargs['product_id'])
    
