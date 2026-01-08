from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from django.utils import timezone
from .models import Conversation, Message, UserStatus
from .permissions import can_view_conversation, can_delete_message
from permissions.decorators import require_permission, get_user_role
import json

@login_required
@require_http_methods(["GET"])
def load_messages_api(request, conversation_id):
    conv = get_object_or_404(Conversation, id=conversation_id)
    
    if not can_view_conversation(request.user, conv):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    offset = int(request.GET.get('offset', 0))
    limit = 50
    
    messages = conv.messages.exclude(deleted_for=request.user).select_related('sender', 'reply_to__sender').prefetch_related('reactions__user', 'read_by').order_by('-timestamp')[offset:offset+limit]
    
    data = []
    for msg in reversed(list(messages)):
        reactions = {}
        for r in msg.reactions.all():
            if r.emoji not in reactions:
                reactions[r.emoji] = []
            reactions[r.emoji].append({'user': r.user.username, 'user_id': r.user.id})
        
        data.append({
            'id': msg.id,
            'sender': msg.sender.username,
            'sender_id': msg.sender.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'full_timestamp': msg.timestamp.isoformat(),
            'is_mine': msg.sender == request.user,
            'is_read': msg.is_read_by(request.user),
            'read_by_count': msg.read_by.count(),
        'delivery_status': msg.get_delivery_status(request.user) if msg.sender == request.user else None,
            'is_edited': msg.is_edited,
            'is_pinned': msg.is_pinned,
            'is_starred': msg.is_starred_by.filter(id=request.user.id).exists(),
            'reactions': reactions,
            'reply_to': {
                'id': msg.reply_to.id,
                'sender': msg.reply_to.sender.username,
                'content': msg.reply_to.content[:50]
            } if msg.reply_to else None
        })
    
    return JsonResponse({
        'success': True,
        'messages': data,
        'has_more': conv.messages.exclude(deleted_for=request.user).count() > offset + limit
    })

@login_required
@require_http_methods(["POST"])
def edit_message_api(request, message_id):
    msg = get_object_or_404(Message, id=message_id, sender=request.user)
    
    data = json.loads(request.body)
    new_content = data.get('content', '').strip()
    
    if not new_content:
        return JsonResponse({'error': 'Content required'}, status=400)
    
    # Check if message is within 15 minutes
    if (timezone.now() - msg.timestamp).total_seconds() > 900:
        return JsonResponse({'error': 'Cannot edit messages older than 15 minutes'}, status=400)
    
    msg.content = new_content
    msg.is_edited = True
    msg.edited_at = timezone.now()
    msg.save()
    
    from .models import MessageActivity
    MessageActivity.objects.create(message=msg, user=request.user, action='edited')
    
    return JsonResponse({'success': True, 'content': new_content, 'edited_at': msg.edited_at.strftime('%H:%M')})

@login_required
@require_http_methods(["POST"])
def star_message_api(request, message_id):
    msg = get_object_or_404(Message, id=message_id)
    
    if not can_view_conversation(request.user, msg.conversation):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if msg.is_starred_by.filter(id=request.user.id).exists():
        msg.is_starred_by.remove(request.user)
        is_starred = False
    else:
        msg.is_starred_by.add(request.user)
        is_starred = True
    
    return JsonResponse({'success': True, 'is_starred': is_starred})

@login_required
@require_http_methods(["POST"])
def pin_message_api(request, message_id):
    msg = get_object_or_404(Message, id=message_id)
    
    if not can_view_conversation(request.user, msg.conversation):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin', 'manager']:
        return JsonResponse({'error': 'Only admins can pin messages'}, status=403)
    
    msg.is_pinned = not msg.is_pinned
    msg.save()
    
    return JsonResponse({'success': True, 'is_pinned': msg.is_pinned})

@login_required
@require_http_methods(["POST"])
def forward_message_api(request, message_id):
    msg = get_object_or_404(Message, id=message_id)
    
    if not can_view_conversation(request.user, msg.conversation):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    data = json.loads(request.body)
    target_conv_id = data.get('conversation_id')
    
    target_conv = get_object_or_404(Conversation, id=target_conv_id)
    
    if not can_view_conversation(request.user, target_conv):
        return JsonResponse({'error': 'Permission denied for target conversation'}, status=403)
    
    new_msg = Message.objects.create(
        conversation=target_conv,
        sender=request.user,
        content=msg.content,
        forwarded_from=msg
    )
    
    from .models import MessageActivity
    MessageActivity.objects.create(message=new_msg, user=request.user, action='forwarded', details=f'From conversation {msg.conversation.id}')
    
    return JsonResponse({'success': True, 'message_id': new_msg.id})

@login_required
@require_http_methods(["GET"])
def search_messages_api(request):
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'error': 'Query too short'}, status=400)
    
    # Search in user's conversations only
    conversations = request.user.conversations.all()
    
    messages = Message.objects.filter(
        conversation__in=conversations,
        content__icontains=query
    ).exclude(deleted_for=request.user).select_related('sender', 'conversation').order_by('-timestamp')[:50]
    
    results = []
    for msg in messages:
        results.append({
            'message_id': msg.id,
            'conversation_id': msg.conversation.id,
            'conversation_name': msg.conversation.name,
            'sender': msg.sender.username,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M'),
            'preview': msg.content[:100]
        })
    
    return JsonResponse({'success': True, 'results': results, 'count': len(results)})

@login_required
@require_http_methods(["POST"])
def update_status_api(request):
    data = json.loads(request.body)
    is_online = data.get('is_online', True)
    
    status, created = UserStatus.objects.get_or_create(user=request.user)
    status.is_online = is_online
    status.last_seen = timezone.now()
    status.save()
    
    return JsonResponse({'success': True, 'is_online': is_online})

@login_required
@require_http_methods(["POST"])
def typing_indicator_api(request, conversation_id):
    conv = get_object_or_404(Conversation, id=conversation_id)
    
    if not can_view_conversation(request.user, conv):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    data = json.loads(request.body)
    is_typing = data.get('is_typing', False)
    
    status, created = UserStatus.objects.get_or_create(user=request.user)
    status.is_typing_in = conv if is_typing else None
    status.save()
    
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def pin_conversation_api(request, conversation_id):
    conv = get_object_or_404(Conversation, id=conversation_id)
    
    if not can_view_conversation(request.user, conv):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if conv.pinned_by.filter(id=request.user.id).exists():
        conv.pinned_by.remove(request.user)
        is_pinned = False
    else:
        conv.pinned_by.add(request.user)
        is_pinned = True
    
    return JsonResponse({'success': True, 'is_pinned': is_pinned})

@login_required
@require_http_methods(["GET"])
def user_profile_api(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    status = UserStatus.objects.filter(user=user).first()
    user_role = get_user_role(user)
    
    # Check if conversation exists
    conv = Conversation.objects.filter(
        is_group=False,
        members=request.user
    ).filter(members=user).first()
    
    return JsonResponse({
        'success': True,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': user.get_full_name() or user.username,
            'role': user_role,
            'is_online': status.is_online if status else False,
            'last_seen': status.last_seen.isoformat() if status and status.last_seen else None,
            'conversation_id': conv.id if conv else None
        }
    })

@login_required
@require_http_methods(["GET"])
def unread_count_api(request):
    conversations = request.user.conversations.all()
    
    total_unread = 0
    for conv in conversations:
        unread = conv.messages.exclude(sender=request.user).exclude(read_by=request.user).exclude(deleted_for=request.user).count()
        total_unread += unread
    
    return JsonResponse({'success': True, 'unread_count': total_unread})

@login_required
@require_http_methods(["GET"])
def get_conversation_info_api(request, conversation_id):
    """Get detailed conversation information"""
    conv = get_object_or_404(Conversation, id=conversation_id)
    
    if not can_view_conversation(request.user, conv):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get members with their status
    members = []
    for member in conv.members.all():
        status = UserStatus.objects.filter(user=member).first()
        members.append({
            'id': member.id,
            'username': member.username,
            'first_name': member.first_name,
            'last_name': member.last_name,
            'is_online': status.is_online if status else False,
            'last_seen': status.last_seen.isoformat() if status and status.last_seen else None,
            'is_admin': conv.admins.filter(id=member.id).exists() if conv.is_group else False,
            'is_creator': member == conv.created_by
        })
    
    # Get typing users
    typing_users = UserStatus.objects.filter(
        is_typing_in=conv
    ).exclude(user=request.user).values_list('user__username', flat=True)
    
    data = {
        'id': conv.id,
        'name': conv.name,
        'description': conv.description,
        'is_group': conv.is_group,
        'visibility': conv.visibility if conv.is_group else None,
        'created_by': conv.created_by.username,
        'created_at': conv.created_at.isoformat(),
        'members': members,
        'member_count': conv.members.count(),
        'is_admin': conv.is_admin(request.user) if conv.is_group else False,
        'is_muted': conv.muted_by.filter(id=request.user.id).exists(),
        'is_pinned': conv.pinned_by.filter(id=request.user.id).exists(),
        'is_archived': conv.archived_by.filter(id=request.user.id).exists(),
        'typing_users': list(typing_users),
        'unread_count': conv.unread_count(request.user)
    }
    
    return JsonResponse(data)

@login_required
@require_http_methods(["POST"])
def mark_messages_read_api(request, conversation_id):
    """Mark multiple messages as read"""
    conv = get_object_or_404(Conversation, id=conversation_id)
    
    if not can_view_conversation(request.user, conv):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    data = json.loads(request.body)
    message_ids = data.get('message_ids', [])
    
    if message_ids:
        messages = Message.objects.filter(
            id__in=message_ids,
            conversation=conv
        ).exclude(sender=request.user)
        
        for msg in messages:
            msg.mark_read(request.user)
    else:
        # Mark all unread messages as read
        messages = conv.messages.exclude(sender=request.user).exclude(read_by=request.user)
        for msg in messages:
            msg.mark_read(request.user)
    
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["GET"])
def get_online_users_api(request):
    """Get list of online users based on role permissions"""
    online_statuses = UserStatus.objects.filter(
        is_online=True
    ).select_related('user')
    
    # Filter based on role permissions
    user_is_team = request.user.is_staff or request.user.is_superuser
    
    users = []
    for status in online_statuses:
        user = status.user
        target_is_team = user.is_staff or user.is_superuser
        
        # Apply role-based visibility
        if user_is_team or not target_is_team:
            users.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_online': True,
                'last_seen': status.last_seen.isoformat() if status.last_seen else None
            })
    
    return JsonResponse({'online_users': users})

@login_required
@require_http_methods(["GET"])
def get_message_delivery_info_api(request, message_id):
    """Get message delivery and read receipt information"""
    msg = get_object_or_404(Message, id=message_id)
    
    if not can_view_conversation(request.user, msg.conversation):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Only sender can see delivery info
    if msg.sender != request.user:
        return JsonResponse({'error': 'Only sender can view delivery info'}, status=403)
    
    conversation_members = msg.conversation.members.exclude(id=msg.sender.id)
    read_by = []
    delivered_to = []
    
    for member in conversation_members:
        if msg.read_by.filter(id=member.id).exists():
            read_by.append({
                'user_id': member.id,
                'username': member.username,
                'status': 'read'
            })
        else:
            delivered_to.append({
                'user_id': member.id,
                'username': member.username,
                'status': 'delivered'
            })
    
    delivery_status = 'sent'
    if len(read_by) == len(conversation_members) and len(conversation_members) > 0:
        delivery_status = 'read'
    elif len(read_by) > 0:
        delivery_status = 'delivered'
    
    return JsonResponse({
        'message_id': msg.id,
        'delivery_status': delivery_status,
        'read_by': read_by,
        'delivered_to': delivered_to,
        'total_recipients': len(conversation_members),
        'read_count': len(read_by)
    })

@login_required
@require_http_methods(["GET"])
def get_notifications_api(request):
    """Get recent notifications from conversations"""
    limit = int(request.GET.get('limit', 10))
    
    notifications = []
    
    # Get conversations with unread messages (excluding muted/archived)
    conversations = request.user.conversations.exclude(
        muted_by=request.user
    ).exclude(
        archived_by=request.user
    )
    
    for conv in conversations:
        unread_messages = conv.messages.exclude(
            sender=request.user
        ).exclude(
            read_by=request.user
        ).exclude(
            deleted_for=request.user
        ).order_by('-timestamp')[:3]
        
        for msg in unread_messages:
            notifications.append({
                'id': f'msg_{msg.id}',
                'type': 'message',
                'title': f'New message from {msg.sender.username}',
                'content': msg.content[:100],
                'timestamp': msg.timestamp.isoformat(),
                'conversation_id': conv.id,
                'conversation_name': conv.name,
                'sender': msg.sender.username,
                'is_group': conv.is_group
            })
    
    # Sort by timestamp and limit
    notifications.sort(key=lambda x: x['timestamp'], reverse=True)
    notifications = notifications[:limit]
    
    return JsonResponse({
        'notifications': notifications,
        'total_unread': sum(conv.unread_count(request.user) for conv in conversations)
    })

@login_required
@require_http_methods(["POST"])
def bulk_message_action_api(request):
    """Perform bulk actions on messages"""
    data = json.loads(request.body)
    message_ids = data.get('message_ids', [])
    action = data.get('action')
    
    if not message_ids or not action:
        return JsonResponse({'error': 'Message IDs and action required'}, status=400)
    
    messages = Message.objects.filter(
        id__in=message_ids,
        conversation__members=request.user
    )
    
    success_count = 0
    
    for msg in messages:
        if not can_view_conversation(request.user, msg.conversation):
            continue
            
        if action == 'delete':
            msg.deleted_for.add(request.user)
            success_count += 1
        elif action == 'star':
            if msg.is_starred_by.filter(id=request.user.id).exists():
                msg.is_starred_by.remove(request.user)
            else:
                msg.is_starred_by.add(request.user)
            success_count += 1
        elif action == 'pin' and msg.conversation.is_group and msg.conversation.is_admin(request.user):
            msg.is_pinned = not msg.is_pinned
            msg.save()
            success_count += 1
    
    return JsonResponse({
        'success': True,
        'action': action,
        'processed': success_count,
        'total': len(message_ids)
    })
