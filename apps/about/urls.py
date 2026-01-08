from django.urls import path
from . import views

app_name = 'about'

urlpatterns = [
    path('', views.about_page, name='about_page'),
    path('manage/', views.manage_about, name='manage_about'),
    path('section/create/', views.create_section, name='create_section'),
    path('section/<int:pk>/data/', views.section_data, name='section_data'),
    path('section/<int:pk>/update/', views.update_section, name='update_section'),
    path('static/<str:key>/update/', views.update_static, name='update_static'),
    path('section/<int:pk>/delete/', views.delete_section, name='delete_section'),
    path('team/create/', views.create_team, name='create_team'),
    path('team/<int:pk>/delete/', views.delete_team, name='delete_team'),
    path('gallery/create/', views.create_gallery, name='create_gallery'),
    path('gallery/<int:pk>/delete/', views.delete_gallery, name='delete_gallery'),
]
