"""
cleanup_sessions – delete expired DB-backed sessions and optionally old audit logs.

Django's built-in `clearsessions` only removes sessions expired by SESSION_COOKIE_AGE.
This command adds:
  • A --days flag to delete sessions older than N days regardless of cookie age.
  • Optional pruning of old audit log entries (--prune-audit-days).

Schedule example (cron, daily at 2 AM):
    0 2 * * * /path/to/venv/bin/python manage.py cleanup_sessions

Windows Task Scheduler:
    Program: python
    Arguments: manage.py cleanup_sessions
    Start in: C:\\path\\to\\project
"""
from django.core.management.base import BaseCommand
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone
import datetime


class Command(BaseCommand):
    help = 'Delete expired sessions and optionally prune old audit log entries.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=0,
            help='Also delete sessions older than N days (0 = only expired by cookie age).',
        )
        parser.add_argument(
            '--prune-audit-days',
            type=int,
            default=0,
            dest='prune_audit_days',
            help='Delete audit log entries older than N days (0 = skip).',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print counts without deleting.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        extra_days = options['days']
        prune_audit_days = options['prune_audit_days']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN – no records will be deleted.\n'))

        # ── Expired sessions (same as built-in clearsessions) ──────────────────
        try:
            from django.contrib.sessions.models import Session
            expired_qs = Session.objects.filter(expire_date__lt=timezone.now())
            expired_count = expired_qs.count()
            if not dry_run:
                expired_qs.delete()
            self.stdout.write(f'  Expired sessions deleted:    {expired_count}')
        except Exception as exc:
            self.stderr.write(f'  Sessions – error: {exc}')
            expired_count = 0

        # ── Old sessions by age ────────────────────────────────────────────────
        age_count = 0
        if extra_days > 0:
            try:
                from django.contrib.sessions.models import Session
                cutoff = timezone.now() - datetime.timedelta(days=extra_days)
                age_qs = Session.objects.filter(expire_date__lt=cutoff)
                age_count = age_qs.count()
                if not dry_run:
                    age_qs.delete()
                self.stdout.write(f'  Sessions older than {extra_days}d deleted: {age_count}')
            except Exception as exc:
                self.stderr.write(f'  Old sessions – error: {exc}')

        # ── Audit log pruning ──────────────────────────────────────────────────
        audit_count = 0
        if prune_audit_days > 0:
            try:
                from audit.models import AuditLog
                cutoff = timezone.now() - datetime.timedelta(days=prune_audit_days)
                audit_qs = AuditLog.objects.filter(timestamp__lt=cutoff)
                audit_count = audit_qs.count()
                if not dry_run:
                    audit_qs.delete()
                self.stdout.write(
                    f'  Audit logs older than {prune_audit_days}d deleted: {audit_count}'
                )
            except Exception as exc:
                self.stderr.write(f'  Audit log – error: {exc}')

        total = expired_count + age_count + audit_count
        suffix = ' (dry run)' if dry_run else ''
        self.stdout.write(
            self.style.SUCCESS(f'\ncleanup_sessions complete{suffix}: {total} record(s) removed.')
        )
