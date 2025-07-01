# views.py
from decimal import Decimal
from datetime import timedelta

from django.utils import timezone

from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import (
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Product, Category
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    CategorySerializer,
)
from products.filters import ProductFilter


class StandardPagination(PageNumberPagination):
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductListView(ListAPIView):
    """
    /api/products/list
    supports ?page, ?page_size, ?search, ?category, plus any ProductFilter fields
    """
    serializer_class = ProductListSerializer
    pagination_class = StandardPagination
    filter_backends  = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class  = ProductFilter
    search_fields    = ['name', 'description']

    def get_queryset(self):
        return (
            Product.objects
                   .select_related('category')
                   .prefetch_related('images', 'variants')
                   .all()
        )


class DiscountedProductListView(ListAPIView):
    """
    /api/products/discounted
    """
    serializer_class = ProductListSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return (
            Product.objects
                   .exclude(discount_price__isnull=True)
                   .exclude(discount_price=Decimal('0.00'))
                   .select_related('category')
                   .prefetch_related('images', 'variants')
        )


class NewProductListView(ListAPIView):
    """
    /api/products/new-products
    """
    serializer_class = ProductListSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        cutoff = timezone.now() - timedelta(days=7)
        return (
            Product.objects
                   .filter(created_at__gte=cutoff)
                   .select_related('category')
                   .prefetch_related('images', 'variants')
        )


class TopOrderedProductsView(ListAPIView):
    """
    /api/products/top-ordered
    """
    serializer_class = ProductListSerializer
    pagination_class = StandardPagination

    def get_queryset(self):
        return (
            Product.objects
                   .order_by('-sold')
                   .select_related('category')
                   .prefetch_related('images', 'variants')
        )


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    """
    /api/products/<id>/
    """
    queryset         = (
        Product.objects
               .select_related('category')
               .prefetch_related('images', 'variants')
    )
    serializer_class = ProductDetailSerializer
    lookup_field     = 'id'


class CategoryListView(ListAPIView):
    """
    /api/products/category/list
    """
    serializer_class = CategorySerializer
    pagination_class = None  # return all categories without pagination

    def list(self, request, *args, **kwargs):
        qs = Category.objects.all()
        data = self.serializer_class(qs, many=True).data
        return Response(data)


class HomeDiscountedProductsView(ListAPIView):
    serializer_class = ProductListSerializer
    pagination_class = None  # No pagination, just top 4

    def get_queryset(self):
        return (
            Product.objects
            .exclude(discount_price__isnull=True)
            .exclude(discount_price=0)
            .order_by('-discount_price')[:4]
            .select_related('category')
            .prefetch_related('images', 'variants')
        )


class HomeNewProductsView(ListAPIView):
    serializer_class = ProductListSerializer
    pagination_class = None

    def get_queryset(self):
        cutoff = timezone.now() - timedelta(days=7)
        return (
            Product.objects
            .filter(created_at__gte=cutoff)
            .order_by('-created_at')[:4]
            .select_related('category')
            .prefetch_related('images', 'variants')
        )


class HomeTopOrderedProductsView(ListAPIView):
    serializer_class = ProductListSerializer
    pagination_class = None

    def get_queryset(self):
        return (
            Product.objects
            .order_by('-sold')[:4]
            .select_related('category')
            .prefetch_related('images', 'variants')
        )
