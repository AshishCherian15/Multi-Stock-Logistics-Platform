from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('submit/', views.submit_review, name='submit'),
    path('<int:review_id>/helpful/', views.mark_helpful, name='mark_helpful'),
    path('get/<str:review_type>/<int:item_id>/', views.get_reviews, name='get_reviews'),
    path('my-reviews/', views.my_reviews, name='my_reviews'),
]
