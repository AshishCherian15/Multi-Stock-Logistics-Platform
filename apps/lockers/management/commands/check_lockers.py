from django.core.management.base import BaseCommand
from lockers.models import Locker

class Command(BaseCommand):
    help = 'Check locker IDs'

    def handle(self, *args, **options):
        lockers = Locker.objects.all()
        print(f"\nTotal Lockers: {lockers.count()}\n")
        for l in lockers:
            print(f"ID: {l.id}, Number: {l.locker_number}, Status: {l.status}")
