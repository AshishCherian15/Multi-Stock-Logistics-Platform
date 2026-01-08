from django.urls import path
from . import views

urlpatterns = [
    path('', views.return_list, name='return_list'),
    path('create/', views.create_return, name='create_return'),
    path('process/<int:return_id>/', views.process_return, name='process_return'),
    path('refund/<int:return_id>/', views.process_refund, name='process_refund'),
]