from django.urls import path
from . import views

app_name = 'staff_panel'

urlpatterns = [
    # Dashboard
    path('', views.staff_dashboard, name='dashboard'),
    
    # My Tasks
    path('tasks/', views.my_tasks, name='tasks'),
    path('tasks/<int:order_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:order_id>/update-status/', views.update_task_status, name='task_update_status'),
    
    # Inventory Check
    path('inventory/', views.inventory_check, name='inventory'),
    
    # Customer Orders
    path('orders/', views.customer_orders, name='orders'),
    
    # My Activity
    path('activity/', views.my_activity, name='activity'),
]
