from django.urls import path

from .views import WalletView, DepositView, WithdrawView, TransactionView


urlpatterns = [
    path('wallet/transactions', TransactionView.as_view(), name='transactions'),
    path('wallet/deposits', DepositView.as_view(), name='deposits'),
    path('wallet/withdrawals', WithdrawView.as_view(), name='withdrawals'),
    path('wallet', WalletView.as_view(), name='wallet'),
]