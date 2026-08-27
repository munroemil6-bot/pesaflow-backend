"""
Transactions Admin

Owner: Nasra
Responsibility: Django admin interface for transaction management

Admin configuration to implement:
# TODO: TransactionAdmin
#   - List display: id, sender, recipient, amount, status, created_at
#   - Search: reference, sender__email, recipient__email
#   - Filter: status, created_at
#   - Read-only: created_at, updated_at, reference
#   - List filter: status, date created
"""

from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'reference', 'sender', 'recipient', 'amount', 'fee', 'status', 'created_at')
    search_fields = ('reference', 'sender__email', 'recipient__email')
    list_filter = ('status', 'created_at')
    readonly_fields = ('reference', 'created_at', 'updated_at', 'total_amount')
    list_select_related = ('sender', 'recipient')
