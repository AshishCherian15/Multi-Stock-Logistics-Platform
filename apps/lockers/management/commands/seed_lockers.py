from django.core.management.base import BaseCommand
from apps.lockers.models import LockerType, Locker

class Command(BaseCommand):
    help = 'Seed lockers database'

    def handle(self, *args, **kwargs):
        types_data = [
            {'name': 'Personal Locker', 'size': 'small', 'hourly': 20, 'daily': 100, 'weekly': 600, 'monthly': 2000, 'climate': False},
            {'name': 'Parcel Locker', 'size': 'medium', 'hourly': 30, 'daily': 150, 'weekly': 900, 'monthly': 3000, 'climate': False},
            {'name': 'Refrigerated Locker', 'size': 'medium', 'hourly': 50, 'daily': 250, 'weekly': 1500, 'monthly': 5000, 'climate': True},
            {'name': 'Document Vault', 'size': 'small', 'hourly': 25, 'daily': 120, 'weekly': 700, 'monthly': 2500, 'climate': True},
            {'name': 'Luggage Locker', 'size': 'large', 'hourly': 40, 'daily': 200, 'weekly': 1200, 'monthly': 4000, 'climate': False},
        ]

        locker_types = {}
        for type_data in types_data:
            lt, _ = LockerType.objects.get_or_create(
                name=type_data['name'],
                defaults={
                    'size': type_data['size'],
                    'hourly_rate': type_data['hourly'],
                    'daily_rate': type_data['daily'],
                    'weekly_rate': type_data['weekly'],
                    'monthly_rate': type_data['monthly'],
                    'has_climate_control': type_data['climate'],
                    'has_security_monitoring': True,
                    'is_active': True
                }
            )
            locker_types[type_data['name']] = lt

        lockers_data = [
            {'number': 'L-A101', 'type': 'Personal Locker', 'location': 'Building A, Floor 1, Section A'},
            {'number': 'L-A102', 'type': 'Parcel Locker', 'location': 'Building A, Floor 1, Section A'},
            {'number': 'L-B201', 'type': 'Refrigerated Locker', 'location': 'Building B, Floor 2, Section A'},
            {'number': 'L-B202', 'type': 'Document Vault', 'location': 'Building B, Floor 2, Section B'},
            {'number': 'L-C301', 'type': 'Luggage Locker', 'location': 'Building C, Floor 3, Section A'},
            {'number': 'L-C302', 'type': 'Personal Locker', 'location': 'Building C, Floor 3, Section B'},
            {'number': 'L-D401', 'type': 'Parcel Locker', 'location': 'Building D, Floor 4, Section A'},
            {'number': 'L-D402', 'type': 'Refrigerated Locker', 'location': 'Building D, Floor 4, Section B'},
            {'number': 'L-A103', 'type': 'Document Vault', 'location': 'Building A, Floor 1, Section B'},
            {'number': 'L-B203', 'type': 'Luggage Locker', 'location': 'Building B, Floor 2, Section C'},
        ]

        for locker_data in lockers_data:
            Locker.objects.get_or_create(
                locker_number=locker_data['number'],
                defaults={
                    'locker_type': locker_types[locker_data['type']],
                    'location': locker_data['location'],
                    'status': 'available',
                    'is_active': True
                }
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded 10 lockers'))
