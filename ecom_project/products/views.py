from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.settings import api_settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
from django.core.cache import cache

from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from products.filters import ProductFilter
from products.cache import build_cache_key, get_or_set_cache
from .pagination import ProductListPagination


class ProductListView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    pagination_class = ProductListPagination

    def list(self, request, *args, **kwargs):
        page_num = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', api_settings.PAGE_SIZE)
        search = request.query_params.get('search', '')
        filters_qs = '&'.join([f"{k}={v}" for k, v in request.query_params.items() if k != 'page'])

        cache_key = build_cache_key("products:list", page=page_num, page_size=page_size, search=search, filters=filters_qs)

        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
        except Exception:
            cached_data = None  # Fail-safe fallback

        response = super().list(request, *args, **kwargs)

        try:
            cache.set(cache_key, response.data, timeout=300)
        except Exception:
            pass  # Don't crash if caching fails

        return response


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'id'


class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        cache_key = build_cache_key("categories:all")

        try:
            return Response(get_or_set_cache(cache_key, lambda: self.serializer_class(self.get_queryset(), many=True).data))
        except Exception:
            return Response(self.serializer_class(self.get_queryset(), many=True).data)


class DiscountedProductListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.exclude(discount_price__isnull=True).exclude(discount_price=Decimal('0.00'))

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = PageNumberPagination()

        page_size = request.query_params.get('page_size')
        paginator.page_size = int(page_size) if page_size else api_settings.PAGE_SIZE

        page = paginator.paginate_queryset(queryset, request)
        if page is None:
            return Response({"results": [], "count": 0})

        page_num = request.query_params.get('page', 1)
        cache_key = build_cache_key("products:discounted", page=page_num, page_size=paginator.page_size)

        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
        except Exception:
            cached_data = None

        response = paginator.get_paginated_response(self.serializer_class(page, many=True).data)

        try:
            cache.set(cache_key, response.data, timeout=300)
        except Exception:
            pass

        return response


class NewProductListView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        cutoff = timezone.now() - timedelta(days=7)
        return Product.objects.filter(created_at__gte=cutoff)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = PageNumberPagination()

        page_size = request.query_params.get('page_size')
        paginator.page_size = int(page_size) if page_size else api_settings.PAGE_SIZE

        page = paginator.paginate_queryset(queryset, request)
        if page is None:
            return Response({"results": [], "count": 0})

        page_num = request.query_params.get('page', 1)
        cache_key = build_cache_key("products:new", page=page_num, page_size=paginator.page_size)

        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
        except Exception:
            cached_data = None

        response = paginator.get_paginated_response(self.serializer_class(page, many=True).data)

        try:
            cache.set(cache_key, response.data, timeout=300)
        except Exception:
            pass

        return response


class TopOrderedProductsView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.order_by('-sold')

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = PageNumberPagination()

        page_size = request.query_params.get('page_size')
        paginator.page_size = int(page_size) if page_size else api_settings.PAGE_SIZE

        page = paginator.paginate_queryset(queryset, request)
        if page is None:
            return Response({"results": [], "count": 0})

        page_num = request.query_params.get('page', 1)
        cache_key = build_cache_key("products:top", page=page_num, page_size=paginator.page_size)

        try:
            cached_data = cache.get(cache_key)
            if cached_data is not None:
                return Response(cached_data)
        except Exception:
            cached_data = None

        response = paginator.get_paginated_response(self.serializer_class(page, many=True).data)

        try:
            cache.set(cache_key, response.data, timeout=300)
        except Exception:
            pass

        return response
