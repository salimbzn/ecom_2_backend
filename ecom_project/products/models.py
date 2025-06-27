from django.db import models
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import re

# Utility to clean names for file paths
def clean_name(name):
    # Replace spaces with underscores and remove invalid characters
    name = name.strip().replace(' ', '_')
    return re.sub(r'[^a-zA-Z0-9_-]', '', name)

def upload_to(instance, filename):
    base_name = clean_name(instance.name)
    return f'products/{base_name}/{filename}'

def upload_category_image(instance, filename):
    base_name = clean_name(instance.name)
    return f'categories/{base_name}/{filename}'

class Category(models.Model):
    name = models.CharField(max_length=255, db_index=True, unique=True)  # Add db_index and unique for faster lookups
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=upload_category_image, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Add db_index for filtering/sorting
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)  # Add db_index for search/filter
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  # Add db_index for "new" queries
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=upload_to)
    color = models.CharField(max_length=50, blank=True, null=True, db_index=True)  # Add db_index for filtering
    size = models.CharField(max_length=50, blank=True, null=True, db_index=True)   # Add db_index for filtering
    stock = models.PositiveIntegerField(default=0, db_index=True)  # Add db_index for low-stock queries
    category = models.ForeignKey(
        Category,
        related_name='products',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        db_index=True
    )
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sold = models.PositiveIntegerField(default=0, db_index=True)  # Add db_index for best-seller queries

    @property
    def is_new(self):
        days = 7
        return self.created_at >= timezone.now() - timedelta(days=days)

    def get_discounted_price(self):
        if self.discount_price:
            return max(self.price - self.discount_price, Decimal('0.00'))

    def __str__(self):
        return self.name

    @classmethod
    def bulk_update_stock(cls, product_quantity_list):
        """
        Efficiently update stock for multiple products.
        product_quantity_list: list of (product_id, quantity_to_subtract)
        """
        products = cls.objects.filter(id__in=[pid for pid, _ in product_quantity_list])
        product_map = {p.id: p for p in products}
        for pid, qty in product_quantity_list:
            if pid in product_map:
                product_map[pid].stock = max(product_map[pid].stock - qty, 0)
        cls.objects.bulk_update(products, ['stock'])

# If you ever need to bulk create products, you can use Product.objects.bulk_create([...])
