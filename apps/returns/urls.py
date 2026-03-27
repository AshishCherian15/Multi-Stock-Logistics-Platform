from django.urls import path
from . import views
app_name = 'returns'
urlpatterns = [
    path('', views.return_list, name='list'),
    path('create/', views.create_return, name='create'),
    path('<int:return_id>/process/', views.process_return, name='process'),
    path('<int:return_id>/refund/', views.process_refund, name='refund'),
]
