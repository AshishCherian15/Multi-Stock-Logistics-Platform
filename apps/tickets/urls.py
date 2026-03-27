from django.urls import path
from . import views
app_name = 'tickets'
urlpatterns = [
    path('', views.ticket_list, name='list'),
    path('create/', views.ticket_create, name='create'),
    path('<int:ticket_id>/', views.ticket_detail, name='detail'),
    path('<int:ticket_id>/status/', views.ticket_update_status, name='update_status'),
]
