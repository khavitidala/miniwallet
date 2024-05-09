from dataclasses import dataclass
from django.conf import settings

import jwt

from app.models import Account
from config.base import APIException


@dataclass
class AccountApps:
    customer_xid: str=None
    token: str=''

    @property
    def cust_obj(self):
        return Account.objects.filter(customer_xid=self.customer_xid).first()
    
    @property
    def is_create(self):
        return self.cust_obj is None
    
    @property
    def is_auth(self):
        return self.cust_obj is not None
    
    def create(self):
        Account.objects.create(customer_xid=self.customer_xid)
    
    def get_token(self):
        payload = {
            'customer_xid': self.customer_xid
        }
        return 'Token ' + jwt.encode(payload=payload, key=settings.SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def decode_token(token: str):
        return jwt.decode(token.split('Token ')[-1], key=settings.SECRET_KEY, verify=True, algorithms='HS256')
    
    @staticmethod
    def is_valid(data: dict):
        if not data.get('customer_xid'):
            raise APIException(
                message={
                    'customer_xid': [
                        'Missing data for required field.'
                    ]}
                )
        return True

    def get_or_create(self):
        if self.is_create:
            self.create()
        return self.get_token()