from django.core.management.base import BaseCommand
from django_seed import Seed
from products.models import Product, ProductVariant
from orders.models import Order, OrderItem, Wilaya, Commune

class Command(BaseCommand):
    help = "Seed orders and related models using django-seed"

    def handle(self, *args, **kwargs):
        seeder = Seed.seeder()

        # Seed Wilaya and Commune
        wilaya_pks = seeder.add_entity(Wilaya, 3, {
            'name': lambda x: seeder.faker.city()
        })
        commune_pks = seeder.add_entity(Commune, 5, {
            'wilaya': lambda x: Wilaya.objects.order_by('?').first(),
            'name': lambda x: seeder.faker.street_name()
        })

        # Seed Products and Variants
        product_pks = seeder.add_entity(Product, 5, {
            'name': lambda x: seeder.faker.word(),
            'description': lambda x: seeder.faker.text(),
            'price': lambda x: seeder.faker.random_int(min=100, max=1000)
        })
        variant_pks = seeder.add_entity(ProductVariant, 10, {
            'product': lambda x: Product.objects.order_by('?').first(),
            'name': lambda x: seeder.faker.color_name(),
            'price': lambda x: seeder.faker.random_int(min=100, max=1000),
            'stock': lambda x: seeder.faker.random_int(min=1, max=20)
        
        })
        # VALID_PREFIXES = ["5", "6", "7"]
        # Seed Orders
        order_pks = seeder.add_entity(Order, 30, {
            'costumer_name': lambda x: seeder.faker.name(),
            'costumer_phone': '+213799305654',
            'wilaya': lambda x: Wilaya.objects.order_by('?').first(),
            'commune': lambda x: Commune.objects.order_by('?').first(),
            'order_status': 'Pending',
            'total_amount': lambda x: seeder.faker.random_int(min=1000, max=5000),
            'delivery_type': lambda x: seeder.faker.random_element(elements=["A Domicile", "Bureau"]),
            'order_date': lambda x: seeder.faker.date_time_this_year()

        })

        inserted_pks = seeder.execute()

        # Seed OrderItems for each order
        for order_pk in inserted_pks[Order]:
            order = Order.objects.get(pk=order_pk)
            for _ in range(seeder.faker.random_int(min=1, max=3)):
                variant = ProductVariant.objects.order_by('?').first()
                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    quantity=seeder.faker.random_int(min=1, max=3),
                    price=variant.price
                )
            order.update_total()

        self.stdout.write(self.style.SUCCESS("Seeded orders, products, variants, wilayas, communes, and order items."))