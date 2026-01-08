from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages as django_messages
from django.db.models import Q, Count, Max, Prefetch
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import Conversation, Message, MessageReaction, UserStatus, MessageActivity
from .permissions import can_message_user, can_view_conversation, can_delete_message, get_messageable_users
from permissions.decorators import require_permission, require_role

@require_permission('messaging', 'view')
def messaging_home(request):
    # Get or create user status
    try:
        UserStatus.objects.get_or_create(user=request.user, defaults={'is_online': True})
    except:
        pass
    
    conversations = request.user.conversations.select_related('created_by').prefetch_related(
        'members'
    ).annotate(
        last_msg_time=Max('messages__timestamp')
    ).order_by('-last_msg_time')
    
    # Calculate unread for each conversation
    conv_list = []
    for conv in conversations:
        # Query unread messages without using prefetched sliced queryset
        unread = Message.objects.filter(
            conversation=conv
        ).exclude(sender=request.user).exclude(read_by=request.user).exclude(deleted_for=request.user).count()
        
        # Get last message separately
        last_msg = Message.objects.filter(conversation=conv).order_by('-timestamp').first()
        other_user = conv.get_other_user(request.user) if not conv.is_group else None
        
        conv_list.append({
            'conversation': conv,
            'unread': unread,
            'last_message': last_msg,
            'other_user': other_user,
            'is_pinned': conv.pinned_by.filter(id=request.user.id).exists()
        })
    
    # Sort: pinned first, then by last message time
    conv_list.sort(key=lambda x: (not x['is_pinned'], -(x['conversation'].updated_at.timestamp() if x['conversation'].updated_at else 0)))
    
    return render(request, 'messaging/home.html', {'conversations': conv_list})

@require_permission('messaging', 'group')
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        member_ids = request.POST.getlist('members')
        
        if not name or not member_ids:
            django_messages.error(request, 'Group name and members are required')
            return redirect('messaging:create_group')
        
        conv = Conversation.objects.create(name=name, created_by=request.user, is_group=True)
        conv.members.add(request.user)
        conv.members.add(*User.objects.filter(id__in=member_ids))
        
        django_messages.success(request, f'Group "{name}" created')
        return redirect('messaging:chat', conversation_id=conv.id)
    
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'messaging/create_group.html', {'users': users})

@require_permission('messaging', 'send')
def start_chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Check RBAC permission
    if not can_message_user(request.user, other_user):
        django_messages.error(request, 'You do not have permission to message this user')
        return redirect('messaging:home')
    
    conv = Conversation.objects.filter(
        is_group=False,
        members=request.user
    ).filter(members=other_user).first()
    
    if not conv:
        conv = Conversation.objects.create(
            name=f"{request.user.username} & {other_user.username}",
            created_by=request.user,
            is_group=False
        )
        conv.members.add(request.user, other_user)
    
    return redirect('messaging:chat', conversation_id=conv.id)

@require_permission('messaging', 'send')
def start_user_chat(request, user_id):
    """Start chat with a team user"""
    other_user = get_object_or_404(User, id=user_id)
    
    if not can_message_user(request.user, other_user):
        django_messages.error(request, 'You do not have permission to message this user')
        return redirect('messaging:home')
    
    conv = Conversation.objects.filter(
        is_group=False,
        members=request.user
    ).filter(members=other_user).first()
    
    if not conv:
        conv = Conversation.objects.create(
            name=f"{request.user.username} & {other_user.username}",
            created_by=request.user,
            is_group=False
        )
        conv.members.add(request.user, other_user)
    
    return redirect('messaging:chat', conversation_id=conv.id)

@require_role('superadmin', 'admin', 'subadmin', 'staff')
def start_supplier_chat(request, supplier_id):
    """Start chat with a supplier"""
    from supplier.models import ListModel as SupplierModel
    from audit.models import AuditLog
    
    supplier = get_object_or_404(SupplierModel, id=supplier_id)
    
    # Find or create user for this supplier
    supplier_user = None
    if supplier.supplier_contact:
        supplier_user = User.objects.filter(username=supplier.supplier_contact).first()
    
    if not supplier_user:
        username = f"supplier_{supplier.id}"
        supplier_user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': supplier.supplier_name.split()[0] if supplier.supplier_name else 'Supplier',
                'last_name': ' '.join(supplier.supplier_name.split()[1:]) if supplier.supplier_name and len(supplier.supplier_name.split()) > 1 else '',
                'email': supplier.supplier_contact or f'{username}@supplier.local',
                'is_active': True
            }
        )
    
    conv = Conversation.objects.filter(
        is_group=False,
        members=request.user
    ).filter(members=supplier_user).first()
    
    if not conv:
        conv = Conversation.objects.create(
            name=f"{request.user.username} & {supplier.supplier_name}",
            created_by=request.user,
            is_group=False
        )
        conv.members.add(request.user, supplier_user)
    
    try:
        AuditLog.objects.create(
            user=request.user,
            action='opened_message_thread',
            module='messaging',
            details=f'Opened message thread with supplier {supplier.supplier_name} (ID: {supplier_id})',
            ip_address=request.META.get('REMOTE_ADDR')
        )
    except:
        pass
    
    return redirect('messaging:chat', conversation_id=conv.id)

@require_role('superadmin', 'admin', 'subadmin', 'staff')
def start_customer_chat(request, customer_id):
    from customer.models import ListModel as CustomerModel
    from audit.models import AuditLog
    
    customer = get_object_or_404(CustomerModel, id=customer_id)
    
    # Find or create user for this customer
    customer_user = None
    if customer.customer_contact:
        customer_user = User.objects.filter(username=customer.customer_contact).first()
    
    if not customer_user:
        # Create virtual user for customer
        username = f"customer_{customer.id}"
        customer_user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': customer.customer_name.split()[0] if customer.customer_name else 'Customer',
                'last_name': ' '.join(customer.customer_name.split()[1:]) if customer.customer_name and len(customer.customer_name.split()) > 1 else '',
                'email': customer.customer_contact or f'{username}@customer.local',
                'is_active': True
            }
        )
    
    # Find or create conversation
    conv = Conversation.objects.filter(
        is_group=False,
        members=request.user
    ).filter(members=customer_user).first()
    
    if not conv:
        conv = Conversation.objects.create(
            name=f"{request.user.username} & {customer.customer_name}",
            created_by=request.user,
            is_group=False
        )
        conv.members.add(request.user, customer_user)
    
    # Audit log
    try:
        AuditLog.objects.create(
            user=request.user,
            action='opened_message_thread',
            module='messaging',
            details=f'Opened message thread with customer {customer.customer_name} (ID: {customer_id})',
            ip_address=request.META.get('REMOTE_ADDR')
        )
    except:
        pass
    
    return redirect('messaging:chat', conversation_id=conv.id)

@require_permission('messaging', 'view')
def chat(request, conversation_id):
    conv = get_object_or_404(Conversation, id=conversation_id)
    
    # Check RBAC permission
    if not can_view_conversation(request.user, conv):
        django_messages.error(request, 'You do not have permission to view this conversation')
        return redirect('messaging:home')
    
    # Handle simple form POST (non-AJAX) for sending a message
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            msg = Message.objects.create(
                conversation=conv,
                sender=request.user,
                content=content
            )
            conv.updated_at = timezone.now()
            conv.save()
            MessageActivity.objects.create(message=msg, user=request.user, action='created')
            return redirect('messaging:chat', conversation_id=conv.id)
        else:
            django_messages.warning(request, 'Cannot send an empty message')
            return redirect('messaging:chat', conversation_id=conv.id)

    messages_list = conv.messages.exclude(deleted_for=request.user).select_related('sender', 'reply_to__sender').prefetch_related('reactions__user', 'read_by', 'is_starred_by').order_by('timestamp')
    
    # Mark as read
    for msg in messages_list:
        if msg.sender != request.user:
            msg.mark_read(request.user)
    
    other_user = conv.get_other_user(request.user) if not conv.is_group else None
    
    context = {
        'conversation': conv,
        'messages': messages_list,
        'other_user': other_user,
        'is_pinned': conv.pinned_by.filter(id=request.user.id).exists()
    }
    return render(request, 'messaging/chat_enhanced.html', context)

@require_permission('messaging', 'view')
def user_list(request):
    search = request.GET.get('search', '')
    users = get_messageable_users(request.user)
    
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search))
    
    # Add status info
    user_list = []
    for user in users:
        status = UserStatus.objects.filter(user=user).first()
        user_list.append({
            'user': user,
            'is_online': status.is_online if status else False,
            'last_seen': status.last_seen if status else None
        })
    
    return render(request, 'messaging/user_list.html', {'users': user_list, 'search': search})

@login_required
@require_permission('messaging', 'send')
@require_http_methods(["POST"])
def send_message_api(request, conversation_id):
    conv = get_object_or_404(Conversation, id=conversation_id)
    
    if not can_view_conversation(request.user, conv):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    import json
    data = json.loads(request.body)
    content = data.get('content', '').strip()
    reply_to_id = data.get('reply_to')
    
    if not content:
        return JsonResponse({'error': 'Content required'}, status=400)
    
    msg = Message.objects.create(
        conversation=conv,
        sender=request.user,
        content=content,
        reply_to_id=reply_to_id if reply_to_id else None
    )
    
    conv.updated_at = timezone.now()
    conv.save()
    
    MessageActivity.objects.create(message=msg, user=request.user, action='created')
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': msg.id,
            'sender': msg.sender.username,
            'sender_id': msg.sender.id,
            'content': msg.content,
            'timestamp': msg.timestamp.strftime('%H:%M'),
            'is_mine': True,
            'reply_to': {'id': msg.reply_to.id, 'content': msg.reply_to.content[:50]} if msg.reply_to else None
        }
    })

@require_permission('messaging', 'view')
def get_messages_api(request, conversation_id):
    conv = get_object_or_404(Conversation, id=conversation_id, members=request.user)
    messages_list = conv.messages.select_related('sender').order_by('-timestamp')[:50]
    
    data = [{
        'id': m.id,
        'sender': m.sender.username,
        'content': m.content,
        'timestamp': m.timestamp.strftime('%H:%M'),
        'is_mine': m.sender == request.user
    } for m in reversed(messages_list)]
    
    return JsonResponse({'messages': data})

@login_required
@require_permission('messaging', 'delete')
@require_http_methods(["POST"])
def delete_message(request, message_id):
    msg = get_object_or_404(Message, id=message_id)
    
    if not can_delete_message(request.user, msg):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    import json
    data = json.loads(request.body)
    delete_for_everyone = data.get('delete_for_everyone', False)
    
    if delete_for_everyone and msg.sender == request.user:
        # Delete for everyone
        msg.delete()
        MessageActivity.objects.create(message=msg, user=request.user, action='deleted', details='Deleted for everyone')
    else:
        # Soft delete - just for current user
        msg.deleted_for.add(request.user)
        MessageActivity.objects.create(message=msg, user=request.user, action='deleted', details='Deleted for me')
    
    return JsonResponse({'success': True})

@login_required
@require_permission('messaging', 'view')
@require_http_methods(["POST"])
def react_message(request, message_id):
    msg = get_object_or_404(Message, id=message_id)
    
    if not can_view_conversation(request.user, msg.conversation):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    import json
    data = json.loads(request.body)
    emoji = data.get('emoji', '👍')
    
    reaction, created = MessageReaction.objects.get_or_create(message=msg, user=request.user, defaults={'emoji': emoji})
    if not created:
        if reaction.emoji == emoji:
            # Remove reaction if same emoji
            reaction.delete()
            return JsonResponse({'success': True, 'removed': True})
        else:
            reaction.emoji = emoji
            reaction.save()
    
    MessageActivity.objects.create(message=msg, user=request.user, action='reacted', details=emoji)
    
    # Get all reactions for this message
    reactions = {}
    for r in msg.reactions.all():
        if r.emoji not in reactions:
            reactions[r.emoji] = []
        reactions[r.emoji].append(r.user.username)
    
    return JsonResponse({'success': True, 'emoji': emoji, 'reactions': reactions})


def send_guest_message(request):
    """Handle messages from guest users and send to team members"""
    if request.method == 'POST':
        name = request.POST.get('name', 'Anonymous')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', 'Guest Inquiry')
        message_text = request.POST.get('message', '')
        
        system_user, created = User.objects.get_or_create(
            username='system_guest_messages',
            defaults={
                'email': 'system@multistock.com',
                'first_name': 'Guest',
                'last_name': 'Messages',
                'is_active': True
            }
        )
        
        team_users = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True)).distinct()
        
        if team_users.exists():
            formatted_message = f"""🔔 New Guest Message

From: {name}
Email: {email}
Subject: {subject}

Message:
{message_text}

---
This message was sent via the contact form."""
            
            messages_sent = 0
            for team_user in team_users:
                try:
                    existing_conv = Conversation.objects.filter(
                        is_group=False,
                        members=system_user
                    ).filter(members=team_user).first()
                    
                    if existing_conv:
                        conv = existing_conv
                    else:
                        conv = Conversation.objects.create(
                            name=f'Guest Messages - {team_user.username}',
                            created_by=system_user,
                            is_group=False
                        )
                        conv.members.add(system_user, team_user)
                    
                    Message.objects.create(
                        conversation=conv,
                        sender=system_user,
                        content=formatted_message
                    )
                    
                    conv.updated_at = timezone.now()
                    conv.save()
                    messages_sent += 1
                except:
                    continue
            
            if messages_sent > 0:
                django_messages.success(request, f'Thank you! Your message has been sent to our team.')
            else:
                django_messages.error(request, 'Error sending message. Please try again.')
        else:
            django_messages.warning(request, 'Message received. Our team will contact you.')
        
        return redirect('contact')
    
    return redirect('contact')