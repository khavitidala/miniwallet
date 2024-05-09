from io import BytesIO
from django.db import transaction
from django.http import HttpRequest
from app.applications.transaction import TransactionApps
from app.applications.wallet import WalletApps
from auths.views import AuthView
from config.base import SUCCESS, ResponseData


class WalletView(AuthView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        wallet = WalletApps(account_obj=self.request.account.cust_obj)
        wallet.enable()
        return ResponseData(
            status=SUCCESS,
            data={
                'wallet': wallet.get_wallet_dict()
            }
        ), '201'
    
    def get(self, request: HttpRequest, *args, **kwargs):
        wallet = WalletApps(account_obj=self.request.account.cust_obj)
        wallet.enabled_check_with_exception()
        return ResponseData(
            status=SUCCESS,
            data={
                'wallet': wallet.get_wallet_dict()
            }
        ), '200'
    
    def load_data_from_patch_and_formdata(self, request: HttpRequest):
        if hasattr(self, "_body"):
            data = BytesIO(request._body)
        else:
            data = request
        return request.parse_file_upload(request.META, data)[0]
    
    @transaction.atomic
    def patch(self, request: HttpRequest, *args, **kwargs):
        wallet = WalletApps(account_obj=self.request.account.cust_obj)
        wallet.do_disable_with_exception(self.load_data_from_patch_and_formdata(request))
        return ResponseData(
            status=SUCCESS,
            data={
                'wallet': wallet.get_wallet_dict()
            }
        ), '200'


class WalletPermissionView(AuthView):
    def check_permission(self, request: HttpRequest, *args, **kwargs):
        super().check_permission(request, *args, **kwargs)
        
        self.wallet = WalletApps(account_obj=self.request.account.cust_obj)
        self.wallet.enabled_check_with_exception()


class TransactionView(WalletPermissionView):
    def get(self, request: HttpRequest, *args, **kwargs):
        return ResponseData(
            status=SUCCESS,
            data={
                'transactions': TransactionApps(wallet_obj=self.wallet.wallet_obj).get_all_transactions_dict()
            }
        ), '200'


class DepositView(WalletPermissionView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        TransactionApps.is_valid(request.POST)
        return ResponseData(
            status=SUCCESS,
            data={
                'deposit': TransactionApps(wallet_obj=self.wallet.wallet_obj, data=request.POST).deposit()
            }
        ), '201'


class WithdrawView(WalletPermissionView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        TransactionApps.is_valid(request.POST)
        return ResponseData(
            status=SUCCESS,
            data={
                'withdrawal': TransactionApps(wallet_obj=self.wallet.wallet_obj, data=request.POST).withdraw()
            }
        ), '201'