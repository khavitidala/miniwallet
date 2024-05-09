from __future__ import annotations
from dataclasses import dataclass
from django.utils import timezone

from app.models import Wallet
from auths.models import Account
from config.base import APIException


@dataclass
class WalletApps:
    account_obj: Account
    wallet_obj: Wallet=None
    has_wallet: bool=None
    is_enabled: bool=None

    def __post_init__(self):
        self.wallet_obj = Wallet.objects.filter(owned_by=self.account_obj).first()
        self.has_wallet = self.wallet_obj is not None
        self.is_enabled = self.has_wallet and self.wallet_obj.status == Wallet.EnabledChoices.ENABLED

    def create(self, **kwargs):
        self.wallet_obj = Wallet.objects.create(owned_by=self.account_obj, **kwargs)
    
    def enable(self):
        if not self.has_wallet:
            self.create(
                enabled_at=timezone.now(),
                status=Wallet.EnabledChoices.ENABLED
            )
            self.has_wallet = True
        
        if self.wallet_obj.status == Wallet.EnabledChoices.DISABLED:
            self.wallet_obj.status = Wallet.EnabledChoices.ENABLED
            self.wallet_obj.enabled_at = timezone.now()
            self.wallet_obj.save()

        self.is_enabled = True
    
    def disable(self):
        if not self.has_wallet:
            self.create(
                disabled_at=timezone.now(),
                status=Wallet.EnabledChoices.DISABLED
            )
            self.has_wallet = True
        
        if self.wallet_obj.status == Wallet.EnabledChoices.ENABLED:
            self.wallet_obj.status = Wallet.EnabledChoices.DISABLED
            self.wallet_obj.disabled_at = timezone.now()
            self.wallet_obj.save()

        self.is_enabled = False
    
    def get_wallet_dict(self):
        resp = {
            'id': str(self.wallet_obj.id),
            'owned_by': str(self.wallet_obj.owned_by.customer_xid),
            'status': str(self.wallet_obj.get_status_display()).lower(),
            'balance': self.wallet_obj.balance
        }
        if self.is_enabled:
            resp['enabled_at'] = str(self.wallet_obj.enabled_at)
        else:
            resp['disabled_at'] = str(self.wallet_obj.disabled_at)
        return resp
    
    def enabled_check_with_exception(self):
        if not self.is_enabled:
            raise APIException(
                message='Wallet disabled',
                status_code='404'
            )

    def do_disable_with_exception(self, data: dict):
        if is_disabled := data.get('is_disabled'):
            if is_disabled == 'true' or is_disabled is True:
                self.disable()
                return

        raise APIException(
            message='Invalid input',
            status_code='400'
        )