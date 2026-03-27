"""
handle_expirations – mark overdue/expired records across every app.

Run manually:
    python manage.py handle_expirations

Schedule with cron (Linux/Mac) or Windows Task Scheduler:
    0 * * * * /path/to/venv/bin/python manage.py handle_expirations   # every hour

Flags:
    --dry-run   Print what would change without writing to the database.
    --quiet     Suppress per-record output (useful in cron).
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction


class Command(BaseCommand):
    help = 'Mark expired quotations, bookings, and coupons across the platform.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would change without modifying the database.',
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Suppress per-category output.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        quiet = options['quiet']
        now = timezone.now()
        results = []

        def log(msg):
            if not quiet:
                self.stdout.write(msg)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN – no database changes will be made.\n'))

        # ── Quotations ─────────────────────────────────────────────────────────
        try:
            from quotations.models import Quotation
            qs = Quotation.objects.filter(
                expires_at__lt=now,
                status__in=('draft', 'sent', 'approved'),
            )
            count = qs.count()
            if count and not dry_run:
                with transaction.atomic():
                    qs.update(status='expired')
            results.append(('Quotations expired', count))
            log(f'  Quotations marked expired:      {count}')
        except Exception as exc:
            self.stderr.write(f'  Quotations – error: {exc}')

        # ── Coupons ────────────────────────────────────────────────────────────
        try:
            from coupons.models import Coupon
            qs = Coupon.objects.filter(valid_until__lt=now, is_active=True)
            count = qs.count()
            if count and not dry_run:
                with transaction.atomic():
                    qs.update(is_active=False)
            results.append(('Coupons deactivated', count))
            log(f'  Coupons deactivated:            {count}')
        except Exception as exc:
            self.stderr.write(f'  Coupons – error: {exc}')

        # ── Storage bookings ───────────────────────────────────────────────────
        try:
            from storage.models import StorageBooking
            qs = StorageBooking.objects.filter(
                end_date__lt=now,
                status='active',
            )
            count = qs.count()
            if count and not dry_run:
                with transaction.atomic():
                    qs.update(status='expired')
            results.append(('Storage bookings expired', count))
            log(f'  Storage bookings expired:       {count}')
        except Exception as exc:
            self.stderr.write(f'  Storage bookings – error: {exc}')

        # ── Locker bookings ────────────────────────────────────────────────────
        try:
            from lockers.models import LockerBooking
            qs = LockerBooking.objects.filter(
                end_date__lt=now,
                status='active',
            )
            count = qs.count()
            if count and not dry_run:
                with transaction.atomic():
                    qs.update(status='overdue')
            results.append(('Locker bookings overdue', count))
            log(f'  Locker bookings marked overdue: {count}')
        except Exception as exc:
            self.stderr.write(f'  Locker bookings – error: {exc}')

        # ── Rental bookings ────────────────────────────────────────────────────
        try:
            from rentals.models import RentalBooking
            qs = RentalBooking.objects.filter(
                end_date__lt=now,
                actual_return_date__isnull=True,
                status='active',
            )
            count = qs.count()
            if count and not dry_run:
                with transaction.atomic():
                    qs.update(status='overdue')
            results.append(('Rental bookings overdue', count))
            log(f'  Rental bookings marked overdue: {count}')
        except Exception as exc:
            self.stderr.write(f'  Rental bookings – error: {exc}')

        # ── Announcements (settings app) ───────────────────────────────────────
        try:
            from settings.models import Announcement
            qs = Announcement.objects.filter(
                expires_at__lt=now,
                is_active=True,
            )
            count = qs.count()
            if count and not dry_run:
                with transaction.atomic():
                    qs.update(is_active=False)
            results.append(('Announcements deactivated', count))
            log(f'  Announcements deactivated:      {count}')
        except Exception as exc:
            self.stderr.write(f'  Announcements – error: {exc}')

        # ── Summary ────────────────────────────────────────────────────────────
        total = sum(n for _, n in results)
        suffix = ' (dry run)' if dry_run else ''
        self.stdout.write(
            self.style.SUCCESS(
                f'\nhandle_expirations complete{suffix}: {total} record(s) updated across '
                f'{len(results)} categories.'
            )
        )
