from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('create/', views.create_ticket, name='create'),
    path('', views.ticket_list, name='list'),
    path('<int:ticket_id>/', views.ticket_detail, name='detail'),
    path('<int:ticket_id>/close/', views.close_ticket, name='close'),
]
