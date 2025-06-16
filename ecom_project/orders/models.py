# orders/models.py

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from products.models import ProductVariant
from django.core.exceptions import ValidationError

CHOICES = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Rejected', 'Rejected'),
)

class Wilaya(models.Model):
    name = models.CharField(max_length=100, unique=True)
    domicile_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bureau_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    class Meta:
        ordering = ["name"]
        verbose_name = "Wilaya"
        verbose_name_plural = "Wilayas"

    def __str__(self):
        return self.name
    
class Commune(models.Model):
    name = models.CharField(max_length=100, unique=True)
    wilaya = models.ForeignKey(Wilaya, related_name='communes', on_delete=models.CASCADE)

    class Meta:
        unique_together = ["wilaya", "name"]
        ordering = ["name"]
        verbose_name = "Commune"
        verbose_name_plural = "Communes"

    def __str__(self):
        return self.name



class Order(models.Model):
    costumer_name = models.CharField(max_length=100)
    costumer_phone = PhoneNumberField(region="DZ")
    order_date = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=50, default="Pending", choices=CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_type = models.CharField(max_length=50, default="Bureau", choices=(("A Domicile", "A Domicile"), ("Bureau", "Bureau")))
    wilaya = models.ForeignKey(Wilaya, on_delete=models.PROTECT)
    commune = models.ForeignKey(Commune, on_delete=models.PROTECT, null=True, blank=True)


    def __str__(self):
        return f"Order {self.id} - {self.costumer_name} - {self.order_status}"

    def update_total(self):
        """
        Recalculate total_amount by summing (variant.price * quantity) for all line items.
        Call this *after* items have been created or modified.
        """
        new_total = sum(
            item.variant.price * item.quantity
            for item in self.items.all()
        )
        self.total_amount = new_total
        self.save(update_fields=["total_amount"])

    def save(self, *args, **kwargs):
        """
        We want to decrement stock only once:
          • When an existing Order’s status changes from “Pending” → “Accepted”.
          • Do NOT decrement on every save. Also do NOT decrement when creating a brand‐new order,
            because new orders default to “Pending.”

        Algorithm:
          1. If this instance already exists in the DB (i.e. self.pk is not None),
             fetch the “old” version to see its previous order_status.
          2. Call super().save(…) to persist any changes (e.g. maybe status just flipped).
          3. If previous_status != 'Accepted' but now self.order_status == 'Accepted',
             iterate self.items.all() and for each, call its update_stock().
        """
        is_new = self.pk is None
        previous_status = None

        if not is_new:
            # Grab the old row to see what the status was before we save
            prev = Order.objects.filter(pk=self.pk).only("order_status").first()
            if prev:
                previous_status = prev.order_status

        super().save(*args, **kwargs)

        # Only when updating (not on create) AND status flipped “Pending→Accepted”:
        if (not is_new) and (previous_status == "Pending") and (self.order_status == "Accepted"):
            for item in self.items.all():
                item.update_stock()
            # (optional) If you want to also recalc total right after acceptance, you could call:
            # self.update_total()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clean(self):
        if self.variant and self.quantity > self.variant.stock:
            raise ValidationError(
                f"Only {self.variant.stock} units available for {self.variant}. You requested {self.quantity}."
            )

    def save(self, *args, **kwargs):
        self.full_clean() 
        is_new_line = self.pk is None
        if is_new_line:
            self.price = self.variant.price * self.quantity
        super().save(*args, **kwargs)

    def update_stock(self):
        """
        Subtract this line’s quantity from the variant’s stock.
        Called by Order.save() only once, when status flips to 'Accepted'.
        """
        # Optionally guard against negative stock:
        if self.quantity > self.variant.stock:
            raise ValueError("Insufficient stock to fulfill this order item.")

        self.variant.stock -= self.quantity
        self.variant.save(update_fields=['stock'])

    def __str__(self):
        return f"{self.quantity} x {self.variant} for Order {self.order.id}"
