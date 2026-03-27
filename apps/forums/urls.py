from django.urls import path
from . import views

app_name = 'forums'

urlpatterns = [
    path('', views.forum_home, name='home'),
    path('category/<int:category_id>/', views.category_topics, name='category_topics'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('category/<int:category_id>/new/', views.create_topic, name='create_topic'),
    path('topic/<int:topic_id>/reply/', views.create_post, name='create_post'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('topic/<int:topic_id>/delete/', views.delete_topic, name='delete_topic'),
]
