from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from wallet.models import Wallet
from .models import Transaction
from .services import create_transaction, get_transaction_summary


class TransactionServiceTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user("sender@example.com", "password", phone="0700000001", full_name="Sender")
        self.recipient = User.objects.create_user("recipient@example.com", "password", phone="0700000002", full_name="Recipient")
        Wallet.objects.create(user=self.sender, balance=Decimal("100.00"))
        Wallet.objects.create(user=self.recipient, balance=Decimal("0.00"))

    def test_transfer_updates_wallets_and_marks_transaction_completed(self):
        transfer = create_transaction(self.sender, self.recipient, Decimal("50.00"), "Lunch")
        self.assertEqual(transfer.status, Transaction.Status.COMPLETED)
        self.assertEqual(transfer.fee, Decimal("0.50"))
        self.sender.wallet.refresh_from_db()
        self.recipient.wallet.refresh_from_db()
        self.assertEqual(self.sender.wallet.balance, Decimal("49.50"))
        self.assertEqual(self.recipient.wallet.balance, Decimal("50.00"))

    def test_transfer_requires_sufficient_balance(self):
        with self.assertRaises(ValidationError):
            create_transaction(self.sender, self.recipient, Decimal("100.00"))
        self.assertFalse(Transaction.objects.exists())

    def test_summary_reports_sent_and_received_totals(self):
        create_transaction(self.sender, self.recipient, Decimal("20.00"))
        summary = get_transaction_summary(self.sender)
        self.assertEqual(summary["total_sent"], Decimal("20.00"))
        self.assertEqual(summary["transaction_count"], 1)


class TransactionApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("user@example.com", "password", phone="0700000003", full_name="User")
        self.recipient = User.objects.create_user("other@example.com", "password", phone="0700000004", full_name="Other")
        Wallet.objects.create(user=self.user, balance=Decimal("20.00"))
        Wallet.objects.create(user=self.recipient)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_post_transfer_and_sent_endpoint(self):
        response = self.client.post("/api/transactions/", {"recipient_id": self.recipient.pk, "amount": "10.00"}, format="json")
        self.assertEqual(response.status_code, 201)
        sent = self.client.get("/api/transactions/sent/")
        self.assertEqual(sent.status_code, 200)
        self.assertEqual(len(sent.data), 1)
