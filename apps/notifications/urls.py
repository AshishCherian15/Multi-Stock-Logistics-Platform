from django.urls import path
from . import views
from django.http import JsonResponse

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_center, name='center'),
    path('mark-read/<int:notification_id>/', views.mark_read, name='mark_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('delete/<int:notification_id>/', views.delete_notification, name='delete'),
    path('preferences/', views.preferences, name='preferences'),
    path('api/unread-count/', views.unread_count_api, name='unread_count_api'),
    path('api/recent/', views.recent_notifications_api, name='recent_api'),
    path('recent/', views.recent_notifications_api, name='recent'),
    path('email-settings/', views.email_settings, name='email_settings'),
    path('test-email/', views.test_email, name='test_email'),
]
