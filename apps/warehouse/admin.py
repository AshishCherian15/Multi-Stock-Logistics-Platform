from django.contrib import admin
from .models import ListModel

@admin.register(ListModel)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['warehouse_name', 'warehouse_city', 'warehouse_manager', 'create_time']
    search_fields = ['warehouse_name', 'warehouse_city']