"""
Transactions App Configuration

Owner: Nasra
Responsibility: Transaction records and money transfer history

This app handles:
- Recording transfers between users
- Transaction history
- Transaction status tracking
- Transaction fees
- Transfer analytics
"""

from django.apps import AppConfig


class TransactionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transactions'
    verbose_name = 'Transactions'
