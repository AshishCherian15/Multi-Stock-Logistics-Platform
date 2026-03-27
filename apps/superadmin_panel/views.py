from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_http_methods
import json

def is_superadmin(user):
    """Check if user is superadmin"""
    return user.is_superuser

@login_required
@user_passes_test(is_superadmin)
def superadmin_panel_home(request):
    """Superadmin panel home - redirect to main dashboard"""
    return redirect('/dashboard/')  # Redirect to existing superadmin dashboard

@login_required
@user_passes_test(is_superadmin)
def system_users(request):
    """Manage all system users"""
    users = User.objects.all().order_by('-date_joined')
    
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
    elif status == 'superuser':
        users = users.filter(is_superuser=True)
    
    context = {
        'users': users,
        'total_users': users.count(),
    }
    
    return render(request, 'superadmin/users/list.html', context)


@login_required
@user_passes_test(is_superadmin)
def user_detail_super(request, user_id):
    """View user details"""
    user = get_object_or_404(User, id=user_id)
    
    # Get user's activity
    try:
        from orders.models import Order
        user_orders = Order.objects.filter(customer_user=user).order_by('-created_at')[:10]
    except:
        user_orders = []
    
    context = {
        'user_obj': user,
        'user_orders': user_orders,
    }
    
    return render(request, 'superadmin/users/detail.html', context)


@login_required
@user_passes_test(is_superadmin)
@require_http_methods(["POST"])
def toggle_user_status(request, user_id):
    """Toggle user active status"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent disabling own account
    if user.id == request.user.id:
        return JsonResponse({
            'success': False,
            'message': 'Cannot modify your own account'
        }, status=403)
    
    user.is_active = not user.is_active
    user.save()
    
    return JsonResponse({
        'success': True,
        'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
        'is_active': user.is_active
    })


@login_required
@user_passes_test(is_superadmin)
@require_http_methods(["POST"])
def change_user_role(request, user_id):
    """Change user role"""
    user = get_object_or_404(User, id=user_id)
    
    # Prevent changing own role
    if user.id == request.user.id:
        return JsonResponse({
            'success': False,
            'message': 'Cannot modify your own role'
        }, status=403)
    
    data = json.loads(request.body)
    new_role = data.get('role')
    
    # Update role
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


@login_required
@user_passes_test(is_superadmin)
def system_settings(request):
    """System settings and configuration"""
    from django.conf import settings
    
    context = {
        'debug_mode': settings.DEBUG,
        'database_engine': settings.DATABASES['default']['ENGINE'],
        'installed_apps_count': len(settings.INSTALLED_APPS),
        'middleware_count': len(settings.MIDDLEWARE),
        'time_zone': settings.TIME_ZONE,
        'language_code': settings.LANGUAGE_CODE,
    }
    
    return render(request, 'superadmin/settings/index.html', context)


@login_required
@user_passes_test(is_superadmin)
def system_logs(request):
    """View system logs"""
    # Placeholder for system logs
    logs = []
    
    context = {
        'logs': logs,
    }
    
    return render(request, 'superadmin/logs/index.html', context)


@login_required
@user_passes_test(is_superadmin)
def database_overview(request):
    """Database overview and statistics"""
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
    
    # Sort by count
    models_info.sort(key=lambda x: x['count'], reverse=True)
    
    context = {
        'models_info': models_info[:50],  # Top 50
        'total_models': len(models_info),
        'total_records': total_records,
    }
    
    return render(request, 'superadmin/database/overview.html', context)


@login_required
@user_passes_test(is_superadmin)
def all_orders_super(request):
    """View all orders with advanced filters"""
    from orders.models import Order
    
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
        'orders': orders[:100],  # Limit to 100
        'total_orders': orders.count(),
    }
    
    return render(request, 'superadmin/orders/list.html', context)


@login_required
@user_passes_test(is_superadmin)
def analytics_dashboard(request):
    """Advanced analytics dashboard"""
    from goods.models import ListModel as Product
    from orders.models import Order
    from customer.models import ListModel as Customer
    
    # Time periods
    today = timezone.now().date()
    week_ago = timezone.now() - timedelta(days=7)
    month_start = timezone.now().replace(day=1)
    
    # Metrics
    total_revenue = 0
    weekly_revenue = 0
    monthly_revenue = 0
    
    # Orders
    total_orders = Order.objects.count()
    weekly_orders = Order.objects.filter(created_at__gte=week_ago).count()
    monthly_orders = Order.objects.filter(created_at__gte=month_start).count()
    
    # Products
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_delete=False).count()
    
    # Customers
    total_customers = Customer.objects.count()
    new_customers_week = Customer.objects.filter(create_time__gte=week_ago).count()
    
    context = {
        'total_revenue': total_revenue,
        'weekly_revenue': weekly_revenue,
        'monthly_revenue': monthly_revenue,
        'total_orders': total_orders,
        'weekly_orders': weekly_orders,
        'monthly_orders': monthly_orders,
        'total_products': total_products,
        'active_products': active_products,
        'total_customers': total_customers,
        'new_customers_week': new_customers_week,
    }
    
    return render(request, 'superadmin/analytics/index.html', context)
