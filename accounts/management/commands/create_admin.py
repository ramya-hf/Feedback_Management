from django.core.management.base import BaseCommand
from django.core.management import CommandError
from accounts.models import User


class Command(BaseCommand):
    """
    Management command to create admin users for the feedback management system.
    
    Usage:
    python manage.py create_admin --email admin@example.com --password admin123
    """
    help = 'Create an admin user for the feedback management system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email address for the admin user'
        )
        parser.add_argument(
            '--password',
            type=str,
            required=True,
            help='Password for the admin user'
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the admin user (defaults to email prefix)'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            default='Admin',
            help='First name for the admin user'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            default='User',
            help='Last name for the admin user'
        )

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        username = options.get('username') or email.split('@')[0]
        first_name = options['first_name']
        last_name = options['last_name']

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise CommandError(f'User with email "{email}" already exists.')

        if User.objects.filter(username=username).exists():
            raise CommandError(f'User with username "{username}" already exists.')

        # Create admin user
        try:
            user = User.objects.create_user(
                email=email,
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=User.Role.ADMIN,
                is_staff=True,
                is_superuser=True,
                is_email_verified=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created admin user "{user.email}" with role "{user.role}"'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'User details: {user.get_full_name()} - {user.email}'
                )
            )
            
        except Exception as e:
            raise CommandError(f'Error creating admin user: {str(e)}') 