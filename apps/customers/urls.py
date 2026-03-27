from django.urls import path
from apps.customers import views
from apps.customers import password_views

app_name = 'customers'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard_alt'),
    path('marketplace/', views.marketplace, name='marketplace'),
    path('mine/', views.mine, name='mine'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('my-rentals/', views.my_rentals, name='my_rentals'),
    path('my-storage/', views.my_storage, name='my_storage'),
    path('my-lockers/', views.my_lockers, name='my_lockers'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('change-password/', password_views.change_password, name='change_password'),
]
