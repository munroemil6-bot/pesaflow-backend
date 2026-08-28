
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

	def validate_amount(self, value):
		if value <= 0:
			raise serializers.ValidationError('Amount must be greater than zero.')
		return value

# TODO: MpesaTransactionSerializer implementation
# TODO: PaymentStatusSerializer implementation
# TODO: CallbackSerializer for webhook validation
