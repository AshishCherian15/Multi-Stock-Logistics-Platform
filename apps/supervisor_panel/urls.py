from django.urls import path
from . import views

app_name = 'supervisor_panel'

urlpatterns = [
    # Dashboard
    path('', views.supervisor_dashboard, name='dashboard'),
    
    # Team Management
    path('team/', views.team_management, name='team'),
    path('team/<int:user_id>/', views.team_member_detail, name='team_detail'),
    path('staff-management/', views.staff_management, name='staff_management'),  # Supervisor-only page
    
    # Order Monitoring
    path('orders/', views.order_monitoring, name='orders'),
    path('orders/<int:order_id>/', views.order_detail_supervisor, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.update_order_status_supervisor, name='order_update_status'),
    
    # Inventory Monitoring
    path('inventory/', views.inventory_monitoring, name='inventory'),
    
    # Booking Monitoring
    path('bookings/', views.booking_monitoring, name='bookings'),
    
    # Reports
    path('reports/', views.performance_reports, name='reports'),
]
