from django.urls import path
from . import views

urlpatterns = [
    path('scanner/', views.barcode_system, name='barcode_scanner'),
    path('generator/', views.barcode_system, name='barcode_generator'),
    path('generate/<int:product_id>/', views.generate_product_barcode, name='generate_product_barcode'),
    path('', views.barcode_system, name='barcode_home'),
]