from django.urls import path
from . import views

urlpatterns = [
    path('', views.quotation_list, name='quotation_list'),
    path('create/', views.create_quotation, name='create_quotation'),
    path('detail/<int:quotation_id>/', views.quotation_detail, name='quotation_detail'),
    path('convert/<int:quotation_id>/', views.convert_to_order, name='convert_to_order'),
]