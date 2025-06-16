from django.core.management.base import BaseCommand
from products.models import Product, ProductVariant, Category

class Command(BaseCommand):
    help = "Seed the database with sample products and variants"

    def handle(self, *args, **kwargs):
        cat, _ = Category.objects.get_or_create(name="Electronics", defaults={"description": "Electronics category"})
        product, _ = Product.objects.get_or_create(
            name="Smartphone",
            defaults={
                "description": "A cool smartphone",
                "price": 500,
                "category": cat,
            }
        )
        ProductVariant.objects.get_or_create(
            product=product,
            name="Black",
            defaults={"price": 500, "stock": 10, "color": "#000000", "size": "Standard"}
        )
        ProductVariant.objects.get_or_create(
            product=product,
            name="White",
            defaults={"price": 500, "stock": 5, "color": "#FFFFFF", "size": "Standard"}
        )
        self.stdout.write(self.style.SUCCESS("Seeded products and variants."))