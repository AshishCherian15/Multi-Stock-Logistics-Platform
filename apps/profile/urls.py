from django.urls import path
from . import views

app_name = 'profile'

urlpatterns = [
    path('', views.user_profile, name='user_profile'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('upload-photo/', views.upload_photo, name='upload_photo'),
    path('change-password/', views.change_password, name='change_password'),
    path('wishlist-cart/', views.wishlist_cart_page, name='wishlist_cart'),
]
