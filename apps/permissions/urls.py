from django.urls import path
from . import views

app_name = 'permissions'

urlpatterns = [
    path('', views.permission_list, name='list'),
    path('create/', views.create_permission, name='create'),
    path('matrix/', views.permission_matrix, name='matrix'),
    path('role/<str:role>/', views.role_permissions, name='role_permissions'),
    path('user/<int:user_id>/', views.user_permissions, name='user_permissions'),
    path('grant/<int:user_id>/', views.grant_permission, name='grant'),
    path('revoke/<int:override_id>/', views.revoke_permission, name='revoke'),
    path('logs/', views.access_logs, name='logs'),
    path('api/check/', views.check_permission_api, name='check_api'),
    path('api/users/', views.get_users_api, name='users_api'),
    path('api/change-role/', views.change_role_api, name='change_role_api'),
    path('api/get-permission/', views.get_permission_api, name='get_permission_api'),
    path('api/update-permission/', views.update_permission_api, name='update_permission_api'),
]
