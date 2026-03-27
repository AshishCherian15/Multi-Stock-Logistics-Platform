from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import ListModel
from .serializers import GoodsSerializer

class GoodsViewSet(viewsets.ModelViewSet):
    queryset = ListModel.objects.filter(is_delete=False)
    serializer_class = GoodsSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['goods_class', 'goods_brand', 'goods_supplier']
    search_fields = ['goods_code', 'goods_desc']

    def get_queryset(self):
        """
        SuperAdmin sees all products.
        Others see only their own products (filtered by openid).
        """
        user = self.request.user
        if user.is_superuser:
            return ListModel.objects.filter(is_delete=False)
        
        # Check for role-based access
        try:
            from permissions.decorators import get_user_role
            role = get_user_role(user)
            if role == 'superadmin':
                return ListModel.objects.filter(is_delete=False)
        except:
            pass
            
        # Default: Filter by user's openid
        openid = getattr(user, 'openid', user.username)
        return ListModel.objects.filter(openid=openid, is_delete=False)

    def perform_create(self, serializer):
        """
        Set openid to current user on creation.
        Admin CANNOT create products (only edit).
        """
        user = self.request.user
        
        # Check if Admin trying to create product
        try:
            from permissions.decorators import get_user_role
            role = get_user_role(user)
            if role == 'admin':
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("Admin can only edit products, not create new ones.")
        except PermissionDenied:
            raise
        except:
            pass
        
        openid = getattr(user, 'openid', user.username)
        serializer.save(openid=openid, created_by=user)
    
    def perform_destroy(self, instance):
        """
        Soft delete for Admin and below.
        Only SuperAdmin can hard delete.
        """
        user = self.request.user
        if user.is_superuser:
            instance.delete()  # Hard delete for SuperAdmin
        else:
            try:
                from permissions.decorators import get_user_role
                role = get_user_role(user)
                if role == 'superadmin':
                    instance.delete()  # Hard delete
                else:
                    instance.is_delete = True  # Soft delete for Admin
                    instance.save()
            except:
                instance.is_delete = True  # Soft delete as fallback
                instance.save()