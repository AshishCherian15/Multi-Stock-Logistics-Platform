from django.urls import path
from . import views, views_api, group_views

app_name = 'messaging'

urlpatterns = [
    # Main views
    path('', views.messaging_home, name='home'),
    path('users/', views.user_list, name='users'),
    path('create-group/', views.create_group, name='create_group'),
    path('start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('chat/<int:conversation_id>/', views.chat, name='chat'),
    
    # Message APIs
    path('api/send/<int:conversation_id>/', views.send_message_api, name='send_message'),
    path('api/load/<int:conversation_id>/', views_api.load_messages_api, name='load_messages'),
    path('api/messages/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    path('api/messages/<int:message_id>/edit/', views_api.edit_message_api, name='edit_message'),
    path('api/messages/<int:message_id>/react/', views.react_message, name='react_message'),
    path('api/messages/<int:message_id>/star/', views_api.star_message_api, name='star_message'),
    path('api/messages/<int:message_id>/pin/', views_api.pin_message_api, name='pin_message'),
    path('api/messages/<int:message_id>/forward/', views_api.forward_message_api, name='forward_message'),
    
    # Conversation APIs
    path('api/conversations/search/', views_api.search_messages_api, name='search_messages'),
    path('api/conversations/<int:conversation_id>/pin/', views_api.pin_conversation_api, name='pin_conversation'),
    
    # Status APIs
    path('api/status/update/', views_api.update_status_api, name='update_status'),
    path('api/status/typing/<int:conversation_id>/', views_api.typing_indicator_api, name='typing_indicator'),
    
    # Guest messages
    path('guest/send/', views.send_guest_message, name='send_guest_message'),
    
    # Customer chat
    path('customer/<int:customer_id>/', views.start_customer_chat, name='customer_chat'),
    
    # User chat
    path('user/<int:user_id>/', views.start_user_chat, name='user_chat'),
    
    # Supplier chat
    path('supplier/<int:supplier_id>/', views.start_supplier_chat, name='supplier_chat'),
    
    # User APIs
    path('api/profile/<int:user_id>/', views_api.user_profile_api, name='user_profile'),
    path('api/unread-count/', views_api.unread_count_api, name='unread_count'),
    path('api/online-users/', views_api.get_online_users_api, name='online_users'),
    path('api/notifications/', views_api.get_notifications_api, name='notifications'),
    
    # Advanced Message APIs
    path('api/conversations/<int:conversation_id>/info/', views_api.get_conversation_info_api, name='conversation_info'),
    path('api/conversations/<int:conversation_id>/mark-read/', views_api.mark_messages_read_api, name='mark_read'),
    path('api/messages/<int:message_id>/delivery/', views_api.get_message_delivery_info_api, name='message_delivery'),
    path('api/messages/bulk-action/', views_api.bulk_message_action_api, name='bulk_action'),
    
    # Group Management
    path('groups/', group_views.group_list, name='group_list'),
    path('groups/create/', group_views.create_group_advanced, name='create_group_advanced'),
    path('groups/<int:conversation_id>/settings/', group_views.group_settings, name='group_settings'),
    path('groups/<int:conversation_id>/delete/', group_views.delete_group, name='delete_group'),
    
    # Conversation Actions
    path('conversations/<int:conversation_id>/pin/', group_views.toggle_conversation_pin, name='toggle_pin'),
    path('conversations/<int:conversation_id>/mute/', group_views.toggle_conversation_mute, name='toggle_mute'),
    path('conversations/<int:conversation_id>/archive/', group_views.toggle_conversation_archive, name='toggle_archive'),
    path('conversations/<int:conversation_id>/settings/', group_views.conversation_settings, name='conversation_settings'),
]