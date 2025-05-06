from drf_spectacular.utils import extend_schema, extend_schema_view
from .parameters import *
from .examples import *
from .responses import *

# Декоратор для ExchangeAPIView
exchange_decorator = extend_schema(
    tags=[DEAL_TAG],
    summary="Создание новой сделки",
    description="""Создает новую сделку обмена валюты с расчетом суммы по текущему курсу.

    - **amount** — сумма
    - **currency_from** — изначальная валюта
    - **currency_to** — целевая валюта
    """,
    examples=[EXCHANGE_REQUEST_EXAMPLE],

)

# Декоратор для ConfirmExchangeAPIView
confirm_decorator = extend_schema(
    tags=[DEAL_TAG],
    summary="Подтверждение сделки",
    parameters=[DEAL_ID_PARAM],
    examples=[CONFIRM_EXAMPLE, REJECT_EXAMPLE],
    description="Подтверждает или отклоняет(confirm/reject) сделки находящиеся в статусе PENDING"

)

# Декоратор для DealReportView
report_decorator = extend_schema(
    tags=[REPORT_TAG],
    parameters=[DATE_FROM_PARAM, DATE_TO_PARAM, CURRENCY_PARAM],
    summary="Предоставляет информацию о сделках за интервал времени",
    description="""
        - **currency** — тип валюты (опционально)
        - **deal_count** — количество сделок, в которых была задействона валюта. Пример: USD->EUR, EUR->USD --- deal_count == 2 для EUR и USD
        """,
)

pending_deals_decorator = extend_schema(
    tags=[DEAL_TAG],
    summary="Список незавершенных сделок",
    description="Возвращает список всех сделок со статусом PENDING.",
)