"""
UNIFIED TEAM DASHBOARD VIEWS
Serves both SuperAdmin and Admin roles with permission-based restrictions

Key Differences:
- SuperAdmin: Full access to everything, can manage all users, change roles, access system settings
- Admin: Limited access, can only manage their own users (staff/supervisors), cannot change superadmin
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_http_methods
from permissions.decorators import require_role, get_user_role
import json

# ============================================================================
# UNIFIED DASHBOARD VIEW - SERVES BOTH SUPERADMIN & ADMIN
# ============================================================================

@login_required
@require_role('superadmin', 'admin')
def unified_dashboard(request):
    """
    Unified dashboard for both SuperAdmin and Admin
    Shows different data based on user role
    
    SuperAdmin: View everything, all metrics
    Admin: View only their business data, limited metrics
    """
    from goods.models import ListModel as Product
    from stock.models import StockListModel
    from orders.models import Order
    from customer.models import ListModel as Customer
    
    user_role = get_user_role(request.user)
    
    # Time periods
    today = timezone.now().date()
    month_start = timezone.now().replace(day=1)
    week_ago = timezone.now() - timedelta(days=7)
    
    # === USER METRICS ===
    if user_role == 'superadmin':
        # SuperAdmin sees ALL users
        total_users = User.objects.count()
        total_customers = Customer.objects.count()
        new_users_week = User.objects.filter(date_joined__gte=week_ago).count()
        active_users = User.objects.filter(last_login__gte=week_ago).count()
    else:
        # Admin sees only their team users
        total_users = User.objects.filter(is_staff=True).count()
        total_customers = Customer.objects.count()
        new_users_week = User.objects.filter(is_staff=True, date_joined__gte=week_ago).count()
        active_users = User.objects.filter(is_staff=True, last_login__gte=week_ago).count()
    
    # === ORDER METRICS ===
    orders = Order.objects.all()
    total_orders = orders.count()
    orders_today = orders.filter(created_at__date=today).count()
    orders_month = orders.filter(created_at__gte=month_start).count()
    pending_orders = orders.filter(status__in=['pending', 'confirmed']).count()
    
    # === REVENUE METRICS ===
    total_revenue = orders.filter(status='completed').aggregate(
        total=Sum('grand_total'))['total'] or 0
    revenue_month = orders.filter(
        status='completed', 
        created_at__gte=month_start
    ).aggregate(total=Sum('grand_total'))['total'] or 0
    
    # === INVENTORY METRICS ===
    stocks = StockListModel.objects.all()
    total_products = Product.objects.filter(is_delete=False).count()
    low_stock_items = stocks.filter(goods_qty__lt=10).count()
    out_of_stock = stocks.filter(goods_qty=0).count()
    total_stock_value = stocks.aggregate(
        value=Sum('goods_qty'))['value'] or 0
    
    context = {
        'user_role': user_role,
        'is_superadmin': user_role == 'superadmin',
        'is_admin': user_role == 'admin',
        
        # User metrics
        'total_users': total_users,
        'total_customers': total_customers,
        'new_users_week': new_users_week,
        'active_users': active_users,
        
        # Order metrics
        'total_orders': total_orders,
        'orders_today': orders_today,
        'orders_month': orders_month,
        'pending_orders': pending_orders,
        
        # Revenue metrics
        'total_revenue': total_revenue,
        'revenue_month': revenue_month,
        
        # Inventory metrics
        'total_products': total_products,
        'low_stock_items': low_stock_items,
        'out_of_stock': out_of_stock,
        'total_stock_value': total_stock_value,
    }
    
    return render(request, 'dashboard/team/dashboard.html', context)


# ============================================================================
# UNIFIED USER MANAGEMENT
# ============================================================================

@login_required
@require_role('superadmin', 'admin')
def team_user_list(request):
    """
    Unified user management page
    
    SuperAdmin: Can see and manage ALL users, change roles, delete users
    Admin: Can see only team users (staff/supervisors), cannot see/modify superadmin/admin
    """
    user_role = get_user_role(request.user)
    
    if user_role == 'superadmin':
        # SuperAdmin sees ALL users
        users = User.objects.all().order_by('-date_joined')
        can_delete = True
        can_change_role = True
        can_change_status = True
    else:
        # Admin sees only non-admin users
        users = User.objects.filter(is_staff=True).exclude(is_superuser=True).order_by('-date_joined')
        can_delete = False  # Admin cannot delete
        can_change_role = True  # Can change to staff/supervisor/customer only
        can_change_status = True  # Can toggle active status
    
    # Search
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Role filter
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role__role=role_filter)
    
    # Status filter
    status = request.GET.get('status')
    if status == 'active':
        users = users.filter(is_active=True)
    elif status == 'inactive':
        users = users.filter(is_active=False)
    
    context = {
        'users': users,
        'total_users': users.count(),
        'user_role': user_role,
        'is_superadmin': user_role == 'superadmin',
        'can_delete': can_delete,
        'can_change_role': can_change_role,
        'can_change_status': can_change_status,
    }
    
    return render(request, 'dashboard/team/users/list.html', context)


@login_required
@require_role('superadmin', 'admin')
def team_user_detail(request, user_id):
    """
    User detail page
    
    SuperAdmin: Can view and edit any user
    Admin: Can only view/edit non-admin users
    """
    user_role = get_user_role(request.user)
    user = get_object_or_404(User, id=user_id)
    
    # Permission check
    if user_role == 'admin':
        # Admin cannot view superadmins or other admins
        if user.is_superuser:
            return redirect('dashboard:team_users')
    
    # Get user's activity
    try:
        from orders.models import Order
        user_orders = Order.objects.filter(customer_user=user).order_by('-created_at')[:10]
    except:
        user_orders = []
    
    try:
        from permissions.models import UserRole
        user_role_obj = UserRole.objects.get(user=user)
    except:
        user_role_obj = None
    
    context = {
        'user_obj': user,
        'user_orders': user_orders,
        'user_role': user_role,
        'user_role_obj': user_role_obj,
        'is_superadmin': user_role == 'superadmin',
    }
    
    return render(request, 'dashboard/team/users/detail.html', context)


@login_required
@require_role('superadmin', 'admin')
@require_http_methods(["POST"])
def team_user_toggle_status(request, user_id):
    """
    Toggle user active/inactive status
    
    SuperAdmin: Can toggle any user
    Admin: Can toggle only non-admin users
    """
    user_role = get_user_role(request.user)
    user = get_object_or_404(User, id=user_id)
    
    # Permission checks
    if user.id == request.user.id:
        return JsonResponse({
            'success': False,
            'message': 'Cannot modify your own account'
        }, status=403)
    
    if user_role == 'admin' and user.is_superuser:
        return JsonResponse({
            'success': False,
            'message': 'Admin cannot modify SuperAdmin accounts'
        }, status=403)
    
    if user_role == 'admin' and (user.is_superuser or user.groups.filter(name='admin').exists()):
        return JsonResponse({
            'success': False,
            'message': 'Admin cannot modify admin accounts'
        }, status=403)
    
    user.is_active = not user.is_active
    user.save()
    
    return JsonResponse({
        'success': True,
        'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
        'is_active': user.is_active
    })


@login_required
@require_role('superadmin', 'admin')
@require_http_methods(["POST"])
def team_user_change_role(request, user_id):
    """
    Change user role
    
    SuperAdmin: Can change to any role
    Admin: Can only change to staff/supervisor/customer (not admin/superadmin)
    """
    user_role = get_user_role(request.user)
    user = get_object_or_404(User, id=user_id)
    
    # Permission checks
    if user.id == request.user.id:
        return JsonResponse({
            'success': False,
            'message': 'Cannot modify your own role'
        }, status=403)
    
    data = json.loads(request.body)
    new_role = data.get('role')
    
    # Admin cannot create/change to admin or superadmin roles
    if user_role == 'admin':
        restricted_roles = ['superadmin', 'admin']
        if new_role in restricted_roles:
            return JsonResponse({
                'success': False,
                'message': f'Admin cannot assign {new_role} role'
            }, status=403)
    
    try:
        from permissions.models import UserRole
        role_obj, created = UserRole.objects.get_or_create(user=user)
        role_obj.role = new_role
        role_obj.save()
        
        return JsonResponse({
            'success': True,
            'message': f'User role changed to {new_role}'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


# ============================================================================
# UNIFIED ORDER MANAGEMENT
# ============================================================================

@login_required
@require_role('superadmin', 'admin')
def team_orders(request):
    """
    Unified order management page
    
    SuperAdmin: Can see and manage ALL orders
    Admin: Can see ALL orders but limited edit permissions
    """
    from orders.models import Order
    
    user_role = get_user_role(request.user)
    orders = Order.objects.all().order_by('-created_at')
    
    # Date filter
    date_filter = request.GET.get('date')
    if date_filter == 'today':
        orders = orders.filter(created_at__date=timezone.now().date())
    elif date_filter == 'week':
        week_ago = timezone.now() - timedelta(days=7)
        orders = orders.filter(created_at__gte=week_ago)
    elif date_filter == 'month':
        month_start = timezone.now().replace(day=1)
        orders = orders.filter(created_at__gte=month_start)
    
    # Status filter
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # Search
    search = request.GET.get('search')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(customer_user__username__icontains=search)
        )
    
    context = {
        'orders': orders[:100],
        'total_orders': orders.count(),
        'user_role': user_role,
        'is_superadmin': user_role == 'superadmin',
        'can_approve': user_role == 'superadmin',  # Only SuperAdmin can approve
        'can_delete': user_role == 'superadmin',   # Only SuperAdmin can delete
    }
    
    return render(request, 'dashboard/team/orders/list.html', context)


# ============================================================================
# UNIFIED INVENTORY MANAGEMENT
# ============================================================================

@login_required
@require_role('superadmin', 'admin')
def team_inventory(request):
    """
    Unified inventory management
    
    SuperAdmin: Full inventory control, can adjust, transfer, audit
    Admin: Can view inventory, limited adjustments
    """
    from inventory.models import Inventory
    
    user_role = get_user_role(request.user)
    inventory = Inventory.objects.all()
    
    # Search
    search = request.GET.get('search')
    if search:
        inventory = inventory.filter(
            Q(goods__goods_name__icontains=search) |
            Q(goods__sku__icontains=search)
        )
    
    context = {
        'inventory': inventory[:100],
        'user_role': user_role,
        'is_superadmin': user_role == 'superadmin',
        'can_transfer': user_role == 'superadmin',
        'can_audit': user_role == 'superadmin',
    }
    
    return render(request, 'dashboard/team/inventory/list.html', context)


# ============================================================================
# UNIFIED ANALYTICS & REPORTS
# ============================================================================

@login_required
@require_role('superadmin', 'admin')
def team_analytics(request):
    """
    Unified analytics dashboard
    
    SuperAdmin: See all analytics
    Admin: See business analytics only
    """
    from goods.models import ListModel as Product
    from orders.models import Order
    from customer.models import ListModel as Customer
    
    user_role = get_user_role(request.user)
    
    # Time periods
    today = timezone.now().date()
    week_ago = timezone.now() - timedelta(days=7)
    month_start = timezone.now().replace(day=1)
    
    # Metrics
    try:
        total_revenue = 0
        weekly_revenue = 0
        monthly_revenue = 0
        
        orders = Order.objects.all()
        total_revenue = orders.filter(status='completed').aggregate(
            total=Sum('grand_total'))['total'] or 0
        weekly_revenue = orders.filter(
            status='completed', 
            created_at__gte=week_ago
        ).aggregate(total=Sum('grand_total'))['total'] or 0
        monthly_revenue = orders.filter(
            status='completed', 
            created_at__gte=month_start
        ).aggregate(total=Sum('grand_total'))['total'] or 0
    except:
        total_revenue = weekly_revenue = monthly_revenue = 0
    
    # Orders
    total_orders = Order.objects.count()
    weekly_orders = Order.objects.filter(created_at__gte=week_ago).count()
    monthly_orders = Order.objects.filter(created_at__gte=month_start).count()
    
    # Products
    total_products = Product.objects.filter(is_delete=False).count()
    
    # Customers
    total_customers = Customer.objects.count()
    
    context = {
        'user_role': user_role,
        'is_superadmin': user_role == 'superadmin',
        'total_revenue': total_revenue,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'total_orders': total_orders,
        'weekly_orders': weekly_orders,
        'monthly_orders': monthly_orders,
        'total_products': total_products,
        'total_customers': total_customers,
    }
    
    return render(request, 'dashboard/team/analytics/index.html', context)


# ============================================================================
# SUPERADMIN ONLY - SYSTEM SETTINGS
# ============================================================================

@login_required
@require_role('superadmin')
def team_system_settings(request):
    """System settings - SuperAdmin ONLY"""
    from django.conf import settings
    
    if get_user_role(request.user) != 'superadmin':
        return JsonResponse({
            'error': 'Access denied'
        }, status=403)
    
    context = {
        'debug_mode': settings.DEBUG,
        'database_engine': settings.DATABASES['default']['ENGINE'],
        'installed_apps_count': len(settings.INSTALLED_APPS),
        'middleware_count': len(settings.MIDDLEWARE),
        'time_zone': settings.TIME_ZONE,
        'language_code': settings.LANGUAGE_CODE,
    }
    
    return render(request, 'dashboard/team/settings/index.html', context)


@login_required
@require_role('superadmin')
def team_system_logs(request):
    """System logs - SuperAdmin ONLY"""
    if get_user_role(request.user) != 'superadmin':
        return JsonResponse({
            'error': 'Access denied'
        }, status=403)
    
    try:
        from audit.models import AuditLog
        logs = AuditLog.objects.all().order_by('-created_at')[:100]
    except:
        logs = []
    
    context = {
        'logs': logs,
    }
    
    return render(request, 'dashboard/team/logs/index.html', context)


@login_required
@require_role('superadmin')
def team_database_overview(request):
    """Database overview - SuperAdmin ONLY"""
    if get_user_role(request.user) != 'superadmin':
        return JsonResponse({
            'error': 'Access denied'
        }, status=403)
    
    from django.apps import apps
    
    models_info = []
    total_records = 0
    
    for model in apps.get_models():
        try:
            count = model.objects.count()
            total_records += count
            models_info.append({
                'name': model.__name__,
                'app': model._meta.app_label,
                'count': count,
            })
        except:
            pass
    
    models_info.sort(key=lambda x: x['count'], reverse=True)
    
    context = {
        'models_info': models_info[:50],
        'total_models': len(models_info),
        'total_records': total_records,
    }
    
    return render(request, 'dashboard/team/database/overview.html', context)
