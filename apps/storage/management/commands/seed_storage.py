from django.core.management.base import BaseCommand
from apps.storage.models import StorageUnit

class Command(BaseCommand):
    help = 'Seed storage units database'

    def handle(self, *args, **kwargs):
        units = [
            {'number': 'CS-101', 'type': 'locker', 'name': 'Cold Storage', 'size': 50, 'location': 'Building A', 'floor': 1, 'zone': 'Zone A', 'price': 3000, 'climate': True},
            {'number': 'DS-102', 'type': 'mini', 'name': 'Dry Storage', 'size': 100, 'location': 'Building A', 'floor': 1, 'zone': 'Zone B', 'price': 2500, 'climate': False},
            {'number': 'PR-201', 'type': 'standard', 'name': 'Pallet Rack', 'size': 200, 'location': 'Building B', 'floor': 2, 'zone': 'Zone A', 'price': 5000, 'climate': False},
            {'number': 'BC-202', 'type': 'large', 'name': 'Bulk Container', 'size': 500, 'location': 'Building B', 'floor': 2, 'zone': 'Zone B', 'price': 10000, 'climate': False},
            {'number': 'AV-301', 'type': 'standard', 'name': 'Archive Vault', 'size': 150, 'location': 'Building C', 'floor': 3, 'zone': 'Zone A', 'price': 4000, 'climate': True},
            {'number': 'ML-302', 'type': 'locker', 'name': 'Mini Locker', 'size': 25, 'location': 'Building C', 'floor': 3, 'zone': 'Zone B', 'price': 1500, 'climate': False},
            {'number': 'SL-401', 'type': 'mini', 'name': 'Standard Locker', 'size': 75, 'location': 'Building D', 'floor': 4, 'zone': 'Zone A', 'price': 2000, 'climate': False},
            {'number': 'LL-402', 'type': 'standard', 'name': 'Large Locker', 'size': 120, 'location': 'Building D', 'floor': 4, 'zone': 'Zone B', 'price': 3500, 'climate': False},
            {'number': 'CC-103', 'type': 'large', 'name': 'Climate Controlled Room', 'size': 300, 'location': 'Building A', 'floor': 1, 'zone': 'Zone C', 'price': 8000, 'climate': True},
            {'number': 'SV-203', 'type': 'standard', 'name': 'Secure Vault', 'size': 180, 'location': 'Building B', 'floor': 2, 'zone': 'Zone C', 'price': 6000, 'climate': True},
        ]

        for unit_data in units:
            StorageUnit.objects.get_or_create(
                unit_number=unit_data['number'],
                defaults={
                    'type': unit_data['type'],
                    'size_sqft': unit_data['size'],
                    'location': unit_data['location'],
                    'floor': unit_data['floor'],
                    'zone': unit_data['zone'],
                    'status': 'available',
                    'price_per_month': unit_data['price'],
                    'is_climate_controlled': unit_data['climate'],
                    'features': {
                        'humidity_control': unit_data['climate'],
                        'temperature_monitoring': unit_data['climate'],
                        'access_logs': True,
                        'fireproofing': unit_data['type'] in ['standard', 'large'],
                        'insurance_coverage': True
                    }
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded 10 storage units'))
