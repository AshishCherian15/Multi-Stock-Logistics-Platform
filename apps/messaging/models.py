from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='messaging_status')
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)
    is_typing_in = models.ForeignKey('Conversation', on_delete=models.SET_NULL, null=True, blank=True, related_name='typing_users')
    
    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"

class Conversation(models.Model):
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('hidden', 'Hidden'),
    ]
    
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_conversations')
    members = models.ManyToManyField(User, related_name='conversations')
    admins = models.ManyToManyField(User, related_name='admin_conversations', blank=True)
    is_group = models.BooleanField(default=False)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    avatar = models.ImageField(upload_to='conversation_avatars/', blank=True, null=True)
    description = models.TextField(blank=True)
    pinned_by = models.ManyToManyField(User, related_name='pinned_conversations', blank=True)
    muted_by = models.ManyToManyField(User, related_name='muted_conversations', blank=True)
    archived_by = models.ManyToManyField(User, related_name='archived_conversations', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.name
    
    def last_message(self):
        return self.messages.order_by('-timestamp').first()
    
    def unread_count(self, user):
        return self.messages.filter(read_by__isnull=True).exclude(sender=user).exclude(deleted_for=user).count()
    
    def get_other_user(self, current_user):
        if not self.is_group:
            return self.members.exclude(id=current_user.id).first()
        return None
    
    def is_admin(self, user):
        return self.admins.filter(id=user.id).exists() or self.created_by == user
    
    def can_view(self, user):
        # Members can always view
        if self.members.filter(id=user.id).exists():
            return True
        
        # Role-based visibility for groups
        if self.is_group:
            user_is_team = user.is_staff or user.is_superuser
            creator_is_team = self.created_by.is_staff or self.created_by.is_superuser
            
            # Team can see team groups based on visibility
            if user_is_team and creator_is_team:
                return self.visibility == 'public'
            
            # Customers can't see team groups unless added
            if not user_is_team and creator_is_team:
                return False
                
            # Team can see customer groups if added
            if user_is_team and not creator_is_team:
                return False
        
        return False
    
    def add_member(self, user, added_by):
        if not self.is_admin(added_by):
            raise ValidationError("Only admins can add members")
        
        # Role-based restrictions
        user_is_team = user.is_staff or user.is_superuser
        creator_is_team = self.created_by.is_staff or self.created_by.is_superuser
        
        # Customers can't add team members
        if not creator_is_team and user_is_team:
            raise ValidationError("Customers cannot add team members")
        
        self.members.add(user)
    
    def remove_member(self, user, removed_by):
        if not self.is_admin(removed_by) and removed_by != user:
            raise ValidationError("Only admins can remove members")
        
        self.members.remove(user)
        self.admins.remove(user)  # Remove admin status if any

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    attachment = models.FileField(upload_to='messages/', blank=True, null=True)
    attachment_type = models.CharField(max_length=20, blank=True, choices=[('image', 'Image'), ('file', 'File'), ('voice', 'Voice')])
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)
    deleted_for = models.ManyToManyField(User, related_name='deleted_messages', blank=True)
    is_edited = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_starred_by = models.ManyToManyField(User, related_name='starred_messages', blank=True)
    reply_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies')
    forwarded_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='forwards')
    timestamp = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.sender.username}: {self.content[:50]}"
    
    def mark_read(self, user):
        if user != self.sender:
            self.read_by.add(user)
    
    def is_read_by(self, user):
        return self.read_by.filter(id=user.id).exists()
    
    def get_delivery_status(self, user=None):
        if user and user == self.sender:
            # For sender, show delivery status
            total_members = self.conversation.members.exclude(id=self.sender.id).count()
            read_count = self.read_by.exclude(id=self.sender.id).count()
            
            if read_count == total_members and total_members > 0:
                return 'read'
            elif read_count > 0:
                return 'delivered'
            else:
                return 'sent'
        return None

class MessageReaction(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.emoji}"

class MessageActivity(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('edited', 'Edited'),
        ('deleted', 'Deleted'),
        ('reacted', 'Reacted'),
        ('forwarded', 'Forwarded'),
    ]
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} {self.action} message {self.message.id}"

class ConversationSettings(models.Model):
    conversation = models.OneToOneField(Conversation, on_delete=models.CASCADE, related_name='settings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notifications_enabled = models.BooleanField(default=True)
    sound_enabled = models.BooleanField(default=True)
    custom_name = models.CharField(max_length=100, blank=True)
    
    class Meta:
        unique_together = ['conversation', 'user']
    
    def __str__(self):
        return f"{self.user.username} settings for {self.conversation.name}"

class GroupAction(models.Model):
    ACTION_CHOICES = [
        ('created', 'Group Created'),
        ('renamed', 'Group Renamed'),
        ('description_changed', 'Description Changed'),
        ('member_added', 'Member Added'),
        ('member_removed', 'Member Removed'),
        ('admin_added', 'Admin Added'),
        ('admin_removed', 'Admin Removed'),
        ('visibility_changed', 'Visibility Changed'),
        ('deleted', 'Group Deleted'),
    ]
    
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='group_actions')
    performed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='performed_actions')
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='target_actions')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.performed_by.username} {self.action} in {self.conversation.name}"