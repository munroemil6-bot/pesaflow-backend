from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from beneficiaries.models import Beneficiary
from transactions.models import Transaction
from wallet.models import Wallet, WalletTransaction


class Command(BaseCommand):
    help = "Create repeatable PesaFlow demo users, wallets, beneficiaries, and transfers."

    demo_users = [
        ("amina.wanjiku@gmail.com", "Amina Wanjiku", "0711000001", Decimal("18500.00")),
        ("brian.ochieng@gmail.com", "Brian Ochieng", "0711000002", Decimal("9200.00")),
        ("carol.njeri@gmail.com", "Carol Njeri", "0711000003", Decimal("14750.00")),
        ("david.kiptoo@gmail.com", "David Kiptoo", "0711000004", Decimal("6300.00")),
        ("esther.auma@gmail.com", "Esther Auma", "0711000005", Decimal("11200.00")),
        ("felix.mwangi@gmail.com", "Felix Mwangi", "0711000006", Decimal("7800.00")),
        ("grace.nyambura@gmail.com", "Grace Nyambura", "0711000007", Decimal("22100.00")),
    ]

    def handle(self, *args, **options):
        with transaction.atomic():
            users = self._create_users()
            self._create_wallets(users)
            self._create_beneficiaries(users)
            self._create_transfers(users)

        self.stdout.write(self.style.SUCCESS("Created or updated 7 PesaFlow demo users and related data."))
        self.stdout.write("Demo email accounts use an unusable password until one is set explicitly.")

    def _create_users(self):
        users = []
        for email, full_name, phone, balance in self.demo_users:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"full_name": full_name, "phone": phone},
            )
            changed = False
            if user.full_name != full_name:
                user.full_name = full_name
                changed = True
            if user.phone != phone:
                user.phone = phone
                changed = True
            if created:
                user.set_unusable_password()
                changed = True
            if changed:
                user.save()
            users.append(user)
        return users

    def _create_wallets(self, users):
        for user, (_, _, _, balance) in zip(users, self.demo_users):
            wallet, _ = Wallet.objects.get_or_create(user=user)
            wallet.balance = balance
            wallet.currency = "KES"
            wallet.save(update_fields=["balance", "currency", "updated_at"])
            WalletTransaction.objects.filter(wallet=wallet, description__startswith="Demo:").delete()
            WalletTransaction.objects.create(
                wallet=wallet,
                amount=balance,
                transaction_type=WalletTransaction.CREDIT,
                description="Demo: opening wallet balance",
                balance_before=Decimal("0.00"),
                balance_after=balance,
            )

    def _create_beneficiaries(self, users):
        for index, user in enumerate(users, start=1):
            Beneficiary.objects.get_or_create(
                user=user,
                phone=f"07120000{index:02d}",
                defaults={"name": f"PesaFlow Contact {index}"},
            )

    def _create_transfers(self, users):
        transfers = [
            (0, 1, Decimal("1250.00"), Transaction.Status.COMPLETED, "Rent contribution"),
            (1, 2, Decimal("850.00"), Transaction.Status.COMPLETED, "Lunch reimbursement"),
            (2, 3, Decimal("2100.00"), Transaction.Status.PENDING, "School fees support"),
            (3, 4, Decimal("475.00"), Transaction.Status.FAILED, "Utility payment"),
            (4, 5, Decimal("3200.00"), Transaction.Status.COMPLETED, "Family support"),
            (5, 6, Decimal("675.00"), Transaction.Status.CANCELLED, "Travel contribution"),
            (6, 0, Decimal("1500.00"), Transaction.Status.COMPLETED, "Shared project refund"),
        ]
        for number, (sender_index, recipient_index, amount, status, description) in enumerate(transfers, start=1):
            Transaction.objects.update_or_create(
                reference=f"DEMO-{number:04d}",
                defaults={
                    "sender": users[sender_index],
                    "recipient": users[recipient_index],
                    "amount": amount,
                    "fee": Decimal("25.00"),
                    "total_amount": amount + Decimal("25.00"),
                    "status": status,
                    "description": f"Demo: {description}",
                },
            )
