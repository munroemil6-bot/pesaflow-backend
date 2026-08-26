"""
Wallet Models

Owner: Naomi
Responsibility: Wallet model and related database tables

Models to implement:
# TODO: Wallet model
#   - user (OneToOneField to User, cascade delete)
#   - balance (DecimalField, precision 12.2)
#   - currency (CharField default='KES')
#   - created_at (DateTimeField auto_now_add)
#   - updated_at (DateTimeField auto_now)
#   - Methods: get_balance(), add_funds(), deduct_funds(), to_dict()

# TODO: WalletTransaction model (optional, for detailed history)
#   - wallet (ForeignKey)
#   - amount
#   - transaction_type (credit, debit)
#   - description
#   - balance_before
#   - balance_after
#   - created_at
"""




from decimal import Decimal
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.db import transaction


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet',
    )
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='KES')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wallets'

    def __str__(self):
        return f"{self.user} - {self.balance} {self.currency}"

    def get_balance(self):
        return self.balance

    @transaction.atomic
    def add_funds(self, amount, description=''):
        if amount <= 0:
            raise ValidationError("Amount must be positive.")

        wallet = Wallet.objects.select_for_update().get(pk=self.pk)
        balance_before = wallet.balance
        wallet.balance += Decimal(amount)
        wallet.save(update_fields=['balance', 'updated_at'])

        WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type=WalletTransaction.CREDIT,
            description=description,
            balance_before=balance_before,
            balance_after=wallet.balance,
        )

        self.balance = wallet.balance
        return wallet.balance

    @transaction.atomic
    def deduct_funds(self, amount, description=''):
        if amount <= 0:
            raise ValidationError("Amount must be positive.")

        wallet = Wallet.objects.select_for_update().get(pk=self.pk)
        if wallet.balance < amount:
            raise ValidationError("Insufficient funds.")

        balance_before = wallet.balance
        wallet.balance -= Decimal(amount)
        wallet.save(update_fields=['balance', 'updated_at'])

        WalletTransaction.objects.create(
            wallet=wallet,
            amount=amount,
            transaction_type=WalletTransaction.DEBIT,
            description=description,
            balance_before=balance_before,
            balance_after=wallet.balance,
        )

        self.balance = wallet.balance
        return wallet.balance


class WalletTransaction(models.Model):
    CREDIT = 'credit'
    DEBIT = 'debit'
    TRANSACTION_TYPE_CHOICES = [
        (CREDIT, 'Credit'),
        (DEBIT, 'Debit'),
    ]

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'wallet_transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.wallet} | {self.transaction_type} | {self.amount}"