from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.global_search, name='global_search'),
    path('suggestions/', views.search_suggestions, name='suggestions'),
    path('history/', views.search_history, name='history'),
]
