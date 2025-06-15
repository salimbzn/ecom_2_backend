
from django.urls import path,include
from .views import ProductListView, ProductVariationListView, CategoryListView

urlpatterns = [
    path('list',ProductListView.as_view(), name='product-list-create'),
    path('<int:product_id>/list', ProductVariationListView.as_view(), name='product-variation-list-create'),
    path('category/list', CategoryListView.as_view(), name='category-list-create'),
]
