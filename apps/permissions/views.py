from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from .models import UserRole, PERMISSION_MATRIX
from django.core.paginator import Paginator

from permissions.decorators import require_permission

@require_permission('permissions', 'view')
def permission_list(request):
    # Redirect to matrix view as default
    return redirect('permissions:matrix')

@require_permission('permissions', 'manage')
def create_permission(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        user = User.objects.get(id=user_id)
        UserRole.objects.update_or_create(user=user, defaults={'role': role})
        messages.success(request, f'Role assigned to {user.username}')
        return redirect('permissions:list')
    
    users = User.objects.all()
    roles = UserRole.ROLE_CHOICES
    return render(request, 'permissions/create.html', {'users': users, 'roles': roles})

@require_permission('permissions', 'view')
def role_permissions(request, role):
    permissions = PERMISSION_MATRIX.get(role, {})
    return render(request, 'permissions/role_permissions.html', {'role': role, 'permissions': permissions})

@require_permission('permissions', 'view')
def user_permissions(request, user_id):
    user = get_object_or_404(User, id=user_id)
    try:
        user_role = user.role
        permissions = PERMISSION_MATRIX.get(user_role.role, {})
    except:
        user_role = None
        permissions = {}
    
    return render(request, 'permissions/user_permissions.html', {'user_obj': user, 'user_role': user_role, 'permissions': permissions})

@require_permission('permissions', 'manage')
def grant_permission(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        role = request.POST.get('role')
        UserRole.objects.update_or_create(user=user, defaults={'role': role})
        messages.success(request, f'Role {role} granted to {user.username}')
        return redirect('permissions:user_permissions', user_id=user_id)
    
    roles = UserRole.ROLE_CHOICES
    return render(request, 'permissions/grant.html', {'user_obj': user, 'roles': roles})

@require_permission('permissions', 'manage')
def revoke_permission(request, override_id):
    user = get_object_or_404(User, id=override_id)
    try:
        user.role.delete()
        messages.success(request, 'Role revoked')
    except:
        messages.error(request, 'No role to revoke')
    return redirect('permissions:list')

@require_permission('audit', 'view')
def access_logs(request):
    from audit.models import AuditLog
    logs = AuditLog.objects.select_related('user').all()[:100]
    return render(request, 'permissions/access_logs.html', {'logs': logs})

@login_required
def permission_matrix(request):
    # Team roles can view permissions page
    from permissions.decorators import get_user_role
    user_role = get_user_role(request.user)
    
    if user_role not in ['superadmin', 'admin', 'supervisor']:
        messages.error(request, 'Access denied. Team roles only.')
        return redirect('dashboard')
    
    roles = ['superadmin', 'admin', 'supervisor', 'staff']
    modules = list(PERMISSION_MATRIX.get('superadmin', {}).keys())
    
    # Only SuperAdmin can manage roles
    can_manage_roles = user_role == 'superadmin'
    
    return render(request, 'permissions/matrix.html', {
        'roles': roles, 
        'modules': modules, 
        'matrix': PERMISSION_MATRIX,
        'can_manage_roles': can_manage_roles
    })

@require_permission('permissions', 'view')
def check_permission_api(request):
    user_id = request.GET.get('user_id')
    module = request.GET.get('module')
    action = request.GET.get('action')
    
    user = User.objects.get(id=user_id)
    try:
        user_role = user.role
        has_permission = user_role.has_permission(module, action)
    except:
        has_permission = False
    
    return JsonResponse({'has_permission': has_permission})

@login_required
def get_users_api(request):
    from permissions.decorators import get_user_role
    
    current_user_role = get_user_role(request.user)
    
    # Only team roles can access this API
    if current_user_role not in ['superadmin', 'admin', 'supervisor']:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    users = User.objects.filter(is_staff=True).select_related('role')
    user_list = []
    
    # Role hierarchy - what roles can each role see/modify
    restricted_roles = {
        'superadmin': [],  # Can see all
        'admin': ['superadmin', 'admin'],  # Cannot see/modify superadmin or admin
        'admin': ['superadmin', 'admin'],
        'supervisor': ['superadmin', 'admin', 'supervisor'],
    }
    
    for u in users:
        user_role = u.role.role if hasattr(u, 'role') else None
        
        # Filter users based on role hierarchy
        if user_role not in restricted_roles.get(current_user_role, []):
            user_list.append({
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'role': user_role,
                'is_superuser': u.is_superuser
            })
    
    return JsonResponse({'users': user_list})

@login_required
def get_permission_api(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    role = request.GET.get('role')
    module = request.GET.get('module')
    
    if not role or not module:
        return JsonResponse({'error': 'Role and module required'}, status=400)
    
    permissions = PERMISSION_MATRIX.get(role, {}).get(module, {})
    return JsonResponse({'success': True, 'permissions': permissions})

@login_required
def update_permission_api(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    import json
    data = json.loads(request.body)
    role = data.get('role')
    module = data.get('module')
    permissions = data.get('permissions', {})
    
    if not role or not module:
        return JsonResponse({'error': 'Role and module required'}, status=400)
    
    # Update permission matrix in memory
    if role not in PERMISSION_MATRIX:
        PERMISSION_MATRIX[role] = {}
    
    if module not in PERMISSION_MATRIX[role]:
        PERMISSION_MATRIX[role][module] = {}
    
    # Update permissions
    PERMISSION_MATRIX[role][module].update(permissions)
    
    # Save to file
    try:
        import os
        from django.conf import settings
        
        file_path = os.path.join(settings.BASE_DIR, 'apps', 'permissions', 'models.py')
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find and replace the PERMISSION_MATRIX
        import re
        pattern = r'PERMISSION_MATRIX = \{[\s\S]*?\n\}'
        
        # Convert matrix to string
        matrix_str = 'PERMISSION_MATRIX = ' + repr(PERMISSION_MATRIX)
        
        new_content = re.sub(pattern, matrix_str, content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return JsonResponse({'success': True, 'message': 'Permission updated'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def change_role_api(request):
    from permissions.decorators import get_user_role
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    import json
    data = json.loads(request.body)
    user_id = data.get('user_id')
    new_role = data.get('role')
    
    try:
        current_user_role = get_user_role(request.user)
        target_user = User.objects.get(id=user_id)
        target_current_role = get_user_role(target_user)
        
        # Role hierarchy restrictions
        restricted_roles = {
            'superadmin': [],  # Can change any role
            'admin': ['superadmin', 'admin'],  # Cannot change superadmin or admin
            'admin': ['superadmin', 'admin'],  # Cannot change superadmin, admin, or admin
            'supervisor': ['superadmin', 'admin', 'supervisor'],  # Cannot change superadmin, admin, admin, or supervisor
        }
        
        # Check if current user has permission to change roles
        if current_user_role not in restricted_roles:
            return JsonResponse({'error': 'You do not have permission to change roles'}, status=403)
        
        # Check if target role is restricted
        if target_current_role in restricted_roles.get(current_user_role, []):
            return JsonResponse({'error': f'You cannot modify {target_current_role} roles'}, status=403)
        
        # Check if new role is restricted
        if new_role in restricted_roles.get(current_user_role, []):
            return JsonResponse({'error': f'You cannot assign {new_role} role'}, status=403)
        
        # Update or create role
        UserRole.objects.update_or_create(
            user=target_user,
            defaults={'role': new_role}
        )
        
        # Update is_superuser and is_staff flags
        if new_role == 'superadmin':
            target_user.is_superuser = True
            target_user.is_staff = True
        elif new_role in ['admin', 'admin', 'supervisor', 'staff']:
            target_user.is_superuser = False
            target_user.is_staff = True
        else:
            target_user.is_superuser = False
            target_user.is_staff = False
        target_user.save()
        
        return JsonResponse({'success': True, 'message': 'Role updated successfully'})
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
