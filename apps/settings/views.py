from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings as django_settings
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from datetime import datetime
from django.db import models
from .models import SystemSettings, MaintenanceMode, Announcement
from permissions.decorators import get_user_role

@login_required
def settings_page(request):
    user_role = get_user_role(request.user)
    maintenance_mode, _ = MaintenanceMode.objects.get_or_create(id=1)
    system_settings, _ = SystemSettings.objects.get_or_create(
        id=1,
        defaults={
            'company_name': 'MultiStock Logistics',
            'currency': 'INR',
            'timezone': 'Asia/Kolkata',
        }
    )
    # Lightweight per-user preferences stored in session
    user_prefs = {
        'language': request.session.get('settings_language', 'en'),
        'theme': request.session.get('settings_theme', 'light'),
        'items_per_page': int(request.session.get('settings_items', 25)),
        'notifications': {
            'email': request.session.get('notif_email', True),
            'order_updates': request.session.get('notif_order_updates', True),
            'stock_alerts': request.session.get('notif_stock_alerts', True),
        },
    }
    
    # Get active announcements for user's role
    announcements = Announcement.objects.filter(
        is_active=True,
        created_at__lte=timezone.now()
    ).filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gte=timezone.now())
    )
    
    # Filter by target roles
    user_announcements = []
    for ann in announcements:
        if not ann.target_roles or user_role in ann.target_roles:
            user_announcements.append(ann)
    
    context = {
        'user_role': user_role,
        'maintenance_mode': maintenance_mode,
        'system_settings': system_settings,
        'user_prefs': user_prefs,
        'allowed_roles_options': ['superadmin', 'admin', 'supervisor', 'staff', 'customer'],
        'announcements': user_announcements[:5],  # Show latest 5
    }
    return render(request, 'settings/role_based_settings.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('full_name', '').split()[0] if request.POST.get('full_name') else ''
        user.email = request.POST.get('email', '')
        user.save()
        messages.success(request, 'Profile updated successfully')
    return redirect('settings_page')

@login_required
def change_password(request):
    if request.method == 'POST':
        from django.contrib.auth import update_session_auth_hash
        user = request.user
        current = request.POST.get('current_password')
        new_pass = request.POST.get('new_password')
        confirm = request.POST.get('confirm_password')
        
        if user.check_password(current):
            if new_pass == confirm:
                user.set_password(new_pass)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully')
            else:
                messages.error(request, 'Passwords do not match')
        else:
            messages.error(request, 'Current password is incorrect')
    return redirect('settings_page')

@login_required
def update_notifications(request):
    if request.method == 'POST':
        request.session['notif_email'] = 'email_notifications' in request.POST
        request.session['notif_order_updates'] = 'order_updates' in request.POST
        request.session['notif_stock_alerts'] = 'stock_alerts' in request.POST
        messages.success(request, 'Notification preferences updated')
    return redirect('settings_page')

@login_required
def toggle_maintenance(request):
    user_role = get_user_role(request.user)
    if user_role != 'superadmin':
        messages.error(request, 'Permission denied')
        return redirect('settings_page')
    
    if request.method == 'POST':
        maintenance, created = MaintenanceMode.objects.get_or_create(id=1)
        maintenance.is_active = 'maintenance_mode' in request.POST
        maintenance.allowed_roles = request.POST.getlist('allowed_roles')
        maintenance.save()
        messages.success(request, 'Maintenance mode updated')
    return redirect('settings_page')

@login_required
def save_setting(request):
    if request.method != 'POST':
        return redirect('settings_page')

    form_type = request.POST.get('form_type')
    user_role = get_user_role(request.user)
    settings_obj, _ = SystemSettings.objects.get_or_create(id=1)

    if form_type == 'system':
        if user_role not in ['superadmin', 'admin']:
            messages.error(request, 'Permission denied')
            return redirect('settings_page')
        settings_obj.company_name = request.POST.get('company_name', settings_obj.company_name)
        settings_obj.currency = request.POST.get('currency', settings_obj.currency)
        settings_obj.timezone = request.POST.get('timezone', settings_obj.timezone)
        settings_obj.save()
        messages.success(request, 'System settings saved')
    elif form_type == 'preferences':
        request.session['settings_language'] = request.POST.get('language', 'en')
        request.session['settings_theme'] = request.POST.get('theme', 'light')
        request.session['settings_items'] = request.POST.get('items_per_page', 25)
        messages.success(request, 'Preferences updated')
    else:
        messages.info(request, 'No changes detected')

    return redirect('settings_page')

@login_required
def get_setting(request, key):
    from django.http import JsonResponse
    return JsonResponse({'key': key, 'value': ''})

@login_required
def system_status(request):
    return render(request, 'settings/system_status.html')

@login_required
def system_metrics_api(request):
    return JsonResponse({'status': 'ok'})

@login_required
def create_announcement(request):
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        priority = request.POST.get('priority', 'medium')
        target_roles = request.POST.getlist('target_roles')
        expires_at_raw = request.POST.get('expires_at')
        expires_at = None
        if expires_at_raw:
            parsed = parse_datetime(expires_at_raw)
            if not parsed:
                try:
                    parsed = datetime.fromisoformat(expires_at_raw)
                except ValueError:
                    parsed = None
            if parsed:
                expires_at = timezone.make_aware(parsed) if timezone.is_naive(parsed) else parsed
        
        announcement = Announcement.objects.create(
            title=title,
            message=message,
            priority=priority,
            target_roles=target_roles if target_roles else [],
            created_by=request.user,
            expires_at=expires_at
        )
        messages.success(request, 'Announcement created successfully')
        return redirect('settings_page')
    
    return JsonResponse({'success': False}, status=400)

@login_required
def get_announcements_api(request):
    user_role = get_user_role(request.user)
    announcements = Announcement.objects.filter(
        is_active=True,
        created_at__lte=timezone.now()
    ).filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gte=timezone.now())
    )
    
    results = []
    for ann in announcements:
        if not ann.target_roles or user_role in ann.target_roles:
            results.append({
                'id': ann.id,
                'title': ann.title,
                'message': ann.message,
                'priority': ann.priority,
                'created_at': ann.created_at.strftime('%b %d, %Y'),
                'created_by': ann.created_by.username
            })
    
    return JsonResponse({'announcements': results})

@login_required
def get_dashboard_announcements_api(request):
    user_role = get_user_role(request.user)
    
    # Get announcements created in last 24 hours that user hasn't dismissed
    from datetime import timedelta
    recent_time = timezone.now() - timedelta(hours=24)
    
    announcements = Announcement.objects.filter(
        is_active=True,
        created_at__gte=recent_time,
        created_at__lte=timezone.now()
    ).filter(
        models.Q(expires_at__isnull=True) | models.Q(expires_at__gte=timezone.now())
    )
    
    # Get dismissed announcements from session
    dismissed = request.session.get('dismissed_announcements', [])
    
    results = []
    for ann in announcements:
        if ann.id not in dismissed and (not ann.target_roles or user_role in ann.target_roles):
            results.append({
                'id': ann.id,
                'title': ann.title,
                'message': ann.message,
                'priority': ann.priority,
                'created_at': ann.created_at.strftime('%b %d, %Y %H:%M'),
                'created_by': ann.created_by.username
            })
    
    return JsonResponse({'announcements': results})

@login_required
def dismiss_announcement(request, announcement_id):
    dismissed = request.session.get('dismissed_announcements', [])
    if announcement_id not in dismissed:
        dismissed.append(announcement_id)
        request.session['dismissed_announcements'] = dismissed
    return JsonResponse({'success': True})

@login_required
def delete_announcement(request, announcement_id):
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        announcement = Announcement.objects.get(id=announcement_id)
        announcement.delete()
        return JsonResponse({'success': True})
    except Announcement.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Announcement not found'}, status=404)

@login_required
def update_announcement(request):
    user_role = get_user_role(request.user)
    if user_role not in ['superadmin', 'admin']:
        messages.error(request, 'Permission denied')
        return redirect('settings_page')
    
    if request.method == 'POST':
        announcement_id = request.POST.get('announcement_id')
        try:
            announcement = Announcement.objects.get(id=announcement_id)
            announcement.title = request.POST.get('title')
            announcement.message = request.POST.get('message')
            announcement.priority = request.POST.get('priority')
            announcement.save()
            messages.success(request, 'Announcement updated successfully')
        except Announcement.DoesNotExist:
            messages.error(request, 'Announcement not found')
    
    return redirect('settings_page')
