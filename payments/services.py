import requests
import os
from requests.auth import HTTPBasicAuth
from django.conf import settings
from base64 import b64encode
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation


_access_token = None
_access_token_expires_at = None


def _daraja_base_url():
	"""Return the Daraja URL for the configured environment."""
	environment = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox').lower()
	if environment == 'production':
		return 'https://api.safaricom.co.ke'
	return 'https://sandbox.safaricom.co.ke'


def _required_setting(name):
	value = getattr(settings, name, '')
	if not value:
		raise ValueError(f'Missing required M-PESA setting: {name}')
	return value


def _generate_timestamp():
	return datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')


def get_mpesa_access_token():
	"""Get and cache a Daraja OAuth access token."""
	global _access_token, _access_token_expires_at

	now = datetime.now(timezone.utc)
	if _access_token and _access_token_expires_at and now < _access_token_expires_at:
		return _access_token

	consumer_key = _required_setting('MPESA_CONSUMER_KEY')
	consumer_secret = _required_setting('MPESA_CONSUMER_SECRET')
	response = requests.get(
		f'{_daraja_base_url()}/oauth/v1/generate?grant_type=client_credentials',
		auth=HTTPBasicAuth(consumer_key, consumer_secret),
		timeout=30,
	)
	response.raise_for_status()
	payload = response.json()
	token = payload.get('access_token')
	if not token:
		raise ValueError('Daraja OAuth response did not contain an access token')

	expires_in = int(payload.get('expires_in', 3599))
	_access_token = token
	_access_token_expires_at = now + timedelta(seconds=max(expires_in - 60, 1))
	return token


def initiate_stk_push(phone_number, amount):
	"""Initiate an M-PESA STK push and return Daraja's response identifiers."""
	try:
		amount = Decimal(str(amount))
	except (InvalidOperation, TypeError, ValueError) as exc:
		raise ValueError('Amount must be a valid positive number') from exc
	if amount <= 0:
		raise ValueError('Amount must be a valid positive number')

	phone_number = str(phone_number).strip()
	if phone_number.startswith('+'):
		phone_number = phone_number[1:]
	if phone_number.startswith('0') and len(phone_number) == 10:
		phone_number = f'254{phone_number[1:]}'
	if not phone_number.isdigit() or len(phone_number) != 12 or not phone_number.startswith('254'):
		raise ValueError('Phone number must be a Kenyan number in 254XXXXXXXXX format')

	shortcode = _required_setting('MPESA_SHORTCODE')
	passkey = _required_setting('MPESA_PASSKEY')
	callback_url = _required_setting('MPESA_CALLBACK_URL')
	timestamp = _generate_timestamp()
	password = b64encode(f'{shortcode}{passkey}{timestamp}'.encode()).decode()
	payload = {
		'BusinessShortCode': shortcode,
		'Password': password,
		'Timestamp': timestamp,
		'TransactionType': 'CustomerPayBillOnline',
		'Amount': int(amount),
		'PartyA': phone_number,
		'PartyB': shortcode,
		'PhoneNumber': phone_number,
		'CallBackURL': callback_url,
		'AccountReference': 'Pesaflow',
		'TransactionDesc': 'Wallet funding',
	}
	response = requests.post(
		f'{_daraja_base_url()}/mpesa/stkpush/v1/processrequest',
		json=payload,
		headers={'Authorization': f'Bearer {get_mpesa_access_token()}'},
		timeout=30,
	)
	response.raise_for_status()
	result = response.json()
	return {
		'merchant_request_id': result.get('MerchantRequestID'),
		'checkout_request_id': result.get('CheckoutRequestID'),
		'response_code': result.get('ResponseCode'),
		'customer_message': result.get('CustomerMessage'),
		'raw_response': result,
	}


def handle_mpesa_callback(data):
	"""Extract the payment result from a Daraja callback payload."""
	callback = data.get('Body', {}).get('stkCallback', {})
	metadata = {
		item.get('Name'): item.get('Value')
		for item in callback.get('CallbackMetadata', {}).get('Item', [])
		if item.get('Name')
	}
	result_code = callback.get('ResultCode')
	return {
		'success': result_code == 0,
		'checkout_request_id': callback.get('CheckoutRequestID'),
		'merchant_request_id': callback.get('MerchantRequestID'),
		'result_code': result_code,
		'result_description': callback.get('ResultDesc'),
		'mpesa_receipt_number': metadata.get('MpesaReceiptNumber'),
		'amount': metadata.get('Amount'),
		'phone_number': metadata.get('PhoneNumber'),
		'transaction_date': metadata.get('TransactionDate'),
	}

# TODO: Service class or functions for M-PESA integration
# TODO: Implement Daraja OAuth2 flow
# TODO: Handle STK push and callbacks
# TODO: Query payment status
# TODO: Coordinate with transactions and wallet apps
