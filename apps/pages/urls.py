from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('customers/', views.customers_page, name='customers'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:customer_id>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:customer_id>/delete/', views.customer_delete, name='customer_delete'),
    path('customers/<int:customer_id>/message/', views.customer_message, name='customer_message'),
    path('customers/create/', views.customer_create, name='customer_create'),
    path('customers/export/', views.customers_export, name='customers_export'),
    path('suppliers/', views.suppliers_page, name='suppliers'),
    path('warehouses/', views.warehouses_page, name='warehouses'),
]
