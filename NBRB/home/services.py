import requests
from django.utils import timezone
from .models import CurrencyRate
from datetime import timedelta


def fetch_currency_rates():
    """Обновляет курсы валют с API НБ РБ.

        Загружает текущие курсы валют и сохраняет их в базу данных.
        Можно запустить через python manage.py update_rates.
        Запускается при старте приложения, а именно при
        python manage.py runserver

        Returns:
            bool: True если курсы были обновлены, False если обновление не требовалось.

        Raises:
            Exception: При ошибках запроса к API НБ РБ.
    """

    last_update = CurrencyRate.objects.order_by('-last_updated').first()

    if last_update and (timezone.now() - last_update.last_updated) < timedelta(days=1):
        return False

    try:
        response = requests.get('https://api.nbrb.by/exrates/rates?periodicity=0')
        response.raise_for_status()
        rates_data = response.json()

        for rate_data in rates_data:
            CurrencyRate.objects.update_or_create(
                currency_code=rate_data['Cur_Abbreviation'],
                defaults={
                    'currency_name': rate_data['Cur_Name'],
                    'rate': rate_data['Cur_OfficialRate'],
                    'scale': rate_data['Cur_Scale'],
                    'last_updated': timezone.now()
                }
            )
        return True

    except Exception as e:
        print(f"Ошибка при загрузке курсов валют: {e}")
        return False
