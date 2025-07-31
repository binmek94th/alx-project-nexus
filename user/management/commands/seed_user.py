import random
from django.core.management import BaseCommand

from user.models import PrivacyChoice, User


class Command(BaseCommand):
    """
    Command to seed the database with users.
    This command creates a specified number of superusers with random usernames,
    emails, full names, and privacy choices.
    If no count is specified, it defaults to creating 100 users.
    Usage:
        python manage.py seed_user --count 50
    or
        python manage.py seed_user
    """
    help = 'Seed the database with a superuser'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=0,
                            help='An optional argument for amount of users to create')

    def handle(self, *args, **kwargs):
        count = kwargs['count'] or 100

        self.stdout.write('Seeding user')

        for i in range(count):
            username = f'user_{i}'
            email = f'user{username}@gmail.com'
            full_name = f'user {username}'
            password = 'password1234'
            email_verified = True
            privacy_choice = random.choice([PrivacyChoice.PUBLIC, PrivacyChoice.PRIVATE])

            User.objects.create_superuser(
                username=username,
                email=email,
                full_name=full_name,
                password=password,
                email_verified=email_verified,
                privacy_choice=privacy_choice
            )

        self.stdout.write(self.style.SUCCESS('Users created'))

