from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Cart, CartItem, Order, OrderItem, OrderTracking, 
    Invoice, PreOrder, RestockNotification
)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('product', 'quantity', 'subtotal', 'added_at')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'total_items', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('customer__username', 'customer__email')
    readonly_fields = ('total_items', 'total_amount', 'created_at', 'updated_at')
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)
    fields = ('product', 'product_name', 'quantity', 'unit_price', 'total_price')


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 0
    readonly_fields = ('timestamp',)
    fields = ('status', 'description', 'location', 'updated_by', 'timestamp')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status', 'payment_status', 
                   'total_amount', 'created_at', 'order_actions')
    list_filter = ('status', 'payment_status', 'created_at', 'confirmed_at', 'shipped_at')
    search_fields = ('order_number', 'customer__username', 'customer__email', 'shipping_name')
    list_editable = ('status', 'payment_status')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'confirmed_at', 
                      'shipped_at', 'delivered_at')
    inlines = [OrderItemInline, OrderTrackingInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'customer', 'status', 'payment_status')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'discount_amount', 'shipping_cost', 'tax_amount', 'total_amount', 'coupon_code')
        }),
        ('Shipping Address', {
            'fields': ('shipping_name', 'shipping_address', 'shipping_city', 'shipping_state', 
                      'shipping_postal_code', 'shipping_country', 'shipping_phone')
        }),
        ('Billing Address', {
            'fields': ('billing_name', 'billing_address', 'billing_city', 'billing_state', 
                      'billing_postal_code', 'billing_country'),
            'classes': ('collapse',)
        }),
        ('Staff Assignment', {
            'fields': ('processed_by', 'warehouse_manager')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'confirmed_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        })
    )
    
    def order_actions(self, obj):
        actions = []
        if obj.status == 'pending':
            actions.append('<a class="button" href="{}">Confirm</a>'.format(
                reverse('admin:orders_order_change', args=[obj.pk]) + '?action=confirm'
            ))
        if obj.can_be_cancelled:
            actions.append('<a class="button" href="{}">Cancel</a>'.format(
                reverse('admin:orders_order_change', args=[obj.pk]) + '?action=cancel'
            ))
        return format_html(' '.join(actions))
    order_actions.short_description = 'Actions'
    order_actions.allow_tags = True


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product_name', 'quantity', 'unit_price', 'total_price')
    list_filter = ('order__status', 'order__created_at')
    search_fields = ('order__order_number', 'product_name', 'product_sku')
    readonly_fields = ('total_price',)


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'description', 'location', 'updated_by', 'timestamp')
    list_filter = ('status', 'timestamp', 'updated_by')
    search_fields = ('order__order_number', 'description', 'location')
    readonly_fields = ('timestamp',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'order', 'invoice_date', 'due_date', 'pdf_file')
    list_filter = ('invoice_date', 'due_date')
    search_fields = ('invoice_number', 'order__order_number')
    readonly_fields = ('invoice_number', 'invoice_date')


@admin.register(PreOrder)
class PreOrderAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'quantity', 'expected_availability', 
                   'deposit_amount', 'is_notified', 'created_at')
    list_filter = ('expected_availability', 'is_notified', 'created_at')
    search_fields = ('customer__username', 'product__name')
    list_editable = ('is_notified',)
    readonly_fields = ('created_at',)


@admin.register(RestockNotification)
class RestockNotificationAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'is_notified', 'created_at', 'notified_at')
    list_filter = ('is_notified', 'created_at', 'notified_at')
    search_fields = ('customer__username', 'product__name')
    list_editable = ('is_notified',)
    readonly_fields = ('created_at', 'notified_at')