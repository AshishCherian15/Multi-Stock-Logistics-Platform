from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.wishlist_page, name='wishlist_page'),
    path('api/get/', views.get_wishlist, name='get_wishlist'),
    path('api/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('api/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_item'),
    path('api/clear/', views.clear_wishlist, name='clear_wishlist'),
]
