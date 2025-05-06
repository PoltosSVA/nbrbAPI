import sys
from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        from django.db.utils import OperationalError
        if 'gunicorn' in sys.argv or 'runserver' in sys.argv:
            try:
                from .services import fetch_currency_rates
                fetch_currency_rates()
            except OperationalError as e:
                print(f"Произошла ошибка при обновлении курсов валют: {e}")
