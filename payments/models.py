
from django.db import models
from django.conf import settings


class MpesaPayment(models.Model):
	class Status(models.TextChoices):
		PENDING = 'pending', 'Pending'
		SUCCESS = 'success', 'Success'
		FAILED = 'failed', 'Failed'

	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name='mpesa_payments',
	)
	phone_number = models.CharField(max_length=20)
	amount = models.DecimalField(max_digits=12, decimal_places=2)
	merchant_request_id = models.CharField(max_length=100, blank=True)
	checkout_request_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
	mpesa_receipt_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
	status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
	result_code = models.CharField(max_length=20, blank=True)
	result_description = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['-created_at']
		indexes = [
			models.Index(fields=['user', 'status', 'created_at']),
		]

	def __str__(self):
		return f'{self.checkout_request_id or "pending"}: {self.amount} {self.status}'

