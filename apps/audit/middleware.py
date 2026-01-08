from django.utils.deprecation import MiddlewareMixin
from django.db import connection
import json
import requests

class AuditLogMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.user.is_authenticated and request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            try:
                ip = self.get_client_ip(request)
                geo_data = self.get_geolocation(ip)
                
                from .models import AuditLog
                
                AuditLog.objects.create(
                    user=request.user,
                    action_type=request.method,
                    model_name=request.path,
                    ip_address=ip,
                    description=json.dumps(geo_data)
                )
            except:
                pass
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_geolocation(self, ip):
        """Get geographic data for IP address"""
        if ip in ['127.0.0.1', 'localhost']:
            return {'city': 'Local', 'country': 'Local', 'risk': 'low'}
        
        try:
            # Use free IP geolocation API
            response = requests.get(f'http://ip-api.com/json/{ip}', timeout=2)
            if response.status_code == 200:
                data = response.json()
                return {
                    'city': data.get('city', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'risk': self.assess_risk(ip, data)
                }
        except:
            pass
        
        return {'city': 'Unknown', 'country': 'Unknown', 'risk': 'unknown'}
    
    def assess_risk(self, ip, geo_data):
        """Assess IP risk level"""
        # Simple risk assessment
        suspicious_keywords = ['vpn', 'proxy', 'tor', 'hosting']
        isp = geo_data.get('isp', '').lower()
        
        if any(kw in isp for kw in suspicious_keywords):
            return 'high'
        
        # Check if IP is from known datacenter ranges
        if geo_data.get('org', '').lower().find('datacenter') != -1:
            return 'medium'
        
        return 'low'
