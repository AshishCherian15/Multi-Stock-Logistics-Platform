from django.contrib import admin
from .models import Conversation, Message, MessageReaction

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_group', 'created_at']
    list_filter = ['is_group', 'created_at']
    search_fields = ['name']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'content', 'is_edited', 'timestamp']
    list_filter = ['is_edited', 'timestamp']
    search_fields = ['content', 'sender__username']

@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'emoji', 'created_at']
    list_filter = ['emoji', 'created_at']
