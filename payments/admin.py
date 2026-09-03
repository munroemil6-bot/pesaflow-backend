
from django.contrib import admin
from .models import MpesaPayment


@admin.register(MpesaPayment)
class MpesaPaymentAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'amount', 'status', 'checkout_request_id', 'created_at')
	list_filter = ('status', 'created_at')
	search_fields = ('user__email', 'phone_number', 'checkout_request_id', 'mpesa_receipt_number')
