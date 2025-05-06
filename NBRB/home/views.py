from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from .models import ExchangeDeal, CurrencyRate
from django.db.models import Sum, Count, Q, F
from drf_spectacular.utils import extend_schema_view
from .serializers import (
    ExchangeDealCreateSerializer,
    ExchangeDealConfirmSerializer,
    DealReportSerializer,
    PendingDealSerializer
)
import uuid
from django.utils import timezone
from .docs.decorators import (
    exchange_decorator,
    confirm_decorator,
    report_decorator,
    pending_deals_decorator
)
from django.shortcuts import redirect


def redirect_to_docs(request):
    return redirect('/api/docs')


@extend_schema_view(post=exchange_decorator)
class ExchangeAPIView(GenericAPIView):
    """API для создания новой сделки обмена валюты.

        Позволяет получить информацию о возможном обмене валюты без фактического совершения сделки.
        Создает сделку со статусом 'pending', которая требует подтверждения.
    """

    serializer_class = ExchangeDealCreateSerializer

    def post(self, request):
        """Создает новую сделку обмена валюты.

            Args:
                request (Request): Объект запроса Django REST Framework.

            Returns:
                Response: JSON с параметрами сделки:
                    - deal_id: UUID сделки
                    - amount_to: Рассчитанная сумма в целевой валюте
                    - rate: Курс обмена
                    - expires_at: Время истечения срока действия сделки

            Пример запроса:
                POST /api/exchange/
                {
                    "amount": 100,
                    "currency_from": "USD",
                    "currency_to": "EUR"
                }
        """

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            currency_from = data['currency_from_obj']
            currency_to = data['currency_to_obj']
            amount = data['amount']

            rate = (currency_from.rate / currency_from.scale) / (currency_to.rate / currency_to.scale)

            amount_to = round(amount * rate, 4)

            deal = ExchangeDeal(
                id=uuid.uuid4(),
                amount_from=amount,
                currency_from=currency_from,
                amount_to=amount_to,
                currency_to=currency_to,
                rate=rate,
                status=ExchangeDeal.PENDING
            )
            deal.save()
            return Response({
                'deal_id': deal.id,
                'amount_to': round(amount_to, 4),
                'rate': round(rate, 2),
                'expires_at': (timezone.now() + timezone.timedelta(minutes=30)).isoformat()
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(post=confirm_decorator)
class ConfirmExchangeAPIView(GenericAPIView):
    """API для подтверждения или отклонения сделки обмена валюты.

        Позволяет подтвердить или отклонить ранее созданную сделку.
        Сделка должна быть в статусе 'pending' и не просрочена (не старше 30 минут).
    """
    serializer_class = ExchangeDealConfirmSerializer

    def post(self, request, deal_id):

        """Подтверждает или отклоняет сделку обмена валюты.

            Args:
                request (Request): Объект запроса Django REST Framework.
                deal_id (UUID): Идентификатор сделки.

            Returns:
                Response: JSON с результатом операции:
                    - status: 'completed' или 'rejected'
                    - deal_id: UUID сделки

            Raises:
                NotFound: Если сделка не найдена или уже обработана.
                BadRequest: Если время для подтверждения истекло.

            Пример запроса:
                POST /api/confirm/{deal_id}/
                {
                    "action": "confirm"
                }
        """

        try:
            deal = ExchangeDeal.objects.get(id=deal_id, status=ExchangeDeal.PENDING)
        except ExchangeDeal.DoesNotExist:
            return Response(
                {'error': 'Сделка не найдена или уже обработана'},
                status=status.HTTP_404_NOT_FOUND
            )

        if deal.created_at < timezone.now() - timezone.timedelta(minutes=30):
            deal.status = ExchangeDeal.REJECTED
            deal.save()
            return Response(
                {'error': 'Время для подтверждения истекло'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            action = serializer.validated_data['action']
            if action == 'confirm':
                deal.status = ExchangeDeal.COMPLETED
                deal.completed_at = timezone.now()
                deal.save()
                return Response({'status': 'completed', 'deal_id': str(deal.id)})
            elif action == 'reject':
                deal.status = ExchangeDeal.REJECTED
                deal.completed_at = timezone.now()
                deal.save()
                return Response({'status': 'rejected', 'deal_id': str(deal.id)})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(get=report_decorator)
class DealReportView(GenericAPIView):
    """API для получения отчетов по завершенным сделкам.

        Позволяет получить агрегированные данные по сделкам за указанный период.
        Поддерживает фильтрацию по валюте.
    """
    serializer_class = DealReportSerializer

    def get(self, request):

        """Возвращает отчет по сделкам за период.

            Args:
                request (Request): Объект запроса Django REST Framework.

            Query Params:
                date_from (str): Начальная дата периода (YYYY-MM-DD).
                date_to (str): Конечная дата периода (YYYY-MM-DD).
                currency (str, optional): Код валюты для фильтрации.

            Returns:
                Response: JSON с агрегированными данными:
                    - currency: Код валюты
                    - total_sent: Сумма отправленных средств
                    - total_received: Сумма полученных средств
                    - deal_count: Количество сделок

            Raises:
                BadRequest: При неверных параметрах запроса.

            Пример запроса:
                GET /api/report/?date_from=2023-01-01&date_to=2023-12-31&currency=USD
        """

        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        currency_code = request.query_params.get('currency')

        if not date_from or not date_to:
            return Response(
                {"error": "Параметры date_from и date_to обязательны"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {"error": "Неверный формат даты. Используйте YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if date_from > date_to:
            return Response(
                {"error": "Дата начала не может быть позже даты окончания"},
                status=status.HTTP_400_BAD_REQUEST
            )

        deals = ExchangeDeal.objects.filter(
            status=ExchangeDeal.COMPLETED,
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )

        if currency_code:
            currency_code = currency_code.upper()
            if not CurrencyRate.objects.filter(currency_code=currency_code).exists():
                return Response(
                    {"error": f"Валюта {currency_code} не найдена"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                deals = deals.filter(
                    Q(currency_from__currency_code=currency_code) |
                    Q(currency_to__currency_code=currency_code)
                )

        deals_data = deals.values(
            'currency_from__currency_code',
            'currency_to__currency_code'
        ).annotate(
            total_sent=Sum('amount_from'),
            total_received=Sum('amount_to'),
            deal_count=Count('id')
        )

        result = {}
        for deal in deals_data:
            from_currency = deal['currency_from__currency_code']
            if from_currency not in result:
                result[from_currency] = {
                    'currency': from_currency,
                    'total_sent': 0,
                    'total_received': 0,
                    'deal_count': 0
                }
            result[from_currency]['total_sent'] += deal['total_sent'] or 0

            to_currency = deal['currency_to__currency_code']
            if to_currency not in result:
                result[to_currency] = {
                    'currency': to_currency,
                    'total_sent': 0,
                    'total_received': 0,
                    'deal_count': 0
                }
            result[to_currency]['total_received'] += deal['total_received'] or 0

            result[from_currency]['deal_count'] += deal['deal_count']
            result[to_currency]['deal_count'] += deal['deal_count']

        report_data = list(result.values())

        serializer = self.get_serializer(report_data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(get=pending_deals_decorator)
class PendingDealsView(GenericAPIView):
    """API для получения списка незавершенных сделок.

    Возвращает список всех актуальных сделок со статусом 'pending'.
    Автоматически отклоняет сделки, созданные более 30 минут назад.
    """
    serializer_class = PendingDealSerializer

    def get(self, request):
        """Возвращает список актуальных незавершенных сделок.

        Args:
            request (Request): Объект запроса Django REST Framework.

        Returns:
            Response: JSON со списком сделок или сообщением об отсутствии сделок.

        Пример ответа:
            [
                {
                    "id": "a1b2c3d4-...",
                    "amount_from": 100.0,
                    "currency_from": "USD",
                    "amount_to": 85.0,
                    "currency_to": "EUR",
                    "rate": 0.85,
                    "created_at": "2023-05-15T10:30:45Z"
                }
            ]
        """
        now = timezone.now()
        expiry_time = now - timezone.timedelta(minutes=30)

        expired_deals = ExchangeDeal.objects.filter(
            status=ExchangeDeal.PENDING,
            created_at__lt=expiry_time
        )

        if expired_deals.exists():
            expired_deals.update(
                status=ExchangeDeal.REJECTED,
                completed_at=now
            )

        pending_deals = ExchangeDeal.objects.filter(
            status=ExchangeDeal.PENDING,
            created_at__gte=expiry_time
        ).select_related(
            'currency_from', 'currency_to'
        ).order_by('-created_at')

        if not pending_deals.exists():
            return Response(
                {"message": "Незавершённых сделок не найдено."},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(pending_deals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)