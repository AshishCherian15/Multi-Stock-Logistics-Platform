from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'auth'

urlpatterns = [
    path('', views.login_selection, name='login_selection'),
    path('login/', views.login_selection, name='login'),
    path('team-login/', views.team_login, name='team_login'),
    path('api/team-users/', views.api_team_users, name='api_team_users'),
    path('customer-login/', views.customer_login, name='customer_login'),
    path('guest-access/', views.guest_access, name='guest_access'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('google/demo/', views.demo_google_callback, name='demo_google_callback'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('send-reset-code/', views.send_reset_code, name='send_reset_code'),
    path('verify-reset-code/', views.verify_reset_code, name='verify_reset_code'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_api, name='change_password'),
]