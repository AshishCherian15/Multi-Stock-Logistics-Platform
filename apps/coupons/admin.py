from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'applicable_to', 'usage_count', 'valid_from', 'valid_until', 'is_active']
    list_filter = ['discount_type', 'applicable_to', 'is_active']
    search_fields = ['code', 'description']
