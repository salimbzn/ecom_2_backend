
from django.urls import path,include
from .views import ProductListView, CategoryListView

urlpatterns = [
    path('list',ProductListView.as_view(), name='product-list-create'),
    path('category/list', CategoryListView.as_view(), name='category-list-create'),
]
