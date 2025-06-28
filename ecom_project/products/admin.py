# products/admin.py

# 1) Create a ModelForm that forces `color` to render as <input type="color">

# 2) In your inline, tell it to use the new form


from decimal import Decimal
from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Category, ProductImage

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

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "is_main", "image_preview")
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="height:120px; width:auto; object-fit:contain; border:1px solid #ccc; padding:2px;" />'
                '</a>',
                obj.image.url,
            )
        return "(no image)"
    image_preview.short_description = "Preview"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "discount_price",
        "main_image_preview",
        "stock",
        "sold"
    )
    list_display_links = ("id", "name")
    list_filter = ("category",)
    search_fields = ("name",)
    ordering = ("name",)
    readonly_fields = ("main_image_preview", "get_discounted_price")
    fields = (
        "name",
        "description",
        "price",
        "discount_price",
        "get_discounted_price",
        "category",
        "main_image_preview",  # This will show the main image bigger
        "color",
        "size",
        "stock",
        "sold",
    )
    inlines = [ProductImageInline]

    def get_discounted_price(self, obj):
        return obj.get_discounted_price()
    get_discounted_price.short_description = "Discounted Price"

    def main_image_preview(self, obj):
        main_img = obj.main_image
        if not main_img:
            main_img_obj = obj.images.filter(is_main=True).first()
            if main_img_obj and main_img_obj.image:
                main_img = main_img_obj.image
        if main_img:
            # SMALLER size for list_display
            return format_html(
                '<img src="{}" style="height:60px; width:auto; object-fit:contain; border:1px solid #333; padding:2px;" />',
                main_img.url,
            )
        return "(no image)"
    main_image_preview.short_description = "Main Image"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category_image_preview")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)
    fields = ("name", "description", "image", "category_image_preview")
    readonly_fields = ("category_image_preview",)

    def category_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px; width:auto; object-fit:contain; border:1px solid #ccc; padding:2px;" />',
                obj.image.url,
            )
        return "(no image)"
    category_image_preview.short_description = "Image"