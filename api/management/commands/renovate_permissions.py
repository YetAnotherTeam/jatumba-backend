from django.core.management.base import BaseCommand

from api.permissions import renovate_permissions


class Command(BaseCommand):
    help = 'Обновляет права'

    def handle(self, *args, **options):
        renovate_permissions()
        self.stdout.write(self.style.SUCCESS('Successfully renovated'))
