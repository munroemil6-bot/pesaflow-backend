
from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'reference', 'sender', 'recipient', 'amount', 'fee', 'status', 'created_at')
    search_fields = ('reference', 'sender__email', 'recipient__email')
    list_filter = ('status', 'created_at')
    readonly_fields = ('reference', 'created_at', 'updated_at', 'total_amount')
    list_select_related = ('sender', 'recipient')
