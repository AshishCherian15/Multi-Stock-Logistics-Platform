from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Notification, NotificationPreference

@login_required
def notification_center(request):
    category_filter = request.GET.get('category', '')
    type_filter = request.GET.get('type', '')
    
    notifications = request.user.notifications.filter(is_archived=False)
    if category_filter:
        notifications = notifications.filter(category=category_filter)
    if type_filter:
        notifications = notifications.filter(type=type_filter)
    
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page', 1)
    notifications_page = paginator.get_page(page)
    
    return render(request, 'notifications/center.html', {
        'notifications': notifications_page,
        'category_filter': category_filter,
        'type_filter': type_filter
    })

@login_required
def mark_read(request, notification_id):
    notif = get_object_or_404(Notification, id=notification_id, user=request.user)
    notif.is_read = True
    notif.read_at = timezone.now()
    notif.save()
    return JsonResponse({'success': True})

@login_required
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True, read_at=timezone.now())
    return JsonResponse({'success': True})

@login_required
def delete_notification(request, notification_id):
    notif = get_object_or_404(Notification, id=notification_id, user=request.user)
    notif.is_archived = True
    notif.save()
    return JsonResponse({'success': True})

@login_required
def unread_count_api(request):
    count = request.user.notifications.filter(is_read=False, is_archived=False).count()
    return JsonResponse({'count': count})

@login_required
def recent_notifications_api(request):
    limit = int(request.GET.get('limit', 5))
    notifications = request.user.notifications.filter(is_archived=False)[:limit]
    
    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.type,
        'category': n.category,
        'link': n.link,
        'icon': n.icon,
        'is_read': n.is_read,
        'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for n in notifications]
    
    return JsonResponse({'notifications': data})

@login_required
def preferences(request):
    prefs, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        prefs.email_enabled = request.POST.get('email_enabled') == 'on'
        prefs.push_enabled = request.POST.get('push_enabled') == 'on'
        prefs.stock_alerts = request.POST.get('stock_alerts') == 'on'
        prefs.order_updates = request.POST.get('order_updates') == 'on'
        prefs.message_notifications = request.POST.get('message_notifications') == 'on'
        prefs.system_notifications = request.POST.get('system_notifications') == 'on'
        prefs.save()
        return redirect('notifications:preferences')
    
    return render(request, 'notifications/preferences.html', {'preferences': prefs})

def create_notification(user, title, message, type='info', category='system', link='', icon=''):
    """Helper function to create notifications"""
    return Notification.objects.create(
        user=user,
        title=title,
        message=message,
        type=type,
        category=category,
        link=link,
        icon=icon
    )

@login_required
def email_settings(request):
    return render(request, 'notifications/email_settings.html')

@login_required
def test_email(request):
    from django.contrib import messages
    from django.core.mail import send_mail
    from django.conf import settings
    
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            send_mail(
                'MultiStock Test Email',
                'This is a test email from MultiStock Platform. Email notifications are working!',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False
            )
            messages.success(request, f'Test email sent to {email}. Check console or inbox.')
        except Exception as e:
            messages.error(request, f'Failed to send email: {str(e)}')
    
    return redirect('email_settings')
