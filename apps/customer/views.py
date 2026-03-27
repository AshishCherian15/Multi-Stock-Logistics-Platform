from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import ListModel
from .serializers import CustomerSerializer

# Import RBAC helper
from permissions.decorators import check_permission

# Custom DRF permission class for customer CRUD
class CustomerPermission(BasePermission):
    """
    RBAC permission class for Customer ViewSet
    - GET (list/retrieve): customers.view permission
    - POST (create): customers.create permission
    - PUT/PATCH (update): customers.edit permission
    - DELETE: customers.delete permission
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        if request.method == 'GET':
            return check_permission(request.user, 'customers', 'view')
        elif request.method == 'POST':
            return check_permission(request.user, 'customers', 'create')
        elif request.method in ['PUT', 'PATCH']:
            return check_permission(request.user, 'customers', 'edit')
        elif request.method == 'DELETE':
            return check_permission(request.user, 'customers', 'delete')
        return False

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = ListModel.objects.filter(is_delete=False)
    serializer_class = CustomerSerializer
    permission_classes = [CustomerPermission]  # RBAC permission
    
    def get_queryset(self):
        """SuperAdmin sees all customers, others see only their store's customers."""
        user = self.request.user
        if user.is_superuser:
            return ListModel.objects.filter(is_delete=False)
        
        try:
            from permissions.decorators import get_user_role
            role = get_user_role(user)
            if role == 'superadmin':
                return ListModel.objects.filter(is_delete=False)
        except:
            pass
        
        openid = getattr(user, 'openid', user.username)
        return ListModel.objects.filter(openid=openid, is_delete=False)
    
    def perform_create(self, serializer):
        """Set openid on customer creation"""
        openid = getattr(self.request.user, 'openid', self.request.user.username)
        serializer.save(openid=openid)
    
    def perform_destroy(self, instance):
        """Admin can only soft delete customers."""
        user = self.request.user
        if user.is_superuser:
            instance.delete()  # Hard delete
        else:
            try:
                from permissions.decorators import get_user_role
                if get_user_role(user) == 'superadmin':
                    instance.delete()
                else:
                    instance.is_delete = True  # Soft delete
                    instance.save()
            except:
                instance.is_delete = True
                instance.save()