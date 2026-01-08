from permissions.decorators import get_user_role
from permissions.models import PERMISSION_MATRIX

def user_permissions(request):
    """Add user role and permissions to template context"""
    if not request.user.is_authenticated:
        return {'user_role': 'guest', 'permissions': {}}
    
    user_role = get_user_role(request.user)
    permissions = PERMISSION_MATRIX.get(user_role, {})
    
    return {
        'user_role': user_role,
        'permissions': permissions,
    }
