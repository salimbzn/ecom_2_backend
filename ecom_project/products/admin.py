# products/admin.py

# 1) Create a ModelForm that forces `color` to render as <input type="color">

# 2) In your inline, tell it to use the new form


from decimal import Decimal
from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category

class DiscountedListFilter(admin.SimpleListFilter):
    title = 'Discounted'
    parameter_name = 'discounted'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Discounted'),
            ('no', 'Not Discounted'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.exclude(discount_price__isnull=True).exclude(discount_price=Decimal('0.00'))
        if self.value() == 'no':
            return queryset.filter(discount_price__isnull=True) | queryset.filter(discount_price=Decimal('0.00'))
        return queryset

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "discount_price",
        "product_image_small_preview",
        "stock",
        "sold"
    )
    list_display_links = ("id", "name")
    list_filter = ("category", DiscountedListFilter)
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("product_image_large_preview", "get_discounted_price")
    fields = (
        "name",
        "description",
        "price",
        "discount_price",
        "get_discounted_price",
        "category",
        "product_image_large_preview",
        "color",
        "size",
        "stock",
        "image",
        "sold",
    )

    def get_discounted_price(self, obj):
        return obj.get_discounted_price()
    get_discounted_price.short_description = "Discounted Price"

    def get_color(self, obj):
        return format_html(
            '<input type="color" value="{}" readonly style="width: 50px; height: 30px; border: none;"/>',
            obj.color or "#ffffff",
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