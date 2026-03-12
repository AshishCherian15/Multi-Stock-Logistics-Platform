from django.contrib import admin
from .models import Quotation, QuotationItem


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'discount_pct']


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['quotation_number', 'customer_name', 'customer_email', 'status',
                    'total_amount', 'expires_at', 'created_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['quotation_number', 'customer_name', 'customer_email']
    readonly_fields = ['quotation_number', 'created_at', 'updated_at', 'subtotal', 'tax_amount', 'total_amount']
    inlines = [QuotationItemInline]
    date_hierarchy = 'created_at'
