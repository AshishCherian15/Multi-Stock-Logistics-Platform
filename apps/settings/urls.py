from django.urls import path
from . import views

urlpatterns = [
    path('', views.settings_page, name='settings_page'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('password/change/', views.change_password, name='change_password'),
    path('notifications/update/', views.update_notifications, name='update_notifications'),
    path('maintenance/toggle/', views.toggle_maintenance, name='toggle_maintenance'),
    path('api/update/', views.save_setting, name='save_setting'),
    path('api/get/<str:key>/', views.get_setting, name='get_setting'),
    path('status/', views.system_status, name='system_status'),
    path('api/metrics/', views.system_metrics_api, name='system_metrics_api'),
    path('announcements/create/', views.create_announcement, name='create_announcement'),
    path('announcements/update/', views.update_announcement, name='update_announcement'),
    path('api/announcements/', views.get_announcements_api, name='get_announcements_api'),
    path('api/dashboard-announcements/', views.get_dashboard_announcements_api, name='dashboard_announcements'),
    path('api/announcements/<int:announcement_id>/dismiss/', views.dismiss_announcement, name='dismiss_announcement'),
    path('api/announcements/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),
]