"""Serializers for transaction input and API representations."""

from decimal import Decimal

from rest_framework import serializers

from accounts.models import User
from .models import Transaction


class TransactionListSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True)
    recipient_name = serializers.CharField(source="recipient.full_name", read_only=True)

    class Meta:
        model = Transaction
        fields = ("id", "reference", "sender", "sender_name", "recipient", "recipient_name", "amount", "status", "created_at")


class TransactionSerializer(TransactionListSerializer):
    class Meta(TransactionListSerializer.Meta):
        fields = TransactionListSerializer.Meta.fields + ("fee", "total_amount", "description", "updated_at")


class TransferSerializer(serializers.Serializer):
    recipient_id = serializers.IntegerField(required=False)
    recipient_phone = serializers.CharField(max_length=20, required=False)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("10.00"))
    description = serializers.CharField(required=False, allow_blank=True, max_length=500, default="")

    def validate(self, attrs):
        if bool(attrs.get("recipient_id")) == bool(attrs.get("recipient_phone")):
            raise serializers.ValidationError("Provide exactly one of recipient_id or recipient_phone.")
        try:
            recipient = User.objects.get(pk=attrs["recipient_id"]) if attrs.get("recipient_id") else User.objects.get(phone=attrs["recipient_phone"].strip())
        except User.DoesNotExist:
            raise serializers.ValidationError({"recipient": "Recipient not found."})
        if recipient == self.context["request"].user:
            raise serializers.ValidationError({"recipient": "You cannot transfer money to yourself."})
        attrs["recipient"] = recipient
        return attrs


CreateTransactionSerializer = TransferSerializer


class TransactionSummarySerializer(serializers.Serializer):
    total_sent = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_received = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    transaction_count = serializers.IntegerField(read_only=True)
    average_transaction = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
