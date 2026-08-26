"""
Payments URLs

Owner: Myles
Responsibility: Route URLs to payment views

URL patterns to implement:
# TODO: path('stk-push/', views.stk_push)
# TODO: path('<checkout_request_id>/', views.check_payment_status)
# TODO: path('callback/', views.payment_callback)
# TODO: path('simulate/', views.simulate_payment)
# TODO: path('access-token/', views.get_access_token)

Notes:
- Payment callback should have AllowAny permission (Safaricom webhook)
- STK push requires IsAuthenticated
"""

from django.urls import path
from .views import stk_push

app_name = 'payments'

urlpatterns = [
    path('stk-push/', stk_push, name='stk-push'),
]
