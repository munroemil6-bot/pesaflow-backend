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

from django.test import SimpleTestCase
from rest_framework.test import APIClient
from unittest.mock import patch


class TestStkPush(SimpleTestCase):
	def setUp(self):
		self.api_client = APIClient()

		class AuthenticatedUser:
			is_authenticated = True

		self.user = AuthenticatedUser()

	def test_stk_push_success(self):
		self.api_client.force_authenticate(user=self.user)
		daraja_response = {
			'merchant_request_id': 'merchant-123',
			'checkout_request_id': 'checkout-123',
			'response_code': '0',
		}

		with patch('payments.views.initiate_stk_push', return_value=daraja_response):
			response = self.api_client.post(
				'/api/payments/stk-push/',
				{'phone_number': '0712345678', 'amount': '1000.00'},
				format='json',
			)

		self.assertEqual(response.status_code, 202)
		self.assertEqual(response.json(), daraja_response)

	def test_stk_push_invalid_phone(self):
		self.api_client.force_authenticate(user=self.user)
		response = self.api_client.post(
			'/api/payments/stk-push/',
			{'phone_number': '123', 'amount': '1000.00'},
			format='json',
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn('phone_number', response.json())

	def test_stk_push_invalid_amount(self):
		self.api_client.force_authenticate(user=self.user)
		response = self.api_client.post(
			'/api/payments/stk-push/',
			{'phone_number': '0712345678', 'amount': '0'},
			format='json',
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn('amount', response.json())

	def test_stk_push_authenticated_required(self):
		response = self.api_client.post(
			'/api/payments/stk-push/',
			{'phone_number': '0712345678', 'amount': '1000.00'},
			format='json',
		)

		self.assertEqual(response.status_code, 401)
