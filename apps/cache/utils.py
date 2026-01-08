from django.core.cache import cache
from django.http import JsonResponse
import json

def cache_api_response(key, data, timeout=300):
    cache.set(key, json.dumps(data), timeout)

def get_cached_response(key):
    cached = cache.get(key)
    return json.loads(cached) if cached else None

def cached_analytics_api(request):
    cache_key = 'analytics_data'
    cached_data = get_cached_response(cache_key)
    
    if cached_data:
        return JsonResponse(cached_data)
    
    data = {
        'revenue': {'current': 125000, 'previous': 98000, 'growth': 27.5},
        'orders': {'today': 45, 'week': 312, 'month': 1250},
        'inventory': {'total_value': 850000, 'low_stock': 23, 'out_stock': 5},
        'chart_data': {
            'sales': [12000, 15000, 18000, 22000, 25000, 28000, 32000],
            'orders': [45, 52, 48, 61, 58, 65, 72],
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        }
    }
    
    cache_api_response(cache_key, data, 60)
    return JsonResponse(data)