from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from auth_system.views import send_welcome_email

class Command(BaseCommand):
    help = 'Send welcome email to a specific user'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address of the user')

    def handle(self, *args, **options):
        email = options['email']
        try:
            user = User.objects.get(email=email)
            account_type = 'staff_request' if user.is_staff else 'customer'
            send_welcome_email(user, account_type)
            self.stdout.write(
                self.style.SUCCESS(f'Welcome email sent successfully to {email}')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with email {email} not found')
            )