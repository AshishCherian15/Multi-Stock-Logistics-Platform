from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Public paths that don't require authentication
        public_paths = [
            reverse('auth:login_selection'),
            reverse('auth:team_login'),
            reverse('auth:customer_login'),
            reverse('auth:register'),
            reverse('auth:logout'),
            reverse('auth:forgot_password'),
            reverse('auth:guest_access'),
            '/admin/',
            '/static/',
            '/media/',
            '/about/',
            '/help/',
            '/api/goods/',
            '/health/',
            '/forums/',
            '/guest/',  # Guest access
        ]
        
        # Admin-only URLs that customers cannot access
        admin_only_urls = [
            '/products/create/',
            '/products/edit/',
            '/products/delete/',
            '/inventory/',
            '/stock/',
            '/customers/',
            '/suppliers/',
            '/team/',
            '/warehouses/',
            '/categories/create/',
            '/categories/edit/',
            '/barcode/',
            '/analytics/',
            '/reports/',
            '/expenses/',
            '/permissions/',
            '/audit/',
            '/admin-panel/',
            '/system-settings/',
            '/api/dashboard-metrics/',
            '/api/dashboard-charts/',
        ]
        
        # Check if path is public
        is_public = any(request.path.startswith(path) for path in public_paths)
        
        # Allow public access to home page
        if request.path == '/' or request.path == '/home/':
            is_public = True
        
        # CUSTOMER ROLE RESTRICTIONS
        if request.user.is_authenticated and hasattr(request.user, 'role'):
            if request.user.role.role == 'customer':
                # Block admin URLs for customers
                for admin_url in admin_only_urls:
                    if request.path.startswith(admin_url):
                        return HttpResponseForbidden(
                            '<h1>Access Denied</h1>'
                            '<p>Customers do not have permission to access this page.</p>'
                            '<p><a href="/dashboard/">Return to Dashboard</a></p>'
                        )
        
        # FORCE login selection if session not verified (only for protected pages)
        if not is_public and not request.session.get('login_verified', False):
            # Clear any existing authentication
            if request.user.is_authenticated:
                from django.contrib.auth import logout
                logout(request)
            request.session.flush()
            return redirect('auth:login_selection')
        
        response = self.get_response(request)
        return response
