from django.urls import path
from . import views
app_name = 'reviews'
urlpatterns = [
    path('product/<int:product_id>/', views.product_reviews, name='product_reviews'),
    path('product/<int:product_id>/submit/', views.submit_review, name='submit'),
    path('<int:review_id>/delete/', views.delete_review, name='delete'),
]
