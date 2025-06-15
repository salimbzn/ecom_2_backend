# # filepath: c:\Users\haroun\Desktop\pfd\ecom_project\Backend\ecom_project\products\signal.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Product, ProductVariant

# @receiver(post_save, sender=Product)
# def create_default_variant(sender, instance, created, **kwargs):
#     if created and not instance.variants.exists():
#         ProductVariant.objects.create(
#             product=instance,
#             name=instance.name,
#             price=instance.price,
#             stock=instance.stock,
#         )