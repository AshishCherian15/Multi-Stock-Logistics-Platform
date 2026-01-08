from permissions.decorators import get_user_role

def can_message_user(from_user, to_user):
    """Check if from_user can message to_user based on RBAC"""
    from_role = get_user_role(from_user)
    to_role = get_user_role(to_user)
    
    # Superadmin can message anyone
    if from_role == 'superadmin':
        return True
    
    # Admin/Sub-admin/Manager can message team + customers
    if from_role in ['admin', 'admin', 'manager']:
        if to_role in ['admin', 'admin', 'manager', 'staff', 'user']:
            return True
    
    # Staff can message team + assigned users
    if from_role == 'staff':
        if to_role in ['admin', 'admin', 'manager', 'staff', 'user']:
            return True
    
    # Users can message staff/admin (support chat)
    if from_role == 'user':
        if to_role in ['superadmin', 'admin', 'manager', 'staff']:
            return True
    
    return False

def can_view_conversation(user, conversation):
    """Check if user can view conversation"""
    return conversation.members.filter(id=user.id).exists()

def can_delete_message(user, message):
    """Check if user can delete message"""
    user_role = get_user_role(user)
    
    # Sender can always delete their own message
    if message.sender == user:
        return True
    
    # Superadmin can delete any message
    if user_role == 'superadmin':
        return True
    
    # Admin can delete messages in conversations they're part of
    if user_role == 'admin' and message.conversation.members.filter(id=user.id).exists():
        return True
    
    return False

def get_messageable_users(user):
    """Get list of users that current user can message"""
    from django.contrib.auth.models import User
    
    user_role = get_user_role(user)
    
    # Superadmin can message anyone
    if user_role == 'superadmin':
        return User.objects.exclude(id=user.id).filter(is_active=True)
    
    # Admin/Manager/Staff can message team + customers
    if user_role in ['admin', 'admin', 'manager', 'staff']:
        return User.objects.exclude(id=user.id).filter(is_active=True)
    
    # Regular users can message staff/admin
    return User.objects.exclude(id=user.id).filter(is_active=True, is_staff=True)
