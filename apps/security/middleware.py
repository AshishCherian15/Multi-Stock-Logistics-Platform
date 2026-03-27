from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import time
from collections import defaultdict

class RateLimitMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.requests = defaultdict(list)
        
    def process_request(self, request):
        if request.path.startswith('/api/'):
            ip = request.META.get('REMOTE_ADDR')
            now = time.time()
            self.requests[ip] = [req_time for req_time in self.requests[ip] if now - req_time < 3600]
            
            if len(self.requests[ip]) >= 1000:
                return JsonResponse({'error': 'Rate limit exceeded'}, status=429)
            
            self.requests[ip].append(now)

class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response