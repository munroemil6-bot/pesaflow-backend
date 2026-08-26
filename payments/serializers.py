"""
Payments Serializers

Owner: Myles
Responsibility: Payment input validation and output serialization

Serializers to implement:
# TODO: STKPushSerializer - Input for initiating STK push
# TODO: MpesaTransactionSerializer - M-PESA transaction details
# TODO: PaymentStatusSerializer - Payment status response
# TODO: CallbackSerializer - M-PESA callback validation
"""

from rest_framework import serializers

class MpesaSTKSerializer(serializers.Serializer):
	phone_number = serializers.CharField()
	amount = serializers.DecimalField(
		max_digits=10,
		decimal_places=2
	)

	def validate_phone_number(self, value):
		normalized = value.strip().replace('+', '', 1)
		if normalized.startswith('0') and len(normalized) == 10:
			normalized = f'254{normalized[1:]}'
		if not normalized.isdigit() or len(normalized) != 12 or not normalized.startswith('254'):
			raise serializers.ValidationError(
				'Enter a valid Kenyan phone number.'
			)
		return value

# TODO: MpesaTransactionSerializer implementation
# TODO: PaymentStatusSerializer implementation
# TODO: CallbackSerializer for webhook validation
