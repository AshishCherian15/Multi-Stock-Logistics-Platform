from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_page, name='cart_page'),
    path('api/get/', views.get_cart, name='get_cart'),
    path('api/add/', views.add_to_cart, name='add_to_cart'),
    path('api/update/<int:item_id>/', views.update_cart_item, name='update_item'),
    path('api/remove/<int:item_id>/', views.remove_from_cart, name='remove_item'),
    path('api/clear/', views.clear_cart, name='clear_cart'),
    path('api/coupon/', views.apply_coupon, name='apply_coupon'),
    path('api/buy-now/', views.buy_now, name='buy_now'),
    path('api/checkout-payment/', views.checkout_payment, name='checkout_payment'),
]
