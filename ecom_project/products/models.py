from django.db import models
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
# Create your models here.

def upload_to(instance, filename):
    return f'products/{instance.name}/{filename}'

def upload_to_variant(instance, filename):
    return f'products/{instance.product.name}/variants/{instance.name}/{filename}'

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to=upload_to)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey('Category', related_name='products', on_delete=models.CASCADE, blank=True, null=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2,blank=True, null=True)
    sold = models.PositiveIntegerField(default=0)
    @property
    def is_new(self):
        days = 7
        return self.created_at >= timezone.now() - timedelta(days=days)
    def get_discounted_price(self):
        if self.discount_price:
            return max(self.price - self.discount_price, Decimal('0.00'))


    def __str__(self):
        return self.name
    


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name
    








# class ProductVariant(models.Model):
#     product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
#     name = models.CharField(max_length=255, blank=True, null=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     stock = models.PositiveIntegerField(default=0)
#     color = models.CharField(max_length=50, blank=True, null=True)
#     size = models.CharField(max_length=50, blank=True, null=True)
#     image = models.ImageField(upload_to=upload_to_variant)
#     def __str__(self):
#         return f"{self.product.name} - {self.name or None} {self.color or 'No Color'} {self.size or 'No Size'}"

#     def get_product_name(self):
#         return self.name or self.product.name

#     def get_product_price(self):
#         return self.price if self.price is not None else self.product.price

#     def save(self, *args, **kwargs):
#         if not self.name:
#             self.name = self.product.name
#         if self.price is None:
#             self.price = self.product.price

#         super().save(*args, **kwargs)


# class ProductImage(models.Model):
#     product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='product_images/')
#     # is_primary = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.product.name}"
    