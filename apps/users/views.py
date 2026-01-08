from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from .models import UserProfile, UserActivity, Team
from django.core.paginator import Paginator

# Import RBAC decorators
from permissions.decorators import require_permission, require_role

@require_permission('users', 'view')  # View users permission required
def user_list(request):
    search = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    users = User.objects.select_related('profile').all()
    
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search))
    if role_filter:
        users = users.filter(profile__role=role_filter)
    if status_filter:
        users = users.filter(profile__is_active=(status_filter == 'active'))
    
    paginator = Paginator(users, 20)
    page = request.GET.get('page', 1)
    users_page = paginator.get_page(page)
    
    return render(request, 'users/list.html', {'users': users_page, 'search': search, 'role_filter': role_filter, 'status_filter': status_filter})

@require_permission('users', 'create')  # Create users permission required
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        phone = request.POST.get('phone', '')
        department = request.POST.get('department', '')
        
        # Restrict Admin from creating Admin or SuperAdmin roles
        from permissions.decorators import get_user_role
        current_user_role = get_user_role(request.user)
        
        # Supervisor CANNOT create any users
        if current_user_role == 'subadmin':
            messages.error(request, 'Access denied. SubAdmin users cannot create user accounts.')
            return redirect('user_list')
        
        if current_user_role == 'admin':
            # Admin can only create: admin, subadmin, staff, customer
            if role in ['admin', 'superadmin']:
                messages.error(request, 'Access denied. You cannot create Admin or SuperAdmin accounts.')
                return redirect('user_list')
        
        elif current_user_role == 'admin':
            # Admin can ONLY create: subadmin, staff, customer (NOT admin or superadmin)
            if role in ['admin', 'superadmin', 'admin']:
                messages.error(request, 'Access denied. You can only create SubAdmin and Staff accounts.')
                return redirect('user_list')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Create UserRole instead of UserProfile for RBAC
        from permissions.models import UserRole
        UserRole.objects.create(user=user, role=role)
        
        # Also create UserProfile for backward compatibility
        UserProfile.objects.create(user=user, role=role, phone=phone, department=department)
        
        messages.success(request, f'User {username} created successfully')
        return redirect('user_list')
    
    # Filter available roles based on current user
    from permissions.decorators import get_user_role
    current_user_role = get_user_role(request.user)
    
    available_roles = [
        ('subadmin', 'SubAdmin (Senior Staff)'),
        ('staff', 'Staff (Employee)'),
        ('customer', 'Customer'),
    ]
    
    if current_user_role == 'admin':
        # Admin can create Admin, SubAdmin, Staff, Customer
        available_roles = [
            
            ('subadmin', 'SubAdmin (Senior Staff)'),
            ('staff', 'Staff (Employee)'),
            ('customer', 'Customer'),
        ]
    elif current_user_role == 'superadmin' or request.user.is_superuser:
        # SuperAdmin can create any role including Admin
        available_roles = [
            ('superadmin', 'SuperAdmin'),
            ('admin', 'Admin (Partner)'),
            
            ('subadmin', 'SubAdmin (Senior Staff)'),
            ('staff', 'Staff (Employee)'),
            ('customer', 'Customer'),
        ]
    
    return render(request, 'users/create.html', {'available_roles': available_roles})

@require_permission('users', 'view')  # View user details
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    activities = UserActivity.objects.filter(user=user)[:20]
    return render(request, 'users/detail.html', {'user_obj': user, 'activities': activities})

@require_permission('users', 'edit')  # Edit users permission required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.save()
        
        profile = user.profile
        profile.role = request.POST.get('role')
        profile.phone = request.POST.get('phone', '')
        profile.department = request.POST.get('department', '')
        profile.is_active = request.POST.get('is_active') == 'on'
        profile.save()
        
        messages.success(request, 'User updated successfully')
        return redirect('user_detail', user_id=user_id)
    
    return render(request, 'users/edit.html', {'user_obj': user})

@require_permission('users', 'delete')  # Delete users permission (SuperAdmin/Admin only)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully')
        return redirect('user_list')
    return render(request, 'users/delete.html', {'user_obj': user})

@require_permission('users', 'view')  # View user activity
def user_activity(request, user_id):
    user = get_object_or_404(User, id=user_id)
    activities = UserActivity.objects.filter(user=user)
    
    module_filter = request.GET.get('module', '')
    if module_filter:
        activities = activities.filter(module=module_filter)
    
    paginator = Paginator(activities, 50)
    page = request.GET.get('page', 1)
    activities_page = paginator.get_page(page)
    
    return render(request, 'users/activity.html', {'user_obj': user, 'activities': activities_page})

@require_permission('team', 'view')  # View teams
def team_list(request):
    teams = Team.objects.annotate(member_count=Count('members')).all()
    return render(request, 'users/teams.html', {'teams': teams})

@require_permission('team', 'create')  # Create teams
def create_team(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        leader_id = request.POST.get('leader')
        
        team = Team.objects.create(name=name, description=description, leader_id=leader_id)
        messages.success(request, f'Team {name} created successfully')
        return redirect('team_list')
    
    users = User.objects.filter(profile__is_active=True)
    return render(request, 'users/create_team.html', {'users': users})

@require_permission('users', 'view')  # User stats API
def user_stats_api(request):
    total = User.objects.count()
    active = UserProfile.objects.filter(is_active=True).count()
    by_role = UserProfile.objects.values('role').annotate(count=Count('id'))
    
    return JsonResponse({
        'total': total,
        'active': active,
        'inactive': total - active,
        'by_role': list(by_role)
    })