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

# TODO: MpesaTransactionSerializer implementation
# TODO: PaymentStatusSerializer implementation
# TODO: CallbackSerializer for webhook validation
