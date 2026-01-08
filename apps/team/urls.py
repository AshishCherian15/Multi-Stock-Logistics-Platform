from django.urls import path
from . import views

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('export/', views.export_team, name='export_team'),
    path('api/user/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('api/user/create/', views.create_user, name='create_user'),
    path('api/user/<int:user_id>/update/', views.update_user, name='update_user'),
    path('api/user/<int:user_id>/change-role/', views.change_role, name='change_role'),
    path('api/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('api/request/<int:request_id>/approve/', views.approve_access_request, name='approve_request'),
    path('api/request/<int:request_id>/reject/', views.reject_access_request, name='reject_request'),
    path('api/invite/', views.invite_user, name='invite_user'),
    path('api/import/', views.import_users, name='import_users'),
]
