from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('api/generate/', views.generate_report_api, name='generate_report_api'),
    path('api/inventory/', views.get_inventory_data, name='get_inventory_data'),
    path('api/sales/', views.get_sales_data, name='get_sales_data'),
    path('export/', views.export_report, name='export_report'),
]