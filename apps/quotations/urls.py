from django.urls import path
from . import views

urlpatterns = [
    path('', views.quotation_list, name='quotation_list'),
    path('create/', views.create_quotation, name='create_quotation'),
    path('<int:quotation_id>/', views.quotation_detail, name='quotation_detail'),
    path('<int:quotation_id>/status/', views.update_status, name='quotation_update_status'),
    path('<int:quotation_id>/convert/', views.convert_to_order, name='convert_to_order'),
]