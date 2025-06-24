
from django.urls import path,include
from .views import ProductListView, CategoryListView, ProductDetailView

urlpatterns = [
    path('list',ProductListView.as_view(), name='product-list-create'),
    path('category/list', CategoryListView.as_view(), name='category-list-create'),
    path('<int:id>/', ProductDetailView.as_view(), name='product-detail'),
]
