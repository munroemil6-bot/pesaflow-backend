"""Admin-only serializers for operational and aggregate data."""

from rest_framework import serializers

from accounts.models import User
from transactions.models import Transaction
from wallet.models import Wallet


class AdminUserSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = User
        fields = ("id", "full_name", "email", "phone", "role", "is_active", "created_at", "wallet_balance")


class AdminTransactionSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source="sender.full_name", read_only=True)
    recipient_name = serializers.CharField(source="recipient.full_name", read_only=True)

    class Meta:
        model = Transaction
        fields = ("id", "reference", "sender", "sender_name", "recipient", "recipient_name", "amount", "fee", "total_amount", "status", "description", "created_at")


class AdminWalletSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Wallet
        fields = ("id", "user", "user_name", "user_email", "balance", "currency", "created_at", "updated_at")


class DashboardSummarySerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_transactions = serializers.IntegerField()
    total_transaction_volume = serializers.DecimalField(max_digits=14, decimal_places=2)
    total_fees_collected = serializers.DecimalField(max_digits=14, decimal_places=2)
    active_users_today = serializers.IntegerField()


class AnalyticsSerializer(serializers.Serializer):
    period = serializers.CharField()
    transaction_count = serializers.IntegerField()
    transaction_volume = serializers.DecimalField(max_digits=14, decimal_places=2)
    average_transaction_amount = serializers.DecimalField(max_digits=14, decimal_places=2)
    user_growth = serializers.IntegerField()
    success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    timeline = serializers.ListField()


class RevenueSerializer(serializers.Serializer):
    total_fees_collected = serializers.DecimalField(max_digits=14, decimal_places=2)
    revenue_by_date = serializers.ListField()
