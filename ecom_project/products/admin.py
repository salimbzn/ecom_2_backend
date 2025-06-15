# products/admin.py

from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Product, ProductVariant, Category


# 1) Create a ModelForm that forces `color` to render as <input type="color">
class ProductVariantForm(forms.ModelForm):
    color = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"type": "color"}),
        help_text="Choose a color (hex, e.g. #ff0000)",
    )

    class Meta:
        model = ProductVariant
        fields = "__all__"


# 2) In your inline, tell it to use the new form
class ProductVariantInline(admin.StackedInline):
    model = ProductVariant
    form = ProductVariantForm    # ← use our form here
    extra = 1

    fields = (
        "name",
        "price",
        "stock",
        "color",               # now a color-picker widget
        "size",
        "variant_image_large_preview",
        "image",
    )
    readonly_fields = ("variant_image_large_preview",)

    def variant_image_large_preview(self, obj):
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

    variant_image_large_preview.short_description = "Variant Image"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "product_image_small_preview",
        "variant_count",
    )
    list_display_links = ("id", "name")
    list_filter = ("category",)
    search_fields = ("name",)
    ordering = ("name",)
    inlines = [ProductVariantInline]

    readonly_fields = ("product_image_large_preview",)
    fields = (
        "name",
        "description",
        "price",
        "category",
        "product_image_large_preview",
        "image",
    )

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

    def variant_count(self, obj):
        return obj.variants.count()

    variant_count.short_description = "Variants"


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    form = ProductVariantForm    # ← use the same form here
    list_display = (
        "id",
        "product",
        "color",              # now shows hex-code, but editable via color picker
        "name",
        "variant_image_small_preview",
        "price",
        "stock",
    )
    list_display_links = ("id", "name")
    list_filter = ("product",)
    search_fields = ("name",)

    readonly_fields = ("variant_image_large_preview",)
    fields = (
        "product",
        "name",
        "color",                # renders as <input type='color'>
        "size",
        "price",
        "stock",
        "variant_image_large_preview",
        "image",
    )

    def variant_image_small_preview(self, obj):
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

    variant_image_small_preview.short_description = "Image"

    def variant_image_large_preview(self, obj):
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

    variant_image_large_preview.short_description = "Image (100px)"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)

    fields = ("name", "description")