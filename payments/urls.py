
from django.urls import path
from .views import callback, stk_push, withdrawal_callback

app_name = 'payments'

urlpatterns = [
    path('stk-push/', stk_push, name='stk-push'),
    path('callback/', callback, name='callback'),
    path('withdrawal-callback/', withdrawal_callback, name='withdrawal-callback'),
]
