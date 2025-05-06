from drf_spectacular.utils import OpenApiExample

# Примеры для ExchangeAPIView
EXCHANGE_REQUEST_EXAMPLE = OpenApiExample(
    'Пример запроса',
    value={"amount": 100, "currency_from": "USD", "currency_to": "EUR"},
    request_only=True
)

EXCHANGE_RESPONSE_EXAMPLE = OpenApiExample(
    'Пример ответа',
    value={
        "deal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "amount_to": 85.5,
        "rate": 0.855,
        "expires_at": "2023-05-20T12:30:45Z"
    },
    response_only=True
)

# Примеры для ConfirmExchangeAPIView
CONFIRM_EXAMPLE = OpenApiExample(
    'Подтверждение сделки',
    value={"action": "confirm"},
    request_only=True
)

REJECT_EXAMPLE = OpenApiExample(
    'Отклонение сделки',
    value={"action": "reject"},
    request_only=True
)

PENDING_DEALS_EXAMPLE = OpenApiExample(
    'Пример ответа',
    value=[
        {
            "id": "a1b2c3d4-e5f6-7890-g1h2-i3j4k5l6m7n8",
            "amount_from": 100.0,
            "currency_from": "USD",
            "amount_to": 85.0,
            "currency_to": "EUR",
            "rate": 0.85,
            "created_at": "2023-05-15T10:30:45Z"
        }
    ],
    response_only=True
)

EMPTY_PENDING_DEALS_EXAMPLE = OpenApiExample(
    'Пустой ответ',
    value={"message": "Незавершённых сделок не найдено."},
    response_only=True,
    status_codes=['200']
)