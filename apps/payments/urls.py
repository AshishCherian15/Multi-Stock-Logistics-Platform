from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('pay/<str:booking_type>/<int:booking_id>/', views.payment_page, name='payment_page'),
    path('process/', views.process_payment_view, name='process'),
    path('refund/', views.refund_payment_view, name='refund'),
    path('history/', views.payment_history, name='history'),
    path('success/<str:booking_type>/<int:booking_id>/', views.payment_success, name='success'),
    path('failed/<str:booking_type>/<int:booking_id>/', views.payment_failed, name='failed'),
    path('webhook/', views.payment_webhook, name='webhook'),
]
