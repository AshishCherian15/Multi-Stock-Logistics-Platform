from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import AccessRequest

@receiver(post_save, sender=User)
def create_access_request_for_new_user(sender, instance, created, **kwargs):
    """Auto-create access request when new non-staff user is created"""
    if created and not instance.is_staff and not instance.is_superuser:
        AccessRequest.objects.get_or_create(
            user=instance,
            defaults={
                'requested_role': 'staff',
                'status': 'pending',
                'reason': f'{instance.username} requesting staff access'
            }
        )
