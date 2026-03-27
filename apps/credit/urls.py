from django.urls import path
from . import views

app_name = 'credit'

urlpatterns = [
    path('', views.credit_dashboard, name='dashboard'),
    path('add/', views.add_credit_profile, name='add_profile'),
    path('<int:profile_id>/', views.credit_detail, name='detail'),
]
