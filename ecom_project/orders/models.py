# orders/models.py

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from products.models import Product
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
    delivery_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    wilaya = models.CharField(max_length=100)
    commune = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Order {self.id} - {self.costumer_name} - {self.order_status}"

    def update_total(self):
        """
        Recalculate total_amount by summing (variant.price * quantity) for all line items.
        Call this *after* items have been created or modified.
        """
        new_total = sum(
            item.product.price * item.quantity
            for item in self.items.all()
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
                # check every LineItem
                for item in self.items.all():
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
            for item in self.items.all():
                item.update_stock()
            # optionally: self.update_total()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT,blank=True, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clean(self):
        if self.product and self.quantity > self.product.stock:
            raise ValidationError(
                f"Only {self.product.stock} units available for {self.product}. You requested {self.quantity}."
            )

    def save(self, *args, **kwargs):
        self.full_clean() 
        self.price = self.product.price * self.quantity if self.product else 0
        is_new_line = self.pk is None
        if is_new_line:
            self.price = self.product.price * self.quantity
        super().save(*args, **kwargs)

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
