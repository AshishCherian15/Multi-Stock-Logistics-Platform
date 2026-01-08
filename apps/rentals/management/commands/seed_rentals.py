from django.core.management.base import BaseCommand
from apps.rentals.models import RentalCategory, RentalItem

class Command(BaseCommand):
    help = 'Seed rental items database'

    def handle(self, *args, **kwargs):
        categories = {
            'equipment': RentalCategory.objects.get_or_create(name='Equipment', category_type='equipment', description='Construction and industrial equipment')[0],
            'vehicle': RentalCategory.objects.get_or_create(name='Vehicles', category_type='vehicle', description='Cars, trucks, and transportation')[0],
            'event': RentalCategory.objects.get_or_create(name='Events', category_type='event', description='Event and party equipment')[0],
        }

        items = [
            {'category': 'equipment', 'name': 'Power Drill Set', 'description': 'Professional cordless power drill with multiple bits and carrying case. Perfect for construction and DIY projects.', 'hourly': 50, 'daily': 300, 'weekly': 1800, 'monthly': 6000},
            {'category': 'equipment', 'name': 'Concrete Mixer', 'description': 'Heavy-duty concrete mixer for construction sites. 150L capacity with electric motor.', 'hourly': 100, 'daily': 600, 'weekly': 3500, 'monthly': 12000},
            {'category': 'equipment', 'name': 'Scaffolding Set', 'description': 'Complete scaffolding system with platforms and safety rails. Suitable for 3-story buildings.', 'hourly': 0, 'daily': 800, 'weekly': 5000, 'monthly': 18000},
            {'category': 'vehicle', 'name': 'Pickup Truck', 'description': 'Toyota Hilux 4x4 pickup truck with 1-ton payload capacity. Ideal for material transport.', 'hourly': 200, 'daily': 1500, 'weekly': 9000, 'monthly': 30000},
            {'category': 'vehicle', 'name': 'Cargo Van', 'description': 'Spacious cargo van with 3m³ loading space. Perfect for deliveries and moving.', 'hourly': 150, 'daily': 1000, 'weekly': 6000, 'monthly': 20000},
            {'category': 'vehicle', 'name': 'Forklift', 'description': '3-ton capacity forklift with 5m lift height. Diesel powered for warehouse operations.', 'hourly': 250, 'daily': 1800, 'weekly': 11000, 'monthly': 40000},
            {'category': 'event', 'name': 'Wedding Tent Package', 'description': 'Complete wedding tent setup for 200 guests including tables, chairs, and lighting.', 'hourly': 0, 'daily': 5000, 'weekly': 30000, 'monthly': 0},
            {'category': 'event', 'name': 'Sound System Pro', 'description': 'Professional PA system with speakers, mixer, and microphones. Suitable for events up to 500 people.', 'hourly': 300, 'daily': 2000, 'weekly': 12000, 'monthly': 40000},
            {'category': 'event', 'name': 'LED Stage Lighting', 'description': 'Complete LED stage lighting package with DMX controller and moving heads.', 'hourly': 200, 'daily': 1500, 'weekly': 9000, 'monthly': 30000},
            {'category': 'equipment', 'name': 'Generator 10KVA', 'description': 'Silent diesel generator with 10KVA output. Automatic voltage regulation and fuel efficiency.', 'hourly': 150, 'daily': 1000, 'weekly': 6000, 'monthly': 20000},
        ]

        for item_data in items:
            cat = categories[item_data['category']]
            RentalItem.objects.get_or_create(
                name=item_data['name'],
                defaults={
                    'category': cat,
                    'description': item_data['description'],
                    'status': 'available',
                    'hourly_rate': item_data['hourly'],
                    'daily_rate': item_data['daily'],
                    'weekly_rate': item_data['weekly'],
                    'monthly_rate': item_data['monthly'],
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded 10 rental items'))
