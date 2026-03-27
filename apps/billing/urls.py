from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('create/', views.invoice_create, name='invoice_create'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('<int:invoice_id>/receipt/create/', views.receipt_create, name='receipt_create'),
    path('receipt/<int:pk>/', views.receipt_detail, name='receipt_detail'),
    path('receipt/<int:pk>/pdf/', views.receipt_pdf, name='receipt_pdf'),
    path('api/create-from-payment/', views.create_from_payment, name='create_from_payment'),
]
