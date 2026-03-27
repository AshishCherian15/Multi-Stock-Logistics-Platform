from django.contrib import admin
from .models import Invoice, InvoiceItem, Receipt, InvoiceComment

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer_name', 'invoice_type', 'grand_total', 'status', 'invoice_date']
    list_filter = ['status', 'invoice_type', 'invoice_date']
    search_fields = ['invoice_number', 'customer_name', 'customer_email']

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'description', 'quantity', 'price', 'amount']

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'invoice', 'payment_mode', 'amount_paid', 'payment_date']
    list_filter = ['payment_mode', 'payment_date']
    search_fields = ['receipt_number']

@admin.register(InvoiceComment)
class InvoiceCommentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'user', 'created_at']
    list_filter = ['created_at']
