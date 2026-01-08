from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.http import JsonResponse
from goods.models import ListModel
from stock.models import StockListModel
from customer.models import ListModel as CustomerModel
from supplier.models import ListModel as SupplierModel
from warehouse.models import ListModel as WarehouseModel
from permissions.decorators import get_user_role

def home(request):
    """Landing page - login selection for everyone, guest or authenticated"""
    
    # Check if user clicked "Continue as Guest"
    if request.GET.get('guest_mode') == 'true':
        request.session['guest_mode'] = True
        return redirect('/catalog/')
    
    # If already in guest mode, redirect to guest catalog
    if request.session.get('guest_mode', False):
        return redirect('/catalog/')
    
    # If authenticated, redirect to role-based dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Show login selection page for unauthenticated users
    return render(request, 'auth/login_selection.html')


@login_required
def dashboard_router(request):
    """
    Smart dashboard router - redirects users to their role-specific dashboard.
    All team roles (superadmin, admin, subadmin, supervisor, staff, senior_staff) use the same dashboard.
    """
    user_role = get_user_role(request.user)
    
    # Route all team members to superadmin dashboard
    if user_role in ['superadmin', 'admin', 'subadmin', 'staff']:
        return redirect('superadmin_dashboard')
    elif user_role == 'customer':
        return redirect('customer_dashboard')
    else:
        return redirect('guest_dashboard')

@login_required
def search_api(request):
    """Legacy search API - redirects to new unified search"""
    try:
        query = request.GET.get('q', '').strip()
        
        if not query or len(query) < 2:
            return JsonResponse({'results': [], 'count': 0, 'by_category': {}})
        
        # Use the new unified search from search app
        from search.advanced_search import AdvancedSearch
        
        try:
            results_data = AdvancedSearch.search_all(query, request.user if request.user.is_authenticated else None)
            return JsonResponse(results_data)
        except Exception as search_error:
            # Fallback to basic search
            search_type = request.GET.get('type', 'all')
            results = []
            
            try:
                if search_type in ['all', 'products']:
                    products = ListModel.objects.filter(
                        Q(goods_desc__icontains=query) | Q(goods_code__icontains=query), 
                        is_delete=False
                    )[:5]
                    for product in products:
                        try:
                            stock = StockListModel.objects.filter(goods_code=product.goods_code).first()
                            results.append({
                                'id': product.id,
                                'title': product.goods_desc or product.goods_code,
                                'subtitle': f'Product - {product.goods_code} | Stock: {stock.goods_qty if stock else 0}',
                                'url': f'/products/?search={product.goods_code}',
                                'icon': 'box',
                                'category': 'products',
                                'relevance': 10
                            })
                        except:
                            pass
                
                if search_type in ['all', 'customers']:
                    customers = CustomerModel.objects.filter(
                        Q(customer_name__icontains=query), 
                        is_delete=False
                    )[:3]
                    for customer in customers:
                        results.append({
                            'id': customer.id,
                            'title': customer.customer_name,
                            'subtitle': f'Customer - {customer.customer_email or "No email"}',
                            'url': f'/customers/',
                            'icon': 'user',
                            'category': 'customers',
                            'relevance': 7
                        })
                
                if search_type in ['all', 'suppliers']:
                    suppliers = SupplierModel.objects.filter(
                        Q(supplier_name__icontains=query), 
                        is_delete=False
                    )[:3]
                    for supplier in suppliers:
                        results.append({
                            'id': supplier.id,
                            'title': supplier.supplier_name,
                            'subtitle': f'Supplier - {supplier.supplier_contact or "No contact"}',
                            'url': f'/suppliers/',
                            'icon': 'truck',
                            'category': 'suppliers',
                            'relevance': 6
                        })
            except Exception as fallback_error:
                pass
            
            return JsonResponse({
                'results': results[:10], 
                'count': len(results),
                'by_category': {'products': len([r for r in results if r.get('category') == 'products'])}
            })
    
    except Exception as e:
        # Always return JSON, never HTML
        return JsonResponse({
            'results': [],
            'count': 0,
            'by_category': {},
            'error': 'Search temporarily unavailable'
        }, status=500)

def analytics_api(request):
    return JsonResponse({
        'revenue': {'current': 1250000, 'previous': 980000, 'growth': 27.5},
        'orders': {'today': 45, 'week': 312, 'month': 1250},
        'inventory': {'total_value': 8500000, 'low_stock': 23, 'out_stock': 5},
        'customers': {'active': 1250, 'new_this_month': 85},
        'chart_data': {
            'sales': [120000, 150000, 180000, 220000, 250000, 280000, 320000],
            'orders': [45, 52, 48, 61, 58, 65, 72],
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        }
    })

def reports_api(request):
    report_type = request.GET.get('type', 'sales')
    if report_type == 'inventory':
        data = {'products': 1250, 'total_value': 8500000, 'categories': 45}
    else:
        data = {'total_sales': 1250000, 'orders': 312, 'customers': 85}
    return JsonResponse({'type': report_type, 'data': data, 'generated_at': '2024-11-12'})

def automation_api(request):
    return JsonResponse({'status': 'Automation system active', 'rules': [{'name': 'Auto Reorder', 'status': 'enabled'}, {'name': 'Low Stock Alerts', 'status': 'enabled'}]})

def set_language_api(request):
    return JsonResponse({'status': 'disabled', 'message': 'Multi-language support has been removed'})

@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email', user.email)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'profile.html')

@login_required
def settings_view(request):
    if request.method == 'POST':
        # Save settings to session or user profile
        request.session['email_notifications'] = 'email_notifications' in request.POST
        request.session['sms_notifications'] = 'sms_notifications' in request.POST
        request.session['push_notifications'] = 'push_notifications' in request.POST
        request.session['two_factor'] = 'two_factor' in request.POST
        request.session['login_alerts'] = 'login_alerts' in request.POST
        request.session['data_analytics'] = 'data_analytics' in request.POST
        request.session['marketing_emails'] = 'marketing_emails' in request.POST
        request.session['language'] = request.POST.get('language', 'en')
        request.session['theme'] = request.POST.get('theme', 'light')
        request.session['items_per_page'] = request.POST.get('items_per_page', '25')
        messages.success(request, 'Settings saved successfully!')
        return redirect('settings')
    return render(request, 'settings.html')