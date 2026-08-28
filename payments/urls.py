
from django.urls import path
from .views import stk_push

app_name = 'payments'

urlpatterns = [
    path('stk-push/', stk_push, name='stk-push'),
]
