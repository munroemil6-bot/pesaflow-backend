"""
Payments Tests

Owner: Myles
Responsibility: Unit tests for payment endpoints

Tests to implement:
# TODO: TestStkPush
#   - test_stk_push_success
#   - test_stk_push_invalid_phone
#   - test_stk_push_invalid_amount
#   - test_stk_push_authenticated_required

# TODO: TestPaymentCallback
#   - test_callback_success
#   - test_callback_failed
#   - test_callback_updates_wallet
#   - test_callback_creates_transaction

# TODO: TestPaymentStatus
#   - test_query_pending_payment
#   - test_query_completed_payment
#   - test_query_failed_payment
#   - test_query_nonexistent_payment

# TODO: TestAccessToken
#   - test_get_access_token
#   - test_access_token_caching
#   - test_access_token_expiration

# TODO: TestSimulation
#   - test_simulate_payment_success
#   - test_simulate_payment_failure
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pesaflow.settings')

import pytest
from rest_framework.test import APIClient
from unittest.mock import patch


@pytest.fixture
def api_client():
	return APIClient()


@pytest.fixture
def user():
	class AuthenticatedUser:
		is_authenticated = True

	return AuthenticatedUser()


def test_stk_push_success(api_client, user):
	api_client.force_authenticate(user=user)
	daraja_response = {
		'merchant_request_id': 'merchant-123',
		'checkout_request_id': 'checkout-123',
		'response_code': '0',
	}

	with patch('payments.views.initiate_stk_push', return_value=daraja_response):
		response = api_client.post(
			'/api/payments/stk-push/',
			{'phone_number': '0712345678', 'amount': '1000.00'},
			format='json',
		)

	assert response.status_code == 202
	assert response.json() == daraja_response


def test_stk_push_invalid_phone(api_client, user):
	api_client.force_authenticate(user=user)
	response = api_client.post(
		'/api/payments/stk-push/',
		{'phone_number': '123', 'amount': '1000.00'},
		format='json',
	)

	assert response.status_code == 400
	assert 'phone_number' in response.json()


def test_stk_push_invalid_amount(api_client, user):
	api_client.force_authenticate(user=user)
	response = api_client.post(
		'/api/payments/stk-push/',
		{'phone_number': '0712345678', 'amount': '0'},
		format='json',
	)

	assert response.status_code == 400
	assert 'amount' in response.json()


def test_stk_push_authenticated_required(api_client):
	response = api_client.post(
		'/api/payments/stk-push/',
		{'phone_number': '0712345678', 'amount': '1000.00'},
		format='json',
	)

	assert response.status_code == 401
