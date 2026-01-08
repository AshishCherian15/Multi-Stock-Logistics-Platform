from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.category_list, name='list'),
    path('create/', views.category_create, name='create'),
    path('edit/<int:pk>/', views.category_edit, name='edit'),
    path('delete/<int:pk>/', views.category_delete, name='delete'),
    path('api/', views.category_api, name='api'),
]
