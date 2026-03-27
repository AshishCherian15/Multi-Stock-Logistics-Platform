from django.contrib import admin
from .models import Cart, CartItem, Coupon

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'subtotal', 'created_at']
    search_fields = ['user__username']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product_name', 'quantity', 'unit_price', 'total_price']
    list_filter = ['created_at']

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'min_order_amount', 'is_active', 'used_count']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code']
