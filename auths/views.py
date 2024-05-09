from __future__ import annotations
from django.db import transaction
from django.http import HttpRequest
from config.base import SUCCESS, APIException, BaseView, ResponseData
from .auth import AccountApps


class AuthView(BaseView):
    def check_permission(self, request: HttpRequest, *args, **kwargs):
        super().check_permission(request, *args, **kwargs)
        if not request.headers.__contains__('Authorization'):
            raise APIException(message='Unauthorized access', status_code='401')
        
        token = request.headers['Authorization']
        try:
            decoded_token = AccountApps.decode_token(token)
            request.account = AccountApps(customer_xid=decoded_token['customer_xid'], token=token)
            if not request.account.is_auth:
                raise Exception
            self.request = request
        except Exception:
            raise APIException(message='Unauthorized access', status_code='401')


class InitOrAuth(BaseView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        AccountApps.is_valid(request.POST)
        return ResponseData(
            status=SUCCESS,
            data={
                'token': AccountApps(
                    customer_xid=request.POST.get('customer_xid')
                ).get_or_create()
            }
        ), '201'
