from django.core.management.base import BaseCommand
from warehouse.models import ListModel

class Command(BaseCommand):
    help = 'Update warehouse images with unique photos'

    def handle(self, *args, **kwargs):
        images = [
            'https://images.unsplash.com/photo-1553413077-190dd305871c?w=400',
            'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400',
            'https://images.unsplash.com/photo-1565610222536-ef125c59da2e?w=400',
            'https://images.unsplash.com/photo-1587293852726-70cdb56c2866?w=400',
            'https://images.unsplash.com/photo-1566576721346-d4a3b4eaeb55?w=400',
        ]
        
        warehouses = ListModel.objects.filter(is_delete=False)
        updated = 0
        
        for i, wh in enumerate(warehouses):
            wh.warehouse_image = images[i % len(images)]
            wh.save()
            updated += 1
            self.stdout.write(f'Updated {wh.warehouse_name}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated} warehouse images'))
