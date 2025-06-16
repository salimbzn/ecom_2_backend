from django.db import models

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
    category = models.ForeignKey('Category', related_name='products', on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.name
    
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to=upload_to_variant)
    def __str__(self):
        return f"{self.product.name} - {self.name or None} {self.color or 'No Color'} {self.size or 'No Size'}"

    def get_product_name(self):
        return self.name or self.product.name

    def get_product_price(self):
        return self.price if self.price is not None else self.product.price

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.product.name
        if self.price is None:
            self.price = self.product.price

        super().save(*args, **kwargs)


# class ProductImage(models.Model):
#     product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
#     image = models.ImageField(upload_to='product_images/')
#     # is_primary = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.product.name}"
    

class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
    def __str__(self):
        return self.name