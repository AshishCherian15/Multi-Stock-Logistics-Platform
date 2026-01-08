from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages as django_messages
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from .models import Conversation, GroupAction, ConversationSettings
from .permissions import can_view_conversation
import json

@login_required
def create_group_advanced(request):
    """Advanced group creation with role-based member filtering"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        visibility = request.POST.get('visibility', 'public')
        member_ids = request.POST.getlist('members')
        
        if not name:
            django_messages.error(request, 'Group name is required')
            return redirect('messaging:create_group_advanced')
        
        # Create group
        conv = Conversation.objects.create(
            name=name,
            description=description,
            visibility=visibility,
            created_by=request.user,
            is_group=True
        )
        
        # Add creator as member and admin
        conv.members.add(request.user)
        conv.admins.add(request.user)
        
        # Add selected members with role validation
        for member_id in member_ids:
            try:
                user = User.objects.get(id=member_id)
                conv.add_member(user, request.user)
                
                # Log action
                GroupAction.objects.create(
                    conversation=conv,
                    performed_by=request.user,
                    target_user=user,
                    action='member_added',
                    new_value=user.username
                )
            except (User.DoesNotExist, ValidationError) as e:
                django_messages.warning(request, f'Could not add user: {str(e)}')
        
        # Log group creation
        GroupAction.objects.create(
            conversation=conv,
            performed_by=request.user,
            action='created',
            new_value=name
        )
        
        django_messages.success(request, f'Group "{name}" created successfully')
        return redirect('messaging:chat', conversation_id=conv.id)
    
    # Get available users based on role
    user_is_team = request.user.is_staff or request.user.is_superuser
    
    if user_is_team:
        # Team can see all users
        available_users = User.objects.exclude(id=request.user.id).filter(is_active=True)
    else:
        # Customers can only see other customers
        available_users = User.objects.exclude(id=request.user.id).filter(
            is_active=True,
            is_staff=False,
            is_superuser=False
        )
    
    context = {
        'available_users': available_users,
        'user_is_team': user_is_team,
        'visibility_choices': Conversation.VISIBILITY_CHOICES
    }
    return render(request, 'messaging/create_group_advanced.html', context)

@login_required
def group_settings(request, conversation_id):
    """Group settings and management"""
    conv = get_object_or_404(Conversation, id=conversation_id, is_group=True)
    
    if not can_view_conversation(request.user, conv):
        django_messages.error(request, 'Permission denied')
        return redirect('messaging:home')
    
    is_admin = conv.is_admin(request.user)
    
    if request.method == 'POST' and is_admin:
        action = request.POST.get('action')
        
        if action == 'update_info':
            old_name = conv.name
            old_desc = conv.description
            
            conv.name = request.POST.get('name', conv.name)
            conv.description = request.POST.get('description', conv.description)
            conv.visibility = request.POST.get('visibility', conv.visibility)
            conv.save()
            
            # Log changes
            if old_name != conv.name:
                GroupAction.objects.create(
                    conversation=conv,
                    performed_by=request.user,
                    action='renamed',
                    old_value=old_name,
                    new_value=conv.name
                )
            
            if old_desc != conv.description:
                GroupAction.objects.create(
                    conversation=conv,
                    performed_by=request.user,
                    action='description_changed',
                    old_value=old_desc,
                    new_value=conv.description
                )
            
            django_messages.success(request, 'Group updated successfully')
        
        elif action == 'add_member':
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                conv.add_member(user, request.user)
                
                GroupAction.objects.create(
                    conversation=conv,
                    performed_by=request.user,
                    target_user=user,
                    action='member_added',
                    new_value=user.username
                )
                
                django_messages.success(request, f'{user.username} added to group')
            except (User.DoesNotExist, ValidationError) as e:
                django_messages.error(request, str(e))
        
        elif action == 'remove_member':
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                conv.remove_member(user, request.user)
                
                GroupAction.objects.create(
                    conversation=conv,
                    performed_by=request.user,
                    target_user=user,
                    action='member_removed',
                    new_value=user.username
                )
                
                django_messages.success(request, f'{user.username} removed from group')
            except (User.DoesNotExist, ValidationError) as e:
                django_messages.error(request, str(e))
        
        elif action == 'toggle_admin':
            user_id = request.POST.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                if conv.admins.filter(id=user.id).exists():
                    conv.admins.remove(user)
                    action_type = 'admin_removed'
                else:
                    conv.admins.add(user)
                    action_type = 'admin_added'
                
                GroupAction.objects.create(
                    conversation=conv,
                    performed_by=request.user,
                    target_user=user,
                    action=action_type,
                    new_value=user.username
                )
                
                django_messages.success(request, f'Admin status updated for {user.username}')
            except User.DoesNotExist:
                django_messages.error(request, 'User not found')
        
        return redirect('messaging:group_settings', conversation_id=conv.id)
    
    # Get available users to add
    user_is_team = request.user.is_staff or request.user.is_superuser
    creator_is_team = conv.created_by.is_staff or conv.created_by.is_superuser
    
    if user_is_team and creator_is_team:
        # Team group - can add all users
        available_users = User.objects.exclude(
            id__in=conv.members.values_list('id', flat=True)
        ).filter(is_active=True)
    elif not user_is_team and not creator_is_team:
        # Customer group - can only add other customers
        available_users = User.objects.exclude(
            id__in=conv.members.values_list('id', flat=True)
        ).filter(is_active=True, is_staff=False, is_superuser=False)
    else:
        # Mixed - no additions allowed
        available_users = User.objects.none()
    
    # Get group actions (audit log)
    group_actions = conv.group_actions.select_related(
        'performed_by', 'target_user'
    ).order_by('-timestamp')[:20]
    
    context = {
        'conversation': conv,
        'is_admin': is_admin,
        'available_users': available_users,
        'group_actions': group_actions,
        'visibility_choices': Conversation.VISIBILITY_CHOICES
    }
    return render(request, 'messaging/group_settings.html', context)

@login_required
@require_http_methods(["POST"])
def toggle_conversation_pin(request, conversation_id):
    """Pin/unpin conversation"""
    conv = get_object_or_404(Conversation, id=conversation_id)
    
    if not can_view_conversation(request.user, conv):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if conv.pinned_by.filter(id=request.user.id).exists():
        conv.pinned_by.remove(request.user)
        pinned = False
    else:
        conv.pinned_by.add(request.user)
        pinned = True
    
    return JsonResponse({'success': True, 'pinned': pinned})

@login_required
@require_http_methods(["POST"])
def toggle_conversation_mute(request, conversation_id):
    """Mute/unmute conversation"""
    conv = get_object_or_404(Conversation, id=conversation_id)
    
    if not can_view_conversation(request.user, conv):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if conv.muted_by.filter(id=request.user.id).exists():
        conv.muted_by.remove(request.user)
        muted = False
    else:
        conv.muted_by.add(request.user)
        muted = True
    
    return JsonResponse({'success': True, 'muted': muted})

@login_required
@require_http_methods(["POST"])
def toggle_conversation_archive(request, conversation_id):
    """Archive/unarchive conversation"""
    conv = get_object_or_404(Conversation, id=conversation_id)
    
    if not can_view_conversation(request.user, conv):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    if conv.archived_by.filter(id=request.user.id).exists():
        conv.archived_by.remove(request.user)
        archived = False
    else:
        conv.archived_by.add(request.user)
        archived = True
    
    return JsonResponse({'success': True, 'archived': archived})

@login_required
def conversation_settings(request, conversation_id):
    """Individual conversation settings"""
    conv = get_object_or_404(Conversation, id=conversation_id)
    
    if not can_view_conversation(request.user, conv):
        django_messages.error(request, 'Permission denied')
        return redirect('messaging:home')
    
    settings, created = ConversationSettings.objects.get_or_create(
        conversation=conv,
        user=request.user,
        defaults={
            'notifications_enabled': True,
            'sound_enabled': True
        }
    )
    
    if request.method == 'POST':
        settings.notifications_enabled = request.POST.get('notifications') == 'on'
        settings.sound_enabled = request.POST.get('sound') == 'on'
        settings.custom_name = request.POST.get('custom_name', '')
        settings.save()
        
        django_messages.success(request, 'Settings updated')
        return redirect('messaging:chat', conversation_id=conv.id)
    
    context = {
        'conversation': conv,
        'settings': settings,
        'is_muted': conv.muted_by.filter(id=request.user.id).exists(),
        'is_pinned': conv.pinned_by.filter(id=request.user.id).exists(),
        'is_archived': conv.archived_by.filter(id=request.user.id).exists()
    }
    return render(request, 'messaging/conversation_settings.html', context)

@login_required
@require_http_methods(["POST"])
def delete_group(request, conversation_id):
    """Delete group (admin only)"""
    conv = get_object_or_404(Conversation, id=conversation_id, is_group=True)
    
    if not conv.is_admin(request.user):
        return JsonResponse({'error': 'Only admins can delete groups'}, status=403)
    
    data = json.loads(request.body)
    confirm = data.get('confirm', False)
    
    if not confirm:
        return JsonResponse({'error': 'Confirmation required'}, status=400)
    
    group_name = conv.name
    
    # Log deletion
    GroupAction.objects.create(
        conversation=conv,
        performed_by=request.user,
        action='deleted',
        old_value=group_name
    )
    
    conv.delete()
    
    return JsonResponse({'success': True, 'message': f'Group "{group_name}" deleted'})

@login_required
def group_list(request):
    """List all accessible groups"""
    user_is_team = request.user.is_staff or request.user.is_superuser
    
    # Get groups based on role and visibility
    if user_is_team:
        # Team can see public team groups and groups they're members of
        groups = Conversation.objects.filter(
            is_group=True
        ).filter(
            Q(members=request.user) |  # Member of group
            Q(created_by__is_staff=True, visibility='public') |  # Public team groups
            Q(created_by__is_superuser=True, visibility='public')
        ).distinct()
    else:
        # Customers can only see groups they're members of
        groups = request.user.conversations.filter(is_group=True)
    
    # Add metadata
    group_list = []
    for group in groups:
        group_list.append({
            'group': group,
            'member_count': group.members.count(),
            'is_admin': group.is_admin(request.user),
            'is_member': group.members.filter(id=request.user.id).exists(),
            'last_message': group.last_message(),
            'unread_count': group.unread_count(request.user)
        })
    
    context = {
        'groups': group_list,
        'user_is_team': user_is_team
    }
    return render(request, 'messaging/group_list.html', context)