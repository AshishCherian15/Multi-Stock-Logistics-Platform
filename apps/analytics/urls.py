from django.urls import path
from . import views
from .streaming import realtime_stream

app_name = 'analytics'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('advanced/', views.advanced_analytics, name='advanced'),
    path('api/data/', views.analytics_data_api, name='analytics_data_api'),
    path('api/overview/', views.overview_api, name='overview_api'),
    path('api/sales-chart/', views.sales_chart_api, name='sales_chart_api'),
    path('api/inventory-chart/', views.inventory_chart_api, name='inventory_chart_api'),
    path('api/top-products/', views.top_products_api, name='top_products_api'),
    path('api/alerts-summary/', views.alerts_summary_api, name='alerts_summary_api'),
    path('api/user-activity/', views.user_activity_api, name='user_activity_api'),
    path('api/revenue-breakdown/', views.revenue_breakdown_api, name='revenue_breakdown_api'),
    path('stream/realtime/', realtime_stream, name='realtime_stream'),
]
