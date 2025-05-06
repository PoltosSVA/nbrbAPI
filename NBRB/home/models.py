from django.db import models
from django.utils import timezone
import uuid


class CurrencyRate(models.Model):
    """Модель для хранения курсов валют от НБ РБ.

        Attributes:
            currency_code (str): Код валюты (3 символа, например: USD, EUR).
            currency_name (str): Название валюты.
            rate (Decimal): Текущий курс валюты.
            scale (int): Масштаб курса .
            last_updated (DateTime): Дата последнего обновления курса.
    """
    currency_code = models.CharField(max_length=3, unique=True)
    currency_name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=15, decimal_places=4)
    scale = models.IntegerField(default=1)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.currency_code} ({self.currency_name}): {self.rate}"


class ExchangeDeal(models.Model):
    """Модель сделки по обмену валюты.

    Attributes:
        id (UUID): Уникальный идентификатор сделки.
        amount_from (Decimal): Сумма в исходной валюте.
        amount_to (Decimal): Сумма в целевой валюте.
        currency_from (ForeignKey): Исходная валюта.
        currency_to (ForeignKey): Целевая валюта.
        rate (Decimal): Курс обмена.
        created_at (DateTime): Дата создания сделки.
        status (str): Статус сделки (pending/completed/rejected).
        completed_at (DateTime): Дата завершения сделки.
    """

    PENDING = 'pending'
    COMPLETED = 'completed'
    REJECTED = 'rejected'

    STATUS_CHOICES = (
        (PENDING, 'Ожидает подтверждения'),
        (COMPLETED, 'Завершена'),
        (REJECTED, 'Отклонена'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount_from = models.DecimalField(max_digits=15, decimal_places=4)
    amount_to = models.DecimalField(max_digits=15, decimal_places=4)
    currency_from = models.ForeignKey(CurrencyRate, on_delete=models.PROTECT, related_name='deal_from')
    currency_to = models.ForeignKey(CurrencyRate, on_delete=models.PROTECT, related_name='deal_to')
    rate = models.DecimalField(max_digits=15, decimal_places=4)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Сделка {self.id}: {self.amount_from} {self.currency_from} - {self.amount_to} {self.currency_to}"
