from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from functools import wraps

def get_user_role(user):
    """Get user role from UserRole model or fallback to user attributes"""
    if not user or not user.is_authenticated:
        return 'guest'
    
    if user.is_superuser:
        return 'superadmin'
    
    # Check UserRole model
    try:
        from permissions.models import UserRole
        user_role = UserRole.objects.filter(user=user).first()
        if user_role:
            return user_role.role
    except:
        pass
    
    # Fallback to Django groups
    try:
        if user.groups.filter(name='admin').exists():
            return 'admin'
        elif user.groups.filter(name__in=['admin', 'sub-admin']).exists():
            return 'admin'
        elif user.groups.filter(name='subadmin').exists():
            return 'subadmin'
        elif user.is_staff:
            return 'staff'
    except:
        pass
    
    return 'customer'

def check_permission(user, module, action='view'):
    """Check if user has permission for module action using PERMISSION_MATRIX"""
    from permissions.models import PERMISSION_MATRIX
    role = get_user_role(user)
    permissions = PERMISSION_MATRIX.get(role, {})
    module_perms = permissions.get(module, {})
    return module_perms.get(action, False)

def require_permission(module, action='view'):
    """
    Decorator to check if user has permission for a specific module action.
    
    Usage:
        @require_permission('products', 'create')
        def create_product(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                return redirect('auth:login_selection')
            
            if not check_permission(request.user, module, action):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': f'Permission denied: {action} access to {module} required'
                    }, status=403)
                messages.error(request, f'Permission denied: {action} access to {module} required')
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_role(*allowed_roles):
    """
    Decorator to check if user has one of the specified roles.
    
    Usage:
        @require_role('superadmin', 'admin')
        def admin_only_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': 'Authentication required'}, status=401)
                return redirect('auth:login_selection')
            
            user_role = get_user_role(request.user)
            if user_role not in allowed_roles:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': f'Role required: {", ".join(allowed_roles)}'
                    }, status=403)
                messages.error(request, f'Access denied. Required role: {", ".join(allowed_roles)}')
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def customer_restricted(view_func):
    """
    Decorator to block customers from accessing a view.
    Use this for admin-only pages like product management, inventory, etc.
    
    Usage:
        @customer_restricted
        def create_product(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('auth:login_selection')
        
        user_role = get_user_role(request.user)
        if user_role == 'customer':
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'error': 'Customers cannot access this page'
                }, status=403)
            return HttpResponseForbidden(
                '<h1>Access Denied</h1>'
                '<p>Customers do not have permission to access this page.</p>'
                '<p><a href="/dashboard/">Return to Dashboard</a></p>'
            )
        
        return view_func(request, *args, **kwargs)
    return wrapper

def own_data_only(model_field='user'):
    """
    Decorator to ensure customers can only access their own data.
    Adds a filter to the request object that views can use.
    
    Usage:
        @own_data_only('customer_user')
        def my_orders(request):
            orders = Order.objects.filter(**request.customer_filter)
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('auth:login_selection')
            
            user_role = get_user_role(request.user)
            if user_role == 'customer':
                # Add filter for customer's own data
                request.customer_filter = {model_field: request.user}
                request.is_customer = True
            else:
                # Admin/staff can see all data
                request.customer_filter = {}
                request.is_customer = False
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
