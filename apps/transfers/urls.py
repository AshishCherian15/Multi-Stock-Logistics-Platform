from django.urls import path
from . import views

urlpatterns = [
    path('', views.transfer_list, name='transfer_list'),
    path('create/', views.create_transfer, name='create_transfer'),
    path('approve/<int:transfer_id>/', views.approve_transfer, name='approve_transfer'),
    path('track/<int:transfer_id>/', views.track_transfer, name='track_transfer'),
]