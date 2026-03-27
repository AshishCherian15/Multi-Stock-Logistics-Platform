from django.urls import path
from . import views
app_name = 'transfers'
urlpatterns = [
    path('', views.transfer_list, name='list'),
    path('create/', views.create_transfer, name='create'),
]
