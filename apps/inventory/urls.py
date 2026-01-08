from django.urls import path
from . import views, views_unified, views_api, views_bulk, views_production

app_name = 'inventory'

urlpatterns = [
    path('', views_unified.unified_inventory, name='dashboard'),
    path('movements/', views.stock_movements, name='movements'),
    path('alerts/', views.stock_alerts, name='alerts'),
    path('create-transaction/', views.create_transaction, name='create_transaction'),
    path('resolve-alert/<int:alert_id>/', views.resolve_alert, name='resolve_alert'),
    
    # Production Inventory routes
    path('production/', views_production.production_inventory, name='production_inventory'),
    path('product/<int:product_id>/details/', views_production.product_detail_modal, name='product_detail'),
    path('product/<int:product_id>/edit/', views_production.product_edit_modal, name='product_edit'),
    
    # Stock API endpoints
    path('api/stock/<int:stock_id>/', views.get_stock_api, name='get_stock'),
    path('api/stock/create/', views.create_stock_api, name='create_stock'),
    path('api/stock/<int:stock_id>/update/', views.update_stock_api, name='update_stock'),
    path('api/stock/<int:stock_id>/delete/', views.delete_stock_api, name='delete_stock'),
    path('api/stock/<int:stock_id>/update-qty/', views.update_qty_api, name='update_qty'),
    path('api/stock/bulk-upload/', views_bulk.bulk_upload_stock_api, name='bulk_upload'),
]