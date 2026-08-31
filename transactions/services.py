"""Business rules for PesaFlow user-to-user transfers."""

from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction as db_transaction
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404

from wallet.models import Wallet, WalletTransaction
from wallet.services import get_or_create_wallet

from .models import Transaction

User = get_user_model()

FEE_RATE = Decimal("0.01")
MONEY_PLACES = Decimal("0.01")


def calculate_transaction_fee(amount):
    """Return the 1% transfer fee, rounded to the smallest currency unit."""
    amount = Decimal(amount)
    if amount <= 0:
        raise ValidationError("Amount must be greater than zero.")
    return (amount * FEE_RATE).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)


@db_transaction.atomic
def create_transaction(sender, recipient, amount, description=""):
    """Transfer money atomically, including the fee, and create ledger entries. Fee goes to admin (Myles)."""
    amount = Decimal(amount).quantize(MONEY_PLACES, rounding=ROUND_HALF_UP)
    if amount <= 0:
        raise ValidationError("Amount must be greater than zero.")
    if sender.pk == recipient.pk:
        raise ValidationError("You cannot transfer money to yourself.")
    if not recipient.is_active:
        raise ValidationError("The recipient account is inactive.")

    sender_wallet = get_or_create_wallet(sender)
    recipient_wallet = get_or_create_wallet(recipient)
    
    # Get admin wallet (Myles)
    try:
        admin_user = User.objects.get(phone="0723274962")
        admin_wallet = get_or_create_wallet(admin_user)
    except User.DoesNotExist:
        admin_user = None
        admin_wallet = None
    
    # Lock wallets for atomic update
    wallet_pks = [sender_wallet.pk, recipient_wallet.pk]
    if admin_wallet:
        wallet_pks.append(admin_wallet.pk)
    
    locked_wallets = {
        wallet.user_id: wallet
        for wallet in Wallet.objects.select_for_update().filter(pk__in=wallet_pks)
    }
    sender_wallet = locked_wallets[sender.pk]
    recipient_wallet = locked_wallets[recipient.pk]
    if admin_wallet:
        admin_wallet = locked_wallets.get(admin_user.pk)
    
    fee = calculate_transaction_fee(amount)
    total_amount = amount + fee
    if sender_wallet.balance < total_amount:
        raise ValidationError("Insufficient wallet balance for this transfer and its fee.")

    transfer = Transaction.objects.create(
        sender=sender, recipient=recipient, amount=amount, fee=fee,
        total_amount=total_amount, description=description,
    )
    sender_before, recipient_before = sender_wallet.balance, recipient_wallet.balance
    admin_before = admin_wallet.balance if admin_wallet else None
    
    sender_wallet.balance -= total_amount
    recipient_wallet.balance += amount
    if admin_wallet:
        admin_wallet.balance += fee
    
    sender_wallet.save(update_fields=["balance", "updated_at"])
    recipient_wallet.save(update_fields=["balance", "updated_at"])
    if admin_wallet:
        admin_wallet.save(update_fields=["balance", "updated_at"])
    
    # Create ledger entries
    ledger_entries = [
        WalletTransaction(wallet=sender_wallet, amount=total_amount, transaction_type=WalletTransaction.DEBIT,
                          description=f"Transfer {transfer.reference}", balance_before=sender_before,
                          balance_after=sender_wallet.balance),
        WalletTransaction(wallet=recipient_wallet, amount=amount, transaction_type=WalletTransaction.CREDIT,
                          description=f"Transfer {transfer.reference}", balance_before=recipient_before,
                          balance_after=recipient_wallet.balance),
    ]
    
    # Add admin fee ledger entry if admin wallet exists
    if admin_wallet:
        ledger_entries.append(
            WalletTransaction(wallet=admin_wallet, amount=fee, transaction_type=WalletTransaction.CREDIT,
                              description=f"Transfer fee {transfer.reference}", balance_before=admin_before,
                              balance_after=admin_wallet.balance)
        )
    
    WalletTransaction.objects.bulk_create(ledger_entries)
    transfer.status = Transaction.Status.COMPLETED
    transfer.save(update_fields=["status", "updated_at"])
    return transfer


def get_user_transactions(user, filters=None):
    """Return a user's transfers, optionally narrowed by date, status, or direction."""
    filters = filters or {}
    queryset = Transaction.objects.filter(Q(sender=user) | Q(recipient=user)).select_related("sender", "recipient")
    if filters.get("direction") == "sent":
        queryset = queryset.filter(sender=user)
    elif filters.get("direction") == "received":
        queryset = queryset.filter(recipient=user)
    if filters.get("status"):
        queryset = queryset.filter(status=filters["status"])
    if filters.get("start_date"):
        queryset = queryset.filter(created_at__date__gte=filters["start_date"])
    if filters.get("end_date"):
        queryset = queryset.filter(created_at__date__lte=filters["end_date"])
    return queryset.order_by("-created_at")


def get_transaction(user, transaction_id):
    """Return a transfer only when the user sent or received it."""
    transfer = get_object_or_404(Transaction.objects.select_related("sender", "recipient"), pk=transaction_id)
    if transfer.sender_id != user.pk and transfer.recipient_id != user.pk:
        raise PermissionDenied("You do not have permission to view this transaction.")
    return transfer


def get_transaction_summary(user):
    """Return completed sent/received totals and overall transaction statistics."""
    queryset = get_user_transactions(user)
    aggregates = queryset.aggregate(
        total_sent=Sum("amount", filter=Q(sender=user, status=Transaction.Status.COMPLETED)),
        total_received=Sum("amount", filter=Q(recipient=user, status=Transaction.Status.COMPLETED)),
        transaction_count=Count("id"),
        average_transaction=Avg("amount", filter=Q(status=Transaction.Status.COMPLETED)),
    )
    return {
        key: value if value is not None else (0 if key == "transaction_count" else Decimal("0.00"))
        for key, value in aggregates.items()
    }


@db_transaction.atomic
def refund_transaction(transfer):
    """Reverse a failed transfer once, returning the amount and fee to its sender."""
    if transfer.status != Transaction.Status.FAILED:
        raise ValidationError("Only failed transactions can be refunded.")
    
    # Get admin wallet (Myles)
    try:
        admin_user = User.objects.get(phone="0723274962")
        admin_wallet = Wallet.objects.select_for_update().get(user=admin_user)
    except User.DoesNotExist:
        admin_user = None
        admin_wallet = None
    
    sender_wallet = Wallet.objects.select_for_update().get(user=transfer.sender)
    recipient_wallet = Wallet.objects.select_for_update().get(user=transfer.recipient)
    
    if recipient_wallet.balance < transfer.amount:
        raise ValidationError("The recipient wallet cannot cover this refund.")
    if admin_wallet and admin_wallet.balance < transfer.fee:
        raise ValidationError("The admin wallet cannot cover the fee refund.")
    
    sender_before, recipient_before = sender_wallet.balance, recipient_wallet.balance
    admin_before = admin_wallet.balance if admin_wallet else None
    
    sender_wallet.balance += transfer.total_amount
    recipient_wallet.balance -= transfer.amount
    if admin_wallet:
        admin_wallet.balance -= transfer.fee
    
    sender_wallet.save(update_fields=["balance", "updated_at"])
    recipient_wallet.save(update_fields=["balance", "updated_at"])
    if admin_wallet:
        admin_wallet.save(update_fields=["balance", "updated_at"])
    
    # Create ledger entries
    ledger_entries = [
        WalletTransaction(wallet=sender_wallet, amount=transfer.total_amount, transaction_type=WalletTransaction.CREDIT,
                          description=f"Refund {transfer.reference}", balance_before=sender_before, balance_after=sender_wallet.balance),
        WalletTransaction(wallet=recipient_wallet, amount=transfer.amount, transaction_type=WalletTransaction.DEBIT,
                          description=f"Refund {transfer.reference}", balance_before=recipient_before, balance_after=recipient_wallet.balance),
    ]
    
    # Add admin fee refund ledger entry if admin wallet exists
    if admin_wallet:
        ledger_entries.append(
            WalletTransaction(wallet=admin_wallet, amount=transfer.fee, transaction_type=WalletTransaction.DEBIT,
                              description=f"Refund fee {transfer.reference}", balance_before=admin_before,
                              balance_after=admin_wallet.balance)
        )
    
    WalletTransaction.objects.bulk_create(ledger_entries)
    transfer.status = Transaction.Status.REFUNDED
    transfer.save(update_fields=["status", "updated_at"])
    return transfer
