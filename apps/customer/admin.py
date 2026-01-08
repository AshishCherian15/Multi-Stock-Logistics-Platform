from django.contrib import admin
from .models import ListModel

@admin.register(ListModel)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['customer_name', 'customer_city', 'customer_contact', 'customer_level']
    search_fields = ['customer_name', 'customer_city']