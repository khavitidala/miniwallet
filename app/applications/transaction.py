from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
import typing

from django.core.cache import cache
from django.db import connection
from django.utils import timezone

from app.models import TransactionHistory, Wallet
from config.base import APIException


TRANSACTION_LOCK_KEY = 'transaction_lock_{}'
TRANSACTION_KEY_LOCK_DURATION = 5


@dataclass
class TransactionApps:
    wallet_obj: Wallet
    data: dict=None
    amount: typing.Type['Decimal']=None
    reference_id: str=None

    def __post_init__(self):
        if self.data:
            self.amount = Decimal(self.data.get('amount').replace(',','.'))
            self.reference_id = self.data.get('reference_id')

    @staticmethod
    def is_valid(data: dict):
        err_msg = {}
        for f in ['amount', 'reference_id']:
            if not data.get(f):
                err_msg.update({
                    f: 'Missing data for required field.'
                })
        
        if TransactionHistory.objects.values('id').filter(reference_id=data.get('reference_id')).exists():
            err_msg.update({
                'reference_id': 'Reference id already exists.'
            })
        
        if err_msg:
            raise APIException(
                message=err_msg,
                status_code='400'
            )
        
        return True
    
    @property
    def transaction_cache_key(self):
        return TRANSACTION_LOCK_KEY.format(str(self.wallet_obj.owned_by.customer_xid))
    
    def create_transaction_obj(self, **kwargs):
        return TransactionHistory(
            amount=self.amount,
            reference_id=self.reference_id,
            transacted_by=str(self.wallet_obj.owned_by.customer_xid),
            transacted_at=timezone.now(),
            status=TransactionHistory.StatusChoices.SUCCESS,
            wallet_id=self.wallet_obj,
            **kwargs
        )
    
    def lock_transaction(self, trx_func):
        return cache.add(self.transaction_cache_key, 1, TRANSACTION_KEY_LOCK_DURATION)

    def get_transaction_dict_based_on_type(self, trx_obj: TransactionHistory):
        res = {
            'id': str(trx_obj.id),
            'status': trx_obj.get_status_display(),
            'amount': trx_obj.amount,
            'reference_id': str(trx_obj.reference_id)
        }
        
        if trx_obj.type == TransactionHistory.TypeChoices.DEPOSIT:
            res.update({
                'deposited_by': str(trx_obj.transacted_by),
                'deposited_at': str(trx_obj.transacted_at),
            })
        
        elif trx_obj.type == TransactionHistory.TypeChoices.WITHDRAWAL:
            res.update({
                'withdrawn_by': str(trx_obj.transacted_by),
                'withdrawn_at': str(trx_obj.transacted_at),
            })
        
        return res
    
    def update_balance(self, trx_obj: TransactionHistory):
        q = """
        SELECT SUM(amount*type) as balance FROM app_transactionhistory
        """
        with connection.cursor() as c:
            c.execute(q)
            for blnc in c.fetchall():
                self.wallet_obj.balance = blnc[0]
                self.wallet_obj.save()
            
    def transaction(self, trx_type):
        if not cache.add(self.transaction_cache_key, 1, TRANSACTION_KEY_LOCK_DURATION):
            raise APIException(
                message='Too many requests',
                status_code='429'
            )

        trx_obj = self.create_transaction_obj(type=trx_type)
        trx_obj.save()
        
        self.update_balance(trx_obj)

        cache.delete(self.transaction_cache_key)
        
        return self.get_transaction_dict_based_on_type(trx_obj)
        
    def deposit(self):
        return self.transaction(TransactionHistory.TypeChoices.DEPOSIT)
    
    def withdraw(self):
        return self.transaction(TransactionHistory.TypeChoices.WITHDRAWAL)
    
    def get_all_transactions_dict(self):
        res = []
        for trx_obj in TransactionHistory.objects.filter(wallet_id=self.wallet_obj):
            res.append({
            'id': str(trx_obj.id),
            'status': trx_obj.get_status_display(),
            'amount': trx_obj.amount,
            'reference_id': str(trx_obj.reference_id),
            'transacted_by': str(trx_obj.transacted_by),
            'transacted_at': str(trx_obj.transacted_at),
        })
        return res

