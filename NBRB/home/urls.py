from django.urls import path
from .views import ExchangeAPIView, ConfirmExchangeAPIView, DealReportView, PendingDealsView

urlpatterns = [
    path('exchange/', ExchangeAPIView.as_view(), name='exchange-calculate'),
    path('exchange/<uuid:deal_id>/confirm/', ConfirmExchangeAPIView.as_view(), name='exchange-confirm'),
    path('reports/deals/', DealReportView.as_view()),
    path('pending-deals/', PendingDealsView.as_view(), name='pending-deals'),

]
