from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView , ListAPIView
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer 
# Create your views here.


class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

# class ProductVariationListView(ListAPIView):
#     serializer_class = ProductVariantSerializer

#     def get_queryset(self):
#         return ProductVariant.objects.filter(product__id=self.kwargs['product_id'])
    

class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer