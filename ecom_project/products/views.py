from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView , ListAPIView
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer 
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from products.filters import ProductFilter
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



# class ProductVariationListView(ListAPIView):
#     serializer_class = ProductVariantSerializer

#     def get_queryset(self):
#         return ProductVariant.objects.filter(product__id=self.kwargs['product_id'])
    
