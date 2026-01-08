from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.SupplierViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('manage/', views.supplier_management_view, name='suppliers_manage'),
    path('export/<str:format>/', views.export_suppliers, name='suppliers_export'),
]