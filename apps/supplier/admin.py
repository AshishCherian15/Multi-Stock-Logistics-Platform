from django.contrib import admin
from .models import ListModel

@admin.register(ListModel)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['supplier_name', 'supplier_city', 'supplier_contact', 'supplier_level']
    search_fields = ['supplier_name', 'supplier_city']