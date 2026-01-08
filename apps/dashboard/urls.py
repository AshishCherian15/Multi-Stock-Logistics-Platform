from django.urls import path
from . import views_unified_team

app_name = 'dashboard'

urlpatterns = [
    # Unified Team Dashboard (SuperAdmin & Admin)
    path('team/', views_unified_team.unified_dashboard, name='team_dashboard'),
    path('team/users/', views_unified_team.team_user_list, name='team_users'),
    path('team/users/<int:user_id>/', views_unified_team.team_user_detail, name='team_user_detail'),
    path('team/users/<int:user_id>/toggle-status/', views_unified_team.team_user_toggle_status, name='team_user_toggle_status'),
    path('team/users/<int:user_id>/change-role/', views_unified_team.team_user_change_role, name='team_user_change_role'),
    path('team/orders/', views_unified_team.team_orders, name='team_orders'),
    path('team/inventory/', views_unified_team.team_inventory, name='team_inventory'),
    path('team/analytics/', views_unified_team.team_analytics, name='team_analytics'),
    path('team/settings/', views_unified_team.team_system_settings, name='team_settings'),
    path('team/logs/', views_unified_team.team_system_logs, name='team_logs'),
    path('team/database/', views_unified_team.team_database_overview, name='team_database'),
]
