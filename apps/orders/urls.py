from django.urls import path
from . import views, views_unified

app_name = 'orders'

urlpatterns = [
    path('all/', views_unified.unified_orders, name='unified_orders'),
    path('sales/', views.sales_orders, name='sales_orders'),
    path('admin-panel/orders/', views.sales_orders, name='admin_orders'),
    path('purchase/', views.purchase_orders, name='purchase_orders'),
    path('create/', views.create_order, name='create_order'),
    path('<int:order_id>/', views.order_detail, name='order_detail_short'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('admin-panel/orders/<int:order_id>/', views.order_detail, name='admin_order_detail'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_status'),
    path('admin-panel/orders/<int:order_id>/update-status/', views.update_order_status, name='admin_update_status'),
    path('delete/<int:order_id>/', views.delete_order, name='delete_order'),
    path('api/checkout/', views.create_order_from_cart, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('export/', views.export_orders, name='export_orders'),
    path('download/<int:order_id>/', views.download_order, name='download_order'),
]