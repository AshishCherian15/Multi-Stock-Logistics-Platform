from django.urls import path
from . import views
app_name = 'adjustments'
urlpatterns = [
    path('', views.adjustment_list, name='list'),
    path('create/', views.create_adjustment, name='create'),
    path('<int:adjustment_id>/approve/', views.approve_adjustment, name='approve'),
]
