# products/admin.py

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Product,Category


# 1) Create a ModelForm that forces `color` to render as <input type="color">

# 2) In your inline, tell it to use the new form


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "product_image_small_preview",
        "stock",
    )
    list_display_links = ("id", "name")
    list_filter = ("category",)
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("product_image_large_preview",)
    fields = (
        "name",
        "description",
        "price",
        "category",
        "product_image_large_preview",
        "color",  # renders as <input type='color'>
        "size",
        "stock",
        "image",
    )

    def get_color(self, obj):
        return format_html(
            '<input type="color" value="{}" readonly style="width: 50px; height: 30px; border: none;"/>',
            obj.color or "#ffffff",  # Default to white if color is None
        )
    def get_size(self, obj):
        return obj.size or "No Size"
    
    def product_image_small_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="height:50px; width:auto; '
                'object-fit:contain; border:1px solid #ccc; padding:2px;" />'
                "</a>",
                obj.image.url,
                obj.image.url,
            )
        return "(no image)"

    product_image_small_preview.short_description = "Image"

    def product_image_large_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="height:100px; width:auto; '
                'object-fit:contain; border:1px solid #ccc; padding:2px;" />'
                "</a>",
                obj.image.url,
                obj.image.url,
            )
        return "(no image)"

    product_image_large_preview.short_description = "Current Image"




@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)

    fields = ("name", "description")