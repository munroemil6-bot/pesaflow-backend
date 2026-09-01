from decimal import Decimal
from django.db import transaction
from django.db.models import Sum, Count, Avg, Q
from django.core.exceptions import ValidationError

from .models import Wallet, WalletTransaction


def get_or_create_wallet(user):
    """
    Get user's wallet or create if it doesn't exist.
    Returns wallet object.
    """
    wallet, created = Wallet.objects.get_or_create(user=user)
    return wallet


def get_balance(wallet):
    """
    Return current balance including currency.
    """
    return {
        'balance': wallet.balance,
        'currency': wallet.currency,
    }


def get_wallet_analytics(wallet):
    """
    Calculate total sent, total received, transaction count,
    average transaction. Returns analytics dict.
    """
    qs = WalletTransaction.objects.filter(wallet=wallet)

    aggregates = qs.aggregate(
        total_received=Sum('amount', filter=Q(transaction_type=WalletTransaction.CREDIT)),
        total_sent=Sum('amount', filter=Q(transaction_type=WalletTransaction.DEBIT)),
        transaction_count=Count('id'),
        average_transaction=Avg('amount'),
    )

    last_transaction = qs.order_by('-created_at').first()

    return {
        'total_sent': aggregates['total_sent'] or Decimal('0.00'),
        'total_received': aggregates['total_received'] or Decimal('0.00'),
        'transaction_count': aggregates['transaction_count'] or 0,
        'average_transaction': aggregates['average_transaction'] or Decimal('0.00'),
        'current_balance': wallet.balance,
        'last_transaction_at': last_transaction.created_at if last_transaction else None,
    }


@transaction.atomic
def add_funds(wallet, amount, description=''):
    amount = Decimal(amount)
    if amount < Decimal('10.00'):
        raise ValidationError("Amount must be at least KSh 10.00.")

    wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

    wallet_transaction = WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type=WalletTransaction.CREDIT,
        description=description,
        balance_before=wallet.balance,
        balance_after=wallet.balance,  
        status=WalletTransaction.PENDING,
    )

  
    from payments.services import initiate_mpesa_payment  

    try:
        initiate_mpesa_payment(
            user=wallet.user,
            amount=amount,
            reference=str(wallet_transaction.id),
        )
    except Exception as exc:
        wallet_transaction.status = WalletTransaction.FAILED
        wallet_transaction.save(update_fields=['status'])
        raise ValidationError(f"Failed to initiate M-PESA payment: {exc}")

    return wallet_transaction


@transaction.atomic
def deduct_funds(wallet, amount, reason=''):
    """
    Validate sufficient balance, create wallet transaction,
    update wallet balance. Returns wallet object.
    """
    amount = Decimal(amount)
    if amount < Decimal('10.00'):
        raise ValidationError("Amount must be at least KSh 10.00.")

    wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

    if wallet.balance < amount:
        raise ValidationError("Insufficient balance.")

    balance_before = wallet.balance
    wallet.balance -= Decimal(amount)
    wallet.save(update_fields=['balance', 'updated_at'])

    WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type=WalletTransaction.DEBIT,
        description=reason,
        balance_before=balance_before,
        balance_after=wallet.balance,
        status=WalletTransaction.SUCCESS,
    )

    return wallet


@transaction.atomic
def add_funds_from_payment(wallet, amount, wallet_transaction=None):
    """
    Called after successful M-PESA payment.
    Update wallet balance, update wallet transaction status to SUCCESS.
    Returns wallet object.
    """
    amount = Decimal(amount)
    if amount < Decimal('10.00'):
        raise ValidationError("Amount must be at least KSh 10.00.")

    wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

    balance_before = wallet.balance
    wallet.balance += amount
    wallet.save(update_fields=['balance', 'updated_at'])

    if wallet_transaction is not None:
        wallet_transaction.refresh_from_db()
        wallet_transaction.balance_before = balance_before
        wallet_transaction.balance_after = wallet.balance
        wallet_transaction.status = WalletTransaction.SUCCESS
        wallet_transaction.save(update_fields=['balance_before', 'balance_after', 'status'])
    else:
        
        WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type=WalletTransaction.CREDIT,
            description='M-PESA payment received',
            balance_before=balance_before,
            balance_after=wallet.balance,
            status=WalletTransaction.SUCCESS,
        )

    return wallet