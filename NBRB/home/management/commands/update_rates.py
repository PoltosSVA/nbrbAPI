from django.core.management.base import BaseCommand
from home.services import fetch_currency_rates


class Command(BaseCommand):
    help = 'Update currency rates from NBRB API'

    def handle(self, *args, **options):
        if fetch_currency_rates():
            self.stdout.write("Currency rates updated")
        else:
            self.stdout.write("Currency rates were up-to-date")