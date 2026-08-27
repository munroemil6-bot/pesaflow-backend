"""
Wallet Admin

Owner: Naomi
Responsibility: Django admin interface for wallet management

Admin configuration to implement:
# TODO: WalletAdmin
#   - List display: user, balance, currency, created_at
#   - Search: user__email, user__phone
#   - Filter: currency, created_at
#   - Read-only: created_at, updated_at

# TODO: WalletTransactionAdmin (if implemented)
#   - List display: wallet, amount, type, created_at
#   - Filter: type, created_at
#   - Search: wallet__user__email
"""
from django.contrib import admin
from .models import Wallet, WalletTransaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'currency', 'created_at')
    search_fields = ('user__email', 'user__phone')
    list_filter = ('currency', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'amount', 'transaction_type', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('wallet__user__email',)

# TODO: Register Wallet model with WalletAdmin
