from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import AuditLog

from permissions.decorators import require_permission

@require_permission('audit', 'view')
def audit_logs(request):
    from django.contrib.auth.models import User
    from django.db.models import Q
    
    logs = AuditLog.objects.select_related('user').all()
    
    action_type = request.GET.get('action_type')
    user_id = request.GET.get('user')
    model_name = request.GET.get('model')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    
    if action_type:
        logs = logs.filter(action_type=action_type)
    if user_id:
        logs = logs.filter(user_id=user_id)
    if model_name:
        logs = logs.filter(model_name__icontains=model_name)
    if date_from:
        logs = logs.filter(timestamp__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__lte=date_to)
    if search:
        logs = logs.filter(Q(description__icontains=search) | Q(model_name__icontains=search))
    
    users = User.objects.filter(is_staff=True).order_by('username')
    models = AuditLog.objects.values_list('model_name', flat=True).distinct().order_by('model_name')
    
    logs = logs[:200]
    return render(request, 'audit/logs.html', {
        'logs': logs,
        'users': users,
        'models': models,
        'selected_action': action_type,
        'selected_user': user_id,
        'selected_model': model_name,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
    })
