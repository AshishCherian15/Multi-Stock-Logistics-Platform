from django.contrib import admin
from .models import CreditProfile, CreditTransaction

@admin.register(CreditProfile)
class CreditProfileAdmin(admin.ModelAdmin):
    list_display = ['customer', 'credit_limit', 'available_credit', 'used_credit', 'risk_level', 'is_active']
    list_filter = ['risk_level', 'is_active']
    search_fields = ['customer__customer_name']

@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ['profile', 'transaction_type', 'amount', 'reference', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['profile__customer__customer_name', 'reference']
