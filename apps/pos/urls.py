from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.pos_interface, name='interface'),
    path('sales/', views.pos_sales, name='sales'),
    path('complete-sale/', views.complete_sale, name='complete_sale'),
    path('bill/<int:sale_id>/', views.bill_view, name='bill_view'),
    path('bill/<int:sale_id>/pdf/', views.bill_pdf, name='bill_pdf'),
]