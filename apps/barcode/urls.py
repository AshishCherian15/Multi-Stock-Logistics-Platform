from django.urls import path
from . import views
urlpatterns = [
    path('', views.barcode_system, name='barcode_system'),
    path('scanner/', views.barcode_scanner, name='barcode_scanner'),
    path('generator/', views.barcode_generator, name='barcode_generator'),
    path('product/<int:product_id>/', views.generate_product_barcode, name='generate_product_barcode'),
    path('api/qr/<int:product_id>/', views.generate_qr_api, name='generate_qr_api'),
]
