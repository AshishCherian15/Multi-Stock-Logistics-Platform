from django.core.management.base import BaseCommand
from apps.storage.models import StorageUnit

class Command(BaseCommand):
    help = 'Update storage unit images with unique Unsplash URLs'

    def handle(self, *args, **kwargs):
        units = StorageUnit.objects.all()
        
        images = [
            'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400',
            'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=400',
            'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=400',
            'https://images.unsplash.com/photo-1600573472591-ee6b68d14c68?w=400',
            'https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?w=400',
            'https://images.unsplash.com/photo-1600585154526-990dced4db0d?w=400',
            'https://images.unsplash.com/photo-1600607687644-c7171b42498f?w=400',
            'https://images.unsplash.com/photo-1600573472550-8090b5e0745e?w=400',
        ]
        
        for idx, unit in enumerate(units):
            image_url = images[idx % len(images)]
            if not hasattr(unit, 'image_url'):
                unit.features = unit.features or {}
                unit.features['image_url'] = image_url
                unit.save()
                self.stdout.write(f'Updated {unit.unit_number} with image')
        
        self.stdout.write(self.style.SUCCESS(f'Updated {units.count()} storage units'))
