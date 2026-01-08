from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api', views.WarehouseViewSet)

urlpatterns = [
    path('', views.warehouse_management_view, name='list'),
    path('manage/', views.warehouse_management_view, name='manage'),
    path('create/', views.create_warehouse, name='create'),
    path('stats/', views.warehouse_stats, name='stats'),
    path('zone/<str:zone_id>/', views.zone_details, name='zone_details'),
    path('products/', views.products_list, name='products'),
    path('', include(router.urls)),
]