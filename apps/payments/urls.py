from django.urls import path
from . import views

urlpatterns = [
    path('pay/<int:order_id>/', views.payment_page, name='payment_page'),
    path('process/', views.process_payment, name='process_payment'),
    path('webhook/', views.payment_webhook, name='payment_webhook'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('failed/<int:payment_id>/', views.payment_failed, name='payment_failed'),
]
