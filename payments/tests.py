
import os
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pesaflow.settings')

from django.test import SimpleTestCase, TestCase
from rest_framework.test import APIClient
from unittest.mock import patch

from accounts.models import User
from wallet.models import Wallet


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


class TestMpesaCallback(TestCase):
	def setUp(self):
		self.api_client = APIClient()

	def test_successful_callback_credits_wallet(self):
		user = User.objects.create_user(
			email='buyer@example.com',
			phone='254712345678',
			password='StrongPass1!',
			full_name='Buyer User',
		)

		payload = {
			'Body': {
				'stkCallback': {
					'ResultCode': 0,
					'ResultDesc': 'The service request is processed successfully.',
					'CheckoutRequestID': 'ws_CO_123',
					'MerchantRequestID': '123',
					'CallbackMetadata': {
						'Item': [
							{'Name': 'Amount', 'Value': 1000.00},
							{'Name': 'MpesaReceiptNumber', 'Value': 'ABC123'},
							{'Name': 'PhoneNumber', 'Value': '254712345678'},
							{'Name': 'TransactionDate', 'Value': '20240601120000'},
						]
					}
				}
			}
		}

		response = self.api_client.post('/api/payments/callback/', payload, format='json')

		self.assertEqual(response.status_code, 200)
		wallet = Wallet.objects.get(user=user)
		self.assertEqual(wallet.balance, Decimal('1000.00'))
