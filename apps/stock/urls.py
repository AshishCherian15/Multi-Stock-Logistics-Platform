from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, views_alerts

router = DefaultRouter()
router.register(r'api', views.StockViewSet)

urlpatterns = [
    path('', views.stock_dashboard, name='stock_dashboard'),
    path('', include(router.urls)),
    path('api/add/', views.add_stock_api, name='add_stock_api'),
    path('api/bulk-upload/', views.bulk_upload_stock_api, name='bulk_upload_stock_api'),
    path('api/adjust/', views.adjust_stock_api, name='adjust_stock_api'),
    path('api/transfer/', views.transfer_stock_api, name='transfer_stock_api'),
    path('movements/', views.stock_movements_page, name='stock_movements_page'),
    path('movements/<int:movement_id>/delete/', views.delete_movement, name='delete_movement'),
    path('api/movements/', views.stock_movements_api, name='stock_movements_api'),
    path('alerts/', views_alerts.stock_alerts, name='stock_alerts'),
    path('check-alerts/', views_alerts.check_alerts_api, name='check_alerts_api'),
    path('resolve-alert/<int:alert_id>/', views_alerts.resolve_alert, name='resolve_alert'),
]