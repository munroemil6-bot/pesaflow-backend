"""
Payments App Configuration

Owner: Myles
Responsibility: M-PESA payment integration and processing

This app handles:
- STK Push initiation
- Payment callbacks
- M-PESA transaction tracking
- Payment status verification
- Daraja API integration
"""

from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'
    verbose_name = 'Payments & M-PESA'
