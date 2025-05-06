from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

DEAL_TAG = 'Сделки'
REPORT_TAG = 'Отчеты'

CURRENCY_PARAM = OpenApiParameter(
    name='currency',
    type=OpenApiTypes.STR,
    location=OpenApiParameter.QUERY,
    description='Фильтр по коду валюты (USD, EUR и т.д.)',
    required=False
)

DATE_FROM_PARAM = OpenApiParameter(
    name='date_from',
    type=OpenApiTypes.DATE,
    location=OpenApiParameter.QUERY,
    description='Начальная дата периода (YYYY-MM-DD)',
    required=True
)

DATE_TO_PARAM = OpenApiParameter(
    name='date_to',
    type=OpenApiTypes.DATE,
    location=OpenApiParameter.QUERY,
    description='Конечная дата периода (YYYY-MM-DD)',
    required=True
)

DEAL_ID_PARAM = OpenApiParameter(
    name='deal_id',
    type=OpenApiTypes.UUID,
    location=OpenApiParameter.PATH,
    description='UUID сделки'
)

