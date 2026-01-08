from django.core.management.base import BaseCommand
from categories.models import Category
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Fix category names to match requirements'

    def handle(self, *args, **kwargs):
        superuser = User.objects.filter(is_superuser=True).first()
        
        # Update existing categories
        updates = {
            'Fashion': 'Apparel',
            'Office Supplies': 'Books & Stationery',
            'Home & Garden': 'Home & Kitchen',
            'Sports': 'Sports & Fitness'
        }
        
        for old_name, new_name in updates.items():
            cat = Category.objects.filter(name=old_name).first()
            if cat:
                cat.name = new_name
                cat.save()
                self.stdout.write(f'Updated: {old_name} -> {new_name}')
        
        # Add Tools if not exists
        if not Category.objects.filter(name='Tools').exists():
            Category.objects.create(
                name='Tools',
                code='TOOLS',
                category_type='product',
                icon='fa-tools',
                description='Hardware and tools',
                created_by=superuser
            )
            self.stdout.write('Created: Tools')
        
        self.stdout.write(self.style.SUCCESS('Categories fixed'))
