from django.urls import path
from supplier import views

app_name = 'suppliers'

urlpatterns = [
    path('', views.supplier_management_view, name='list'),
    path('manage/', views.supplier_management_view, name='manage'),
    path('export/', views.export_suppliers, name='export'),
]