from django.urls import path

from .views import InitOrAuth

urlpatterns = [
    path('', InitOrAuth.as_view(), name='init_or_get_token'),
]