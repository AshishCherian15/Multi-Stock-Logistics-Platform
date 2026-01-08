from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.generic import RedirectView
from . import views, views_superadmin, views_dashboards, views_purge
from . import views_guest
from supplier.views import supplier_management_view

urlpatterns = [
    path('favicon.ico', RedirectView.as_view(url='/static/images/favicon.svg', permanent=True)),
    path('admin-panel/', lambda request: render(request, 'admin/admin_panel.html'), name='admin_panel'),
    path('admin/purge/', views_purge.purge_data, name='purge_data'),
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('/dashboard/') if request.user.is_authenticated else redirect('/auth/'), name='home'),
    path('dashboard/', views.dashboard_router, name='dashboard'),
    path('dashboard/superadmin/', views_superadmin.superadmin_dashboard, name='superadmin_dashboard'),
    path('dashboard/admin/', views_superadmin.superadmin_dashboard, name='admin_dashboard'),
    path('dashboard/supervisor/', views_superadmin.superadmin_dashboard, name='supervisor_dashboard'),
    path('dashboard/staff/', views_superadmin.superadmin_dashboard, name='staff_dashboard'),
    path('dashboard/customer/', views_dashboards.customer_dashboard, name='customer_dashboard'),
    path('dashboard/guest/', views_guest.guest_dashboard, name='guest_dashboard'),
    path('api/dashboard-metrics/', views_superadmin.dashboard_metrics_api, name='dashboard_metrics'),
    path('api/dashboard-charts/', views_superadmin.dashboard_charts_api, name='dashboard_charts'),
    path('api/dashboard-heatmap/', views_superadmin.dashboard_heatmap_api, name='dashboard_heatmap'),
    path('api/dashboard-bubble/', views_superadmin.dashboard_bubble_api, name='dashboard_bubble'),
    path('auth/', include('auth_system.urls')),
    
    # Forums
    path('forums/', include('forums.urls')),
    path('multistock/', lambda request: redirect('/products/marketplace/'), name='multistock_redirect'),
    path('marketplace/', lambda request: redirect('/products/marketplace/'), name='marketplace'),
    
    path('api/goods/', include('goods.urls')),
    path('products/', include('products.urls')),
    path('stock/', include('stock.urls')),
    path('api/warehouse/', include('warehouse.urls')),
    path('warehouses/', include('warehouse.urls')),
    path('api/customer/', include('customer.urls')),
    path('customers/', include('customers.urls')),
    path('api/supplier/', include('supplier.urls')),
    path('suppliers/', include('suppliers.urls')),
    path('suppliers/manage/', supplier_management_view, name='suppliers_manage_direct'),
    path('team/', include('team.urls')),
    
    # UNIFIED DASHBOARD FOR SUPERADMIN & ADMIN
    # Both roles now use the same dashboard with permission-based restrictions
    path('admin-panel/', lambda request: redirect('/dashboard/team/'), name='admin_panel_redirect'),
    path('superadmin-panel/', lambda request: redirect('/dashboard/team/'), name='superadmin_panel_redirect'),
    
    # Keep individual panel URLs but redirect to unified dashboard
    path('admin-panel/', include('admin_panel.urls')),
    path('supervisor-panel/', include('supervisor_panel.urls')),
    path('staff-panel/', include('staff_panel.urls')),
    path('guest/', include('guest.urls')),
    path('superadmin-panel/', include('superadmin_panel.urls')),

    path('barcode/', include('barcode.urls')),
    path('orders/', include('orders.urls')),
    path('reports/', include('reports.urls')),
    path('pos/', include('pos.urls')),
    path('expenses/', include('expenses.urls')),
    path('inventory/', lambda request: redirect('/products/'), name='inventory_redirect'),
    path('inventory/', include('inventory.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('profile/', include('profile.urls')),
    path('pages/', include('pages.urls')),
    path('messages/', include('messaging.urls')),
    path('adjustments/', include('adjustments.urls')),

    path('quotations/', include('quotations.urls')),
    path('returns/', include('returns.urls')),
    path('transfers/', include('transfers.urls')),
    path('users/', include('users.urls')),
    path('system-settings/', include('settings.urls')),
    path('rentals/', include('rentals.urls')),

    path('storage/', include('storage.urls')),
    path('lockers/', include('lockers.urls')),
    path('credit/', include('credit.urls')),
    path('coupons/', include('coupons.urls')),
    path('audit/', include('audit.urls')),

    path('categories/', include('categories.urls')),
    path('billing/', include('billing.urls')),
    path('permissions/', include('permissions.urls')),
    path('shipping/', include('shipping.urls')),
    path('analytics/', include('analytics.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('cart/', include('cart.urls')),
    path('wishlist/', include('wishlist.urls')),
    path('payments/', include('payments.urls')),
    path('accounts/', include('allauth.urls')),
    # Static pages
    path('about/', include('about.urls')),
    path('help/', lambda request: redirect('/about/'), name='help'),
    path('legal/', include('legal.urls')),
    # User pages
    path('mine/', lambda request: render(request, 'mine.html'), name='mine'),
    # path('profile/', views.profile_view, name='profile'),  # Using apps.profile.urls instead
    path('settings/', views.settings_view, name='settings'),
    path('notifications/', lambda request: render(request, 'notifications.html'), name='notifications_page'),
    # System pages
    path('system-status/', lambda request: render(request, 'system_status.html') if hasattr(request.user, 'role') and request.user.role.role != 'customer' else redirect('/dashboard/'), name='system_status'),
    path('mobile/api-docs/', lambda request: render(request, 'mobile/api_docs.html'), name='mobile_api_docs'),
    # API endpoints
    path('api/', include('api.urls')),
    path('search/', include('search.urls')),
    path('api/search/', views.search_api, name='search_api'),
    path('api/automation/', views.automation_api, name='automation_api'),
    path('api/reports/', views.reports_api, name='reports_api'),
    path('health/', lambda request: JsonResponse({'status': 'healthy'}), name='health_check'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)