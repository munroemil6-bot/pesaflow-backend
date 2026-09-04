from decimal import Decimal
from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from wallet.models import Wallet, WalletTransaction

User = get_user_model()



@pytest.fixture
def user(db):
    return User.objects.create_user(email='naomi@example.com', password='testpass123')


@pytest.fixture
def other_user(db):
    return User.objects.create_user(email='other@example.com', password='testpass123')


@pytest.fixture
def wallet(user):
    return Wallet.objects.create(user=user, balance=Decimal('1000.00'), currency='KES')


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


def make_transaction(wallet, amount, txn_type, status_=WalletTransaction.SUCCESS, created_at=None):
    txn = WalletTransaction.objects.create(
        wallet=wallet,
        amount=amount,
        transaction_type=txn_type,
        balance_before=wallet.balance,
        balance_after=wallet.balance + amount if txn_type == WalletTransaction.CREDIT else wallet.balance - amount,
        status=status_,
    )
    if created_at:
        WalletTransaction.objects.filter(pk=txn.pk).update(created_at=created_at)
        txn.refresh_from_db()
    return txn



@pytest.mark.django_db
class TestWalletRetrieval:

    def test_get_wallet_authenticated(self, auth_client, wallet):
        url = reverse('wallet:wallet-detail')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['balance']) == wallet.balance
        assert response.data['currency'] == wallet.currency

    def test_get_wallet_unauthenticated(self, api_client):
        url = reverse('wallet:wallet-detail')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_wallet_not_found(self, auth_client, user):
        
        assert not Wallet.objects.filter(user=user).exists()

        url = reverse('wallet:wallet-detail')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert Wallet.objects.filter(user=user).exists()
        assert Decimal(response.data['balance']) == Decimal('0.00')



@pytest.mark.django_db
class TestWalletBalance:

    def test_get_balance_success(self, auth_client, wallet):
        url = reverse('wallet:wallet-balance')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['balance']) == wallet.balance

    def test_balance_currency_format(self, auth_client, wallet):
        url = reverse('wallet:wallet-balance')
        response = auth_client.get(url)

        assert response.data['currency'] == 'KES'
        assert set(response.data.keys()) == {'balance', 'currency'}



@pytest.mark.django_db
class TestWalletAnalytics:

    def test_get_analytics_empty_wallet(self, auth_client, wallet):
        url = reverse('wallet:wallet-analytics')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert Decimal(response.data['total_sent']) == Decimal('0.00')
        assert Decimal(response.data['total_received']) == Decimal('0.00')
        assert response.data['transaction_count'] == 0
        assert response.data['last_transaction_at'] is None

    def test_get_analytics_with_transactions(self, auth_client, wallet):
        make_transaction(wallet, Decimal('200.00'), WalletTransaction.CREDIT)
        make_transaction(wallet, Decimal('50.00'), WalletTransaction.DEBIT)

        url = reverse('wallet:wallet-analytics')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['transaction_count'] == 2
        assert response.data['last_transaction_at'] is not None

    def test_analytics_calculations(self, auth_client, wallet):
        make_transaction(wallet, Decimal('300.00'), WalletTransaction.CREDIT)
        make_transaction(wallet, Decimal('100.00'), WalletTransaction.CREDIT)
        make_transaction(wallet, Decimal('50.00'), WalletTransaction.DEBIT)

        url = reverse('wallet:wallet-analytics')
        response = auth_client.get(url)

        assert Decimal(response.data['total_received']) == Decimal('400.00')
        assert Decimal(response.data['total_sent']) == Decimal('50.00')
        assert response.data['transaction_count'] == 3
        expected_avg = (Decimal('300.00') + Decimal('100.00') + Decimal('50.00')) / 3
        assert Decimal(response.data['average_transaction']) == pytest.approx(
            float(expected_avg), rel=1e-3
        )




@pytest.mark.django_db
class TestAddFunds:

    @patch('payments.services.initiate_mpesa_payment')
    def test_add_funds_initiates_payment(self, mock_mpesa, auth_client, wallet):
        mock_mpesa.return_value = {'checkout_request_id': 'ws_CO_123'}

        url = reverse('wallet:wallet-add-funds')
        response = auth_client.post(url, {'amount': '500.00', 'description': 'Top up'})

        assert response.status_code == status.HTTP_201_CREATED
        mock_mpesa.assert_called_once()
        _, kwargs = mock_mpesa.call_args
        assert kwargs['amount'] == Decimal('500.00')
        assert kwargs['user'] == wallet.user

    def test_add_funds_invalid_amount(self, auth_client, wallet):
        url = reverse('wallet:wallet-add-funds')

        response = auth_client.post(url, {'amount': '-10.00'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = auth_client.post(url, {'amount': '0'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('payments.services.initiate_mpesa_payment')
    def test_add_funds_creates_transaction(self, mock_mpesa, auth_client, wallet):
        mock_mpesa.return_value = {'checkout_request_id': 'ws_CO_456'}

        url = reverse('wallet:wallet-add-funds')
        response = auth_client.post(url, {'amount': '250.00', 'description': 'Deposit'})

        assert response.status_code == status.HTTP_201_CREATED
        txn = WalletTransaction.objects.get(wallet=wallet)
        assert txn.amount == Decimal('250.00')
        assert txn.transaction_type == WalletTransaction.CREDIT
        assert txn.status == WalletTransaction.PENDING
        
        wallet.refresh_from_db()
        assert wallet.balance == Decimal('1000.00')


@pytest.mark.django_db
class TestWithdrawFunds:

    @patch('wallet.views.initiate_mpesa_withdrawal')
    def test_withdraws_without_fee(self, mock_withdrawal, auth_client, wallet):
        mock_withdrawal.return_value = {'conversation_id': 'AG_123'}

        url = reverse('wallet:wallet-withdraw')
        response = auth_client.post(url, {'amount': '250.00', 'phone_number': '0712345678'})

        assert response.status_code == status.HTTP_202_ACCEPTED
        mock_withdrawal.assert_called_once_with('254712345678', Decimal('250.00'))
        assert Decimal(response.data['wallet']['balance']) == Decimal('750.00')
        assert response.data['phone_number'] == '254712345678'
        assert response.data['provider_reference'] == 'AG_123'
        assert response.data['status'] == WalletTransaction.PENDING

    def test_withdrawal_rejects_insufficient_balance(self, auth_client, wallet):
        url = reverse('wallet:wallet-withdraw')
        response = auth_client.post(url, {'amount': '1001.00', 'phone_number': '0712345678'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        wallet.refresh_from_db()
        assert wallet.balance == Decimal('1000.00')

    def test_withdrawal_rejects_invalid_phone(self, auth_client, wallet):
        url = reverse('wallet:wallet-withdraw')
        response = auth_client.post(url, {'amount': '100.00', 'phone_number': '123'})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('wallet.views.initiate_mpesa_withdrawal')
    def test_failed_withdrawal_is_refunded(self, mock_withdrawal, auth_client, wallet, api_client):
        mock_withdrawal.return_value = {'conversation_id': 'AG_FAIL'}
        url = reverse('wallet:wallet-withdraw')
        response = auth_client.post(url, {'amount': '250.00', 'phone_number': '0712345678'})
        assert response.status_code == status.HTTP_202_ACCEPTED

        callback_url = reverse('payments:withdrawal-callback')
        callback = api_client.post(callback_url, {
            'Result': {
                'ConversationID': 'AG_FAIL',
                'ResultCode': 1,
                'ResultDesc': 'Recipient unavailable',
            },
        }, format='json')

        assert callback.status_code == status.HTTP_200_OK
        wallet.refresh_from_db()
        assert wallet.balance == Decimal('1000.00')
        assert WalletTransaction.objects.filter(
            wallet=wallet,
            status=WalletTransaction.FAILED,
        ).exists()



@pytest.mark.django_db
class TestWalletHistory:

    def test_get_transaction_history(self, auth_client, wallet):
        make_transaction(wallet, Decimal('100.00'), WalletTransaction.CREDIT)
        make_transaction(wallet, Decimal('30.00'), WalletTransaction.DEBIT)

        url = reverse('wallet:wallet-history')
        response = auth_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) == 2

    def test_history_pagination(self, auth_client, wallet):
        for i in range(15):
            make_transaction(wallet, Decimal('10.00'), WalletTransaction.CREDIT)

        url = reverse('wallet:wallet-history')
        response = auth_client.get(url, {'page': 1})

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert response.data['count'] == 15
        assert len(response.data['results']) <= 10  # assumes default page_size=10

    def test_history_date_filter(self, auth_client, wallet):
        old_date = timezone.now() - timedelta(days=30)
        recent_date = timezone.now() - timedelta(days=1)

        make_transaction(wallet, Decimal('50.00'), WalletTransaction.CREDIT, created_at=old_date)
        make_transaction(wallet, Decimal('75.00'), WalletTransaction.CREDIT, created_at=recent_date)

        url = reverse('wallet:wallet-history')
        cutoff = (timezone.now() - timedelta(days=7)).date().isoformat()
        response = auth_client.get(url, {'start_date': cutoff})

        assert response.status_code == status.HTTP_200_OK
        results = response.data.get('results', response.data)
        assert len(results) == 1
        assert Decimal(results[0]['amount']) == Decimal('75.00')