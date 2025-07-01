# views.py
from decimal import Decimal
from datetime import timedelta

from django.utils import timezone
from django.core.cache import cache

from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Product, Category
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    CategorySerializer,
)
from products.filters import ProductFilter
from products.cache import build_cache_key


class CachedListMixin:
    """
    Mixin to paginate, cache and respond consistently.
    Expects:
      - self.queryset
      - self.serializer_class
      - self.cache_prefix (override in subclasses)
    """
    cache_prefix = None   # e.g. "products:list"

    def list(self, request, *args, **kwargs):
        page_num   = request.query_params.get('page', 1)
        page_size  = request.query_params.get('page_size', api_settings.PAGE_SIZE)
        params     = request.query_params.dict()
        params.pop('page', None)

        cache_key = build_cache_key(
            self.cache_prefix,
            page=page_num,
            page_size=page_size,
            **params
        )

        # Try cache
        data = cache.get(cache_key)
        if data is not None:
            return Response(data)

        # Paginate & serialize
        paginator = PageNumberPagination()
        paginator.page_size = int(page_size)

        qs = self.get_queryset()
        page = paginator.paginate_queryset(qs, request)
        serializer = self.serializer_class(page, many=True)
        response = paginator.get_paginated_response(serializer.data)

        # Store in cache
        try:
            cache.set(cache_key, response.data, timeout=300)
        except Exception:
            pass

        return response


class ProductListView(CachedListMixin, ListAPIView):
    """
    /api/products/list
    supports ?page, ?page_size, ?search, ?category, plus any ProductFilter fields
    """
    cache_prefix     = "products:list"
    serializer_class = ProductListSerializer
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


class DiscountedProductListView(CachedListMixin, ListAPIView):
    """
    /api/products/discounted
    """
    cache_prefix     = "products:discounted"
    serializer_class = ProductListSerializer

    def get_queryset(self):
        return (
            Product.objects
                   .exclude(discount_price__isnull=True)
                   .exclude(discount_price=Decimal('0.00'))
                   .select_related('category')
                   .prefetch_related('images', 'variants')
        )


class NewProductListView(CachedListMixin, ListAPIView):
    """
    /api/products/new-products
    """
    cache_prefix     = "products:new"
    serializer_class = ProductListSerializer

    def get_queryset(self):
        cutoff = timezone.now() - timedelta(days=7)
        return (
            Product.objects
                   .filter(created_at__gte=cutoff)
                   .select_related('category')
                   .prefetch_related('images', 'variants')
        )


class TopOrderedProductsView(CachedListMixin, ListAPIView):
    """
    /api/products/top-ordered
    """
    cache_prefix     = "products:top"
    serializer_class = ProductListSerializer

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

    def list(self, request, *args, **kwargs):
        cache_key = build_cache_key("categories:all")

        data = cache.get(cache_key)
        if data is None:
            qs   = Category.objects.all()
            data = self.serializer_class(qs, many=True).data
            try:
                cache.set(cache_key, data, timeout=300)
            except Exception:
                pass

        return Response(data)
