from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from transactions.models import Transaction
from wallet.models import Wallet


class AdminDashboardApiTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("admin@example.com", "password", phone="0700000010", full_name="Admin")
        self.sender = User.objects.create_user("sender@example.com", "password", phone="0700000011", full_name="Sender")
        self.recipient = User.objects.create_user("recipient@example.com", "password", phone="0700000012", full_name="Recipient")
        Wallet.objects.create(user=self.sender, balance=Decimal("100.00"))
        Wallet.objects.create(user=self.recipient, balance=Decimal("50.00"))
        Transaction.objects.create(sender=self.sender, recipient=self.recipient, amount=Decimal("10.00"), fee=Decimal("0.10"), total_amount=Decimal("10.10"), status=Transaction.Status.COMPLETED)
        self.client = APIClient()

    def test_admin_can_read_summary_and_transactions(self):
        self.client.force_authenticate(self.admin)
        summary = self.client.get("/api/admin-dashboard/summary/")
        self.assertEqual(summary.status_code, 200)
        self.assertEqual(summary.data["total_transactions"], 1)
        self.assertEqual(Decimal(summary.data["total_fees_collected"]), Decimal("0.10"))
        transactions = self.client.get("/api/admin-dashboard/transactions/")
        self.assertEqual(transactions.status_code, 200)
        self.assertEqual(transactions.data["total_count"], 1)

    def test_standard_user_is_denied(self):
        self.client.force_authenticate(self.sender)
        response = self.client.get("/api/admin-dashboard/summary/")
        self.assertEqual(response.status_code, 403)
