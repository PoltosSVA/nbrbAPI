from rest_framework import serializers
from .models import CurrencyRate, ExchangeDeal


class CurrencySerializer(serializers.ModelSerializer):
    """Сериализатор для представления данных о валюте.

        Преобразует объект CurrencyRate в JSON-представление для API.
        Включает только основные поля, необходимые для клиента.

    """

    class Meta:
        model = CurrencyRate
        fields = ['currency_code', 'currency_name', 'rate', 'scale']


class ExchangeDealCreateSerializer(serializers.Serializer):
    """Сериализатор для создания новой сделки обмена валюты.

        Args:
            amount (Decimal): Сумма для обмена (должна быть > 0).
            currency_from (str): Код исходной валюты (3 символа).
            currency_to (str): Код целевой валюты (3 символа).
    """
    amount = serializers.DecimalField(max_digits=15, decimal_places=4, min_value=0.0001)
    currency_from = serializers.CharField(max_length=3)
    currency_to = serializers.CharField(max_length=3)

    def validate(self, data):
        """Проверяет корректность данных для обмена валюты.

               Args:
                   data (dict): Входные данные для валидации.

               Returns:
                   dict: Валидированные данные.

               Raises:
                   ValidationError: Если валюта не найдена или происходит конвертация в ту же валюту.
        """
        codes = {data['currency_from'].upper(), data['currency_to'].upper()}
        currencies = CurrencyRate.objects.filter(currency_code__in=codes)

        found_codes = {c.currency_code for c in currencies}
        if missing := codes - found_codes:
            raise serializers.ValidationError(
                f"Валюты не найдены: {', '.join(missing)}"
            )

        data['currency_from_obj'] = currencies.get(currency_code=data['currency_from'].upper())
        data['currency_to_obj'] = currencies.get(currency_code=data['currency_to'].upper())
        if data['currency_from_obj'] == data['currency_to_obj']:
            raise serializers.ValidationError(
                "Конвертация валюты в саму себя не поддерживается."
            )
        return data


class ExchangeDealConfirmSerializer(serializers.Serializer):
    """Сериализатор для подтверждения/отклонения сделки.

        Используется при подтверждении или отклонении сделки через API.

        Fields:
            action (str): Действие с сделкой - 'confirm' (подтвердить) или 'reject' (отклонить)

        Example:
            {
                "action": "confirm"
            }
    """
    action = serializers.ChoiceField(choices=['confirm', 'reject'])


class DealReportSerializer(serializers.Serializer):
    """Сериализатор для данных отчета по сделкам.

        Используется для агрегированных данных о сделках за период.

    """
    currency = serializers.CharField()
    total_sent = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_received = serializers.DecimalField(max_digits=15, decimal_places=2)
    deal_count = serializers.IntegerField()


class PendingDealSerializer(serializers.ModelSerializer):
    """Сериализатор для незавершенных сделок (со статусом 'pending').

        Представляет упрощенное view сделки для списка незавершенных операций.
        Включает только основные поля, необходимые для отображения.
    """

    currency_from = serializers.CharField(source='currency_from.currency_code')
    currency_to = serializers.CharField(source='currency_to.currency_code')

    class Meta:
        model = ExchangeDeal
        fields = [
            'id',
            'amount_from',
            'currency_from',
            'amount_to',
            'currency_to',
            'rate',
            'created_at'
        ]