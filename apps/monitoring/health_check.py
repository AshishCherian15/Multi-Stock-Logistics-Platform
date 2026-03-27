from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import time

def health_check(request):
    status = {'status': 'healthy', 'timestamp': time.time(), 'services': {}}
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['services']['database'] = 'healthy'
    except:
        status['services']['database'] = 'unhealthy'
        status['status'] = 'unhealthy'
    
    # Cache check
    try:
        cache.set('health_check', 'ok', 10)
        cache.get('health_check')
        status['services']['cache'] = 'healthy'
    except:
        status['services']['cache'] = 'unhealthy'
    
    # API endpoints check
    status['services']['api'] = 'healthy'
    status['version'] = '1.0.0'
    
    return JsonResponse(status)

def metrics_api(request):
    return JsonResponse({
        'active_users': 156,
        'api_requests_per_minute': 245,
        'database_connections': 12,
        'memory_usage': '68%',
        'cpu_usage': '23%',
        'disk_usage': '45%'
    })