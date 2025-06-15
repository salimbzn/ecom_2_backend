# orders/admin.py

from django.contrib import admin
from django.db.models import Case, When, Value, IntegerField
from django.utils.html import format_html
from .models import Order, OrderItem, Wilaya, Commune

@admin.register(Wilaya)
class WilayaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'domicile_price', 'bureau_price')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'wilaya')
    search_fields = ('name',)
    ordering = ('name',)
    list_filter = ('wilaya',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('wilaya')



class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 1

    fields = (
        'variant',
        'quantity',
        'price',
        'get_variant_size',
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('variant', 'quantity', 'price', 'get_variant_size')
        return ('price', 'get_variant_size')

    def has_add_permission(self, request, obj=None):
        return obj is None

    def has_delete_permission(self, request, obj=None):
        return obj is None

    def get_variant_size(self, item_obj):
        return item_obj.variant.size if item_obj.variant else "-"
    get_variant_size.short_description = 'Size'

    def price_display(self, item_obj):
        return f"${item_obj.price:.2f}"
    price_display.short_description = 'Price'


@admin.action(description="Mark selected orders as Accepted")
def mark_as_accepted(modeladmin, request, queryset):
    # Only pick orders that are currently pending
    pending_qs = queryset.filter(order_status__iexact='Pending')

    accepted_count = 0
    for order in pending_qs:
        order.order_status = 'Accepted'
        order.save()            # ← triggers Order.save() → item.update_stock()
        order.update_total()    # ← recalc total AFTER stock has been decremented
        accepted_count += 1

    modeladmin.message_user(
        request,
        f"{accepted_count} order(s) marked as accepted."
    )


@admin.action(description="Mark selected orders as Rejected")
def mark_as_rejected(modeladmin, request, queryset):
    # Only pick orders that are currently pending
    pending_qs = queryset.filter(order_status__iexact='Pending')

    rejected_count = 0
    for order in pending_qs:
        order.order_status = 'Rejected'
        order.save()            # ← triggers Order.save(), but no stock change on “Rejected”
        rejected_count += 1

    modeladmin.message_user(
        request,
        f"{rejected_count} order(s) marked as rejected."
    )

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'costumer_name',
        'costumer_phone',
        'order_date',
        'order_status_badge',
        'total_amount_formatted',
    )
    list_display_links = ('id','costumer_name')
    list_filter = ('order_status',)
    search_fields = ('costumer_name', 'costumer_phone')
    date_hierarchy = 'order_date'

    # Include both actions here:
    actions = [mark_as_accepted, mark_as_rejected]

    inlines = [OrderItemInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request).annotate(
            _status_order=Case(
                When(order_status__iexact='pending',  then=Value(0)),
                When(order_status__iexact='accepted', then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            )
        )
        return qs.order_by('_status_order', '-order_date')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            base = (
                'id',
                'costumer_name',
                'costumer_phone',
                'delivery_type',
                'wilaya',
                'commune',
                'order_date',
                'total_amount'
            )
            status = obj.order_status.lower()
            # Once an order is accepted OR rejected, lock all fields (including status)
            if status in ('accepted', 'rejected'):
                return base + ('order_status',)
            # If still pending, lock everything except order_status (so you can change it)
            return base

        # obj is None → Add form: only date & total are read‐only
        return ('order_date', 'total_amount')

    def order_status_badge(self, obj):
        COLOR = {
            'pending':  'badge bg-warning text-dark',
            'accepted': 'badge bg-success',
            'rejected': 'badge bg-danger',
        }
        css = COLOR.get(obj.order_status.lower(), 'badge bg-secondary')
        return format_html(f'<span class="{css}">{obj.order_status.capitalize()}</span>')
    order_status_badge.short_description = 'Status'
    order_status_badge.admin_order_field = 'order_status'

    def total_amount_formatted(self, obj):
        return f"${obj.total_amount:.2f}"
    total_amount_formatted.short_description = 'Total'
    total_amount_formatted.admin_order_field = 'total_amount'

    def get_actions(self, request):
        actions = super().get_actions(request) or {}
        status_filter = request.GET.get('order_status__exact', '').lower()

        # If we're already viewing accepted OR rejected orders, hide both bulk actions:
        if status_filter in ('accepted', 'rejected'):
            actions.pop('mark_as_accepted', None)
            actions.pop('mark_as_rejected', None)

        return actions
