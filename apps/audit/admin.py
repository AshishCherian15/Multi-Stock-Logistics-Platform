from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'model_name', 'object_id', 'ip_address', 'timestamp']
    list_filter = ['action_type', 'model_name', 'timestamp']
    search_fields = ['user__username', 'description', 'object_id']
    readonly_fields = ['user', 'action_type', 'model_name', 'object_id', 'description', 'ip_address', 'user_agent', 'changes', 'timestamp']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
