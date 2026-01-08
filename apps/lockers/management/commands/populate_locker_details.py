from django.core.management.base import BaseCommand
from apps.lockers.models import Locker, LockerType
import random

class Command(BaseCommand):
    help = 'Populate existing lockers with detailed information'

    def handle(self, *args, **kwargs):
        lockers = Locker.objects.all()
        
        if not lockers.exists():
            self.stdout.write(self.style.WARNING('No lockers found in database'))
            return
        
        locations = ['Building A - Floor 1', 'Building A - Floor 2', 'Building B - Floor 1', 'Building B - Floor 2', 'Main Lobby', 'East Wing', 'West Wing']
        names = ['Standard Locker', 'Premium Locker', 'Secure Storage', 'Smart Locker', 'Climate Locker']
        
        updated_count = 0
        
        for locker in lockers:
            # Update location
            if not locker.location or locker.location == 'Main Building':
                locker.location = random.choice(locations)
            
            # Add notes with detailed info
            size_name = locker.locker_type.get_size_display()
            locker.notes = f"{random.choice(names)} - {size_name}. Located in {locker.location}. Features: PIN access, 24/7 monitoring, climate control."
            
            locker.save()
            updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} lockers with detailed information'))
