from django.urls import path
from . import views

urlpatterns = [
    path('', views.shipments_list, name='shipments_list'),
    path('create/', views.create_shipment, name='create_shipment'),
    path('<int:shipment_id>/update/', views.update_shipment, name='update_shipment'),
    path('<int:shipment_id>/delete/', views.delete_shipment, name='delete_shipment'),
    path('tracking/<int:shipment_id>/', views.tracking_detail, name='tracking_detail'),
    path('<int:shipment_id>/tracking/add/', views.add_tracking_event, name='add_tracking_event'),
    path('carriers/', views.carriers_list, name='carriers_list'),
    path('rates/', views.rates_list, name='rates_list'),
    path('track/', views.track_shipment_public, name='track_public'),
]
