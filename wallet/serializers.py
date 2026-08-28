from decimal import Decimal
from rest_framework import serializers
from .models import Wallet, WalletTransaction


class WalletSerializer(serializers.ModelSerializer):
    """Full wallet details."""

    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Wallet
        fields = [
            'id',
            'user',
            'balance',
            'currency',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'balance', 'currency', 'created_at', 'updated_at']


class WalletBalanceSerializer(serializers.ModelSerializer):
    """Just balance info - lightweight, for frequent polling."""

    class Meta:
        model = Wallet
        fields = ['balance', 'currency']
        read_only_fields = fields


class WalletTransactionSerializer(serializers.ModelSerializer):
    """Transaction history entries."""

    class Meta:
        model = WalletTransaction
        fields = [
            'id',
            'amount',
            'transaction_type',
            'description',
            'balance_before',
            'balance_after',
            'created_at',
        ]
        read_only_fields = fields


class WalletAnalyticsSerializer(serializers.Serializer):
    """Wallet statistics - aggregated, not tied directly to a model."""

    total_credits = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_debits = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()
    average_transaction = serializers.DecimalField(max_digits=12, decimal_places=2)
    current_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
    last_transaction_at = serializers.DateTimeField(allow_null=True)

    def to_representation(self, instance):
        """
        `instance` is expected to be a dict of aggregated values built in the view,
        e.g. via WalletTransaction.objects.filter(wallet=wallet).aggregate(...)
        """
        return super().to_representation(instance)


class AddFundsSerializer(serializers.Serializer):
    """Input for adding money (also reusable for deducting money)."""

    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    description = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

# TODO: WalletSerializer implementation
# TODO: WalletBalanceSerializer implementation
# TODO: WalletAnalyticsSerializer implementation
# TODO: AddFundsSerializer implementation
