from django.urls import path
from . import views

urlpatterns = [
    path('', views.adjustment_list, name='adjustment_list'),
    path('create/', views.create_adjustment, name='create_adjustment'),
    path('approve/<int:adjustment_id>/', views.approve_adjustment, name='approve_adjustment'),
]