from django.urls import path
from . import views

app_name = 'superadmin_panel'

urlpatterns = [
    # Home (redirects to main dashboard)
    path('', views.superadmin_panel_home, name='home'),
    
    # User Management
    path('users/', views.system_users, name='users'),
    path('users/<int:user_id>/', views.user_detail_super, name='user_detail'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/change-role/', views.change_user_role, name='change_user_role'),
    
    # System Settings
    path('settings/', views.system_settings, name='settings'),
    
    # System Logs
    path('logs/', views.system_logs, name='logs'),
    
    # Database
    path('database/', views.database_overview, name='database'),
    
    # Orders
    path('orders/', views.all_orders_super, name='orders'),
    
    # Analytics
    path('analytics/', views.analytics_dashboard, name='analytics'),
]
