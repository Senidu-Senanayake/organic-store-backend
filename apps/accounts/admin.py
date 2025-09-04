from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CustomerProfile, ModeratorProfile, WarehouseManagerProfile, SocialMediaAccount


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('role', 'phone_number', 'date_of_birth', 'profile_picture', 
                      'address', 'city', 'state', 'postal_code', 'country', 'is_verified')
        }),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'loyalty_points', 'total_orders', 'total_spent', 'newsletter_subscription')
    list_filter = ('newsletter_subscription',)
    search_fields = ('user__username', 'user__email')


@admin.register(ModeratorProfile)
class ModeratorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'assigned_by', 'department')
    list_filter = ('department',)
    search_fields = ('user__username', 'department')


@admin.register(WarehouseManagerProfile)
class WarehouseManagerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'warehouse_location', 'shift_start', 'shift_end')
    list_filter = ('warehouse_location',)
    search_fields = ('user__username', 'warehouse_location')


@admin.register(SocialMediaAccount)
class SocialMediaAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'social_id', 'created_at')
    list_filter = ('platform', 'created_at')
    search_fields = ('user__username', 'social_id')