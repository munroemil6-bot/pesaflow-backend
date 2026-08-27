"""
Wallet App Configuration

Owner: Naomi
Responsibility: Wallet management and balance tracking

This app handles:
- Wallet creation
- Balance management
- Wallet analytics
- Transaction history
"""

from django.apps import AppConfig


class WalletConfig(AppConfig):
	default_auto_field = 'django.db.models.BigAutoField'
	name = 'wallet'
	verbose_name = 'Wallets'

