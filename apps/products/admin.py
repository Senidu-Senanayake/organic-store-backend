from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Product, ProductImage, Stock, ProductReview, 
    Wishlist, Coupon, PromotionalOffer
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'order')


class StockInline(admin.StackedInline):
    model = Stock
    extra = 0
    fields = ('quantity', 'reserved_quantity', 'reorder_level', 'max_stock_level')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'name': ('name',)}
    ordering = ('name',)
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'availability', 'stock_quantity', 
                   'is_featured', 'is_organic', 'is_active', 'created_at')
    list_filter = ('category', 'availability', 'is_featured', 'is_organic', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'sku')
    list_editable = ('price', 'availability', 'is_featured', 'is_active')
    prepopulated_fields = {'sku': ('name',)}
    inlines = [ProductImageInline, StockInline]
    readonly_fields = ('created_by', 'created_at', 'updated_at', 'average_rating', 'review_count')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'short_description', 'description', 'category', 'sku')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'cost_price', 'availability')
        }),
        ('Product Details', {
            'fields': ('weight', 'dimensions', 'is_organic', 'is_featured', 'is_active')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('System Info', {
            'fields': ('created_by', 'created_at', 'updated_at', 'average_rating', 'review_count'),
            'classes': ('collapse',)
        })
    )
    
    def stock_quantity(self, obj):
        if hasattr(obj, 'stock'):
            return obj.stock.quantity
        return 'No stock info'
    stock_quantity.short_description = 'Stock'
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'alt_text', 'is_primary', 'order')
    list_filter = ('is_primary', 'product__category')
    search_fields = ('product__name', 'alt_text')
    list_editable = ('is_primary', 'order')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return 'No Image'
    image_preview.short_description = 'Preview'


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'reserved_quantity', 'available_quantity', 
                   'reorder_level', 'is_low_stock', 'last_updated')
    list_filter = ('last_updated', 'product__category')
    search_fields = ('product__name', 'product__sku')
    readonly_fields = ('available_quantity', 'is_low_stock', 'last_updated')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'rating', 'is_verified_purchase', 
                   'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'created_at')
    search_fields = ('product__name', 'customer__username', 'title', 'comment')
    list_editable = ('is_approved',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Review Details', {
            'fields': ('product', 'customer', 'rating', 'title', 'comment')
        }),
        ('Status', {
            'fields': ('is_verified_purchase', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'created_at')
    list_filter = ('created_at', 'product__category')
    search_fields = ('customer__username', 'product__name')
    readonly_fields = ('created_at',)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'used_count', 
                   'maximum_uses', 'valid_from', 'valid_to', 'is_active', 'is_valid')
    list_filter = ('discount_type', 'is_active', 'valid_from', 'valid_to', 'created_at')
    search_fields = ('code', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('used_count', 'created_by', 'created_at', 'is_valid')
    filter_horizontal = ('applicable_products', 'applicable_categories')
    
    fieldsets = (
        ('Coupon Details', {
            'fields': ('code', 'description', 'discount_type', 'discount_value', 'minimum_amount')
        }),
        ('Usage Limits', {
            'fields': ('maximum_uses', 'used_count')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to', 'is_active')
        }),
        ('Applicable Items', {
            'fields': ('applicable_products', 'applicable_categories')
        }),
        ('System Info', {
            'fields': ('created_by', 'created_at', 'is_valid'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PromotionalOffer)
class PromotionalOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'offer_type', 'discount_percentage', 'valid_from', 
                   'valid_to', 'is_active', 'created_at')
    list_filter = ('offer_type', 'is_active', 'valid_from', 'valid_to', 'created_at')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)
    readonly_fields = ('created_by', 'created_at')
    filter_horizontal = ('applicable_products',)
    
    fieldsets = (
        ('Offer Details', {
            'fields': ('title', 'description', 'offer_type')
        }),
        ('Discount Configuration', {
            'fields': ('discount_percentage', 'buy_quantity', 'get_quantity')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_to', 'is_active')
        }),
        ('Applicable Products', {
            'fields': ('applicable_products',)
        }),
        ('System Info', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)