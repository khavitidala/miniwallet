from __future__ import annotations
import typing
from dataclasses import dataclass, asdict
from typing import Any
from django.http import HttpRequest
from django.http.response import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


SUCCESS = 'success'
FAIL = 'fail'


@dataclass(frozen=True)
class ResponseData:
    status: str
    data: dict


class APIException(Exception):
    def __init__(self, message: typing.Union[dict, str], status_code: str='400') -> None:
        self.message = message
        self.status_code = status_code


class BaseView(View):
    def check_permission(self, request, *args, **kwargs):
        pass

    @method_decorator(csrf_exempt)
    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        try:
            if request.method.lower() in self.http_method_names:
                handler = getattr(
                    self, request.method.lower(), self.http_method_not_allowed
                )
            else:
                handler = self.http_method_not_allowed

            self.check_permission(request, *args, **kwargs)

            resp: typing.Tuple[ResponseData, str] = handler(request, *args, **kwargs)
            if not isinstance(resp, tuple):
                raise Exception
            if len(resp) != 2:
                raise Exception
        
        except APIException as e:
            return JsonResponse(data=asdict(ResponseData(
                status=FAIL,
                data={
                    'error': e.message
                }
            )), status=e.status_code)
        
        except Exception:
            return JsonResponse(data=asdict(ResponseData(
                status=FAIL,
                data={
                    'error': 'Internal Server Error'
                }
            )), status='500')
        
        return JsonResponse(asdict(resp[0]), status=resp[1] or '200')