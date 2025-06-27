# orders/models.py

from decimal import Decimal
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from products.models import Product
from django.core.exceptions import ValidationError
from django.db.models import Sum

CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Rejected', 'Rejected'),
)

class Wilaya(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)  # Added db_index
    domicile_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bureau_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    class Meta:
        ordering = ["name"]
        verbose_name = "Wilaya"
        verbose_name_plural = "Wilayas"

    def __str__(self):
        return self.name
    
class Commune(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)  # Added db_index
    wilaya = models.ForeignKey(Wilaya, related_name='communes', on_delete=models.CASCADE, db_index=True)  # Added db_index

    class Meta:
        unique_together = ["wilaya", "name"]
        ordering = ["name"]
        verbose_name = "Commune"
        verbose_name_plural = "Communes"

    def __str__(self):
        return self.name

class Order(models.Model):
    costumer_name = models.CharField(max_length=100, db_index=True)  # Added db_index
    costumer_phone = PhoneNumberField(region="DZ", db_index=True)    # Added db_index
    order_date = models.DateTimeField(auto_now_add=True, db_index=True)  # Added db_index
    order_status = models.CharField(max_length=50, default="Pending", choices=CHOICES, db_index=True)  # Added db_index
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_type = models.CharField(max_length=50, default="Bureau", choices=(("A Domicile", "A Domicile"), ("Bureau", "Bureau")))
    delivery_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wilaya = models.CharField(max_length=100, db_index=True)  # Added db_index
    commune = models.CharField(max_length=100, blank=True, null=True, db_index=True)  # Added db_index

    def __str__(self):
        return f"Order {self.id} - {self.costumer_name} - {self.order_status}"

    def update_total(self):
        """
        Recalculate total_amount by summing (discounted price or price) * quantity for all line items.
        Call this *after* items have been created or modified.
        """
        # Use select_related to optimize DB queries
        items = self.items.select_related('product').all()
        new_total = sum(
            (
                (item.product.discount_price if item.product and item.product.discount_price not in [None, Decimal('0.00'), 0] else item.product.price)
                * item.quantity
            )
            for item in items if item.product
        ) + (self.delivery_fees or 0)
        self.total_amount = new_total
        self.save(update_fields=["total_amount"])
        
    def clean(self):
        super().clean()
        # only when editing an existing Order…
        if self.pk:
            old_status = Order.objects.filter(pk=self.pk).values_list("order_status", flat=True).first()
            # …and only when flipping Pending→Accepted…
            if old_status == "Pending" and self.order_status == "Accepted":
                # Use select_related to optimize DB queries
                for item in self.items.select_related('product').all():
                    if item.quantity > item.product.stock:
                        # attach to the order_status field
                        raise ValidationError({
                            "order_status": (
                                f"Not enough stock for “{item.product}” – "
                                f"requested {item.quantity}, available {item.product.stock}."
                            )
                        })
                    
    def save(self, *args, **kwargs):
        self.full_clean()
        is_new = self.pk is None
        previous_status = None

        if not is_new:
            previous_status = (
                Order.objects
                .filter(pk=self.pk)
                .values_list("order_status", flat=True)
                .first()
            )

        super().save(*args, **kwargs)

        # only once, when Pending→Accepted:
        if (not is_new) and (previous_status == "Pending") and (self.order_status == "Accepted"):
            # Use select_related to optimize DB queries
            for item in self.items.select_related('product').all():
                item.update_stock()
                if item.product:
                    item.product.sold += item.quantity
                    item.product.save(update_fields=['sold'])
        # self.update_total()

    def bulk_add_items(self, items_data):
        """
        Efficiently add multiple OrderItems to this order using bulk_create.
        items_data: list of dicts, each with keys: product, quantity
        Example:
            [
                {"product": product1, "quantity": 2},
                {"product": product2, "quantity": 1},
            ]
        """
        order_items = []
        for data in items_data:
            product = data["product"]
            quantity = data["quantity"]
            # Calculate price as in OrderItem.save()
            if product.discount_price not in [None, Decimal('0.00'), 0]:
                unit_price = product.discount_price
            else:
                unit_price = product.price
            price = unit_price * quantity
            order_items.append(OrderItem(
                order=self,
                product=product,
                quantity=quantity,
                price=price
            ))
        OrderItem.objects.bulk_create(order_items)
        # Optionally update total after bulk create
        self.update_total()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, db_index=True)  # Added db_index
    product = models.ForeignKey(Product, on_delete=models.PROTECT, blank=True, null=True, db_index=True)  # Added db_index
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clean(self):
        if self.product and self.quantity > self.product.stock:
            raise ValidationError(
                f"Only {self.product.stock} units available for {self.product}. You requested {self.quantity}."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.product and self.product.discount_price not in [None, Decimal('0.00'), 0]:
            unit_price = self.product.discount_price
        elif self.product:
            unit_price = self.product.price
        else:
            self.price = 0
            unit_price = 0
        self.price = unit_price * self.quantity
        super().save(*args, **kwargs)
        # Update the order's total amount whenever an item is saved
        # if self.order:
        #     self.order.update_total()

    def update_stock(self):
        """
        Subtract this line’s quantity from the variant’s stock.
        Called by Order.save() only once, when status flips to 'Accepted'.
        """
        # Optionally guard against negative stock:
        if self.quantity > self.product.stock:
            raise ValueError("Insufficient stock to fulfill this order item.")

        self.product.stock -= self.quantity
        self.product.save(update_fields=['stock'])

    def __str__(self):
        return f"{self.quantity} x {self.product} for Order {self.order.id}"
