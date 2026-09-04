import requests
import hashlib
import hmac
import json
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


def generate_timestamp():
	return _generate_timestamp()


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


def initiate_mpesa_withdrawal(phone_number, amount):
	"""Submit a no-fee wallet withdrawal to a Kenyan mobile number."""
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

	initiator_name = _required_setting('MPESA_INITIATOR_NAME')
	security_credential = _required_setting('MPESA_SECURITY_CREDENTIAL')
	shortcode = _required_setting('MPESA_SHORTCODE')
	result_url = _required_setting('MPESA_RESULT_URL')
	timeout_url = _required_setting('MPESA_TIMEOUT_URL')
	payload = {
		'InitiatorName': initiator_name,
		'SecurityCredential': security_credential,
		'CommandID': 'BusinessPayment',
		'Amount': int(amount),
		'PartyA': shortcode,
		'PartyB': phone_number,
		'Remarks': 'PesaFlow wallet withdrawal',
		'QueueTimeOutURL': timeout_url,
		'ResultURL': result_url,
		'Occasion': 'Wallet withdrawal',
	}
	response = requests.post(
		f'{_daraja_base_url()}/mpesa/b2c/v1/paymentrequest',
		json=payload,
		headers={'Authorization': f'Bearer {get_mpesa_access_token()}'},
		timeout=30,
	)
	response.raise_for_status()
	result = response.json()
	return {
		'conversation_id': result.get('ConversationID'),
		'originator_conversation_id': result.get('OriginatorConversationID'),
		'response_code': result.get('ResponseCode'),
		'result_description': result.get('ResponseDescription'),
		'raw_response': result,
	}


def handle_mpesa_withdrawal_callback(data):
	"""Extract the result identifiers from a Daraja B2C callback."""
	result = data.get('Result', data.get('result', {})) if isinstance(data, dict) else {}
	if not isinstance(result, dict):
		result = {}
	return {
		'conversation_id': result.get('ConversationID'),
		'originator_conversation_id': result.get('OriginatorConversationID'),
		'conversation_result': result.get('ResultCode'),
		'result_description': result.get('ResultDesc') or result.get('ResultDescription'),
		'transaction_id': result.get('TransactionID'),
		'success': str(result.get('ResultCode')) == '0',
	}


def handle_mpesa_callback(data):
	"""Extract the payment result from a Daraja callback payload."""
	payload = data
	if hasattr(payload, 'dict'):
		payload = payload.dict()
	if isinstance(payload, str):
		try:
			payload = json.loads(payload)
		except json.JSONDecodeError:
			payload = {}
	if not isinstance(payload, dict):
		payload = {}

	body = payload.get('Body') or payload.get('body') or {}
	if isinstance(body, str):
		try:
			body = json.loads(body)
		except json.JSONDecodeError:
			body = {}
	if not isinstance(body, dict):
		body = {}

	callback = body.get('stkCallback') or body.get('STKCallback') or body.get('callback') or {}
	if isinstance(callback, str):
		try:
			callback = json.loads(callback)
		except json.JSONDecodeError:
			callback = {}
	if not isinstance(callback, dict):
		callback = {}

	metadata_items = callback.get('CallbackMetadata', {}).get('Item', [])
	if isinstance(metadata_items, dict):
		metadata_items = [metadata_items]
	metadata = {
		item.get('Name'): item.get('Value')
		for item in metadata_items
		if isinstance(item, dict) and item.get('Name')
	}
	result_code = callback.get('ResultCode')
	result_code_text = str(result_code).strip() if result_code is not None else ''
	return {
		'success': result_code_text in {'0', '00'},
		'checkout_request_id': callback.get('CheckoutRequestID'),
		'merchant_request_id': callback.get('MerchantRequestID'),
		'result_code': result_code,
		'result_description': callback.get('ResultDesc'),
		'mpesa_receipt_number': metadata.get('MpesaReceiptNumber'),
		'amount': metadata.get('Amount'),
		'phone_number': metadata.get('PhoneNumber'),
		'transaction_date': metadata.get('TransactionDate'),
	}


def query_payment_status(checkout_request_id):
	"""Query Daraja for the current status of an STK push."""
	if not checkout_request_id:
		raise ValueError('checkout_request_id is required')

	shortcode = _required_setting('MPESA_SHORTCODE')
	passkey = _required_setting('MPESA_PASSKEY')
	timestamp = _generate_timestamp()
	password = b64encode(f'{shortcode}{passkey}{timestamp}'.encode()).decode()
	payload = {
		'BusinessShortCode': shortcode,
		'Password': password,
		'Timestamp': timestamp,
		'CheckoutRequestID': checkout_request_id,
	}
	response = requests.post(
		f'{_daraja_base_url()}/mpesa/stkpushquery/v1/query',
		json=payload,
		headers={'Authorization': f'Bearer {get_mpesa_access_token()}'},
		timeout=30,
	)
	response.raise_for_status()
	return response.json()


def validate_callback_signature(callback_data, timestamp, signature):
	"""Validate a callback signature using the configured callback secret."""
	secret = getattr(settings, 'MPESA_CALLBACK_SECRET', '')
	if not secret or not timestamp or not signature:
		return False

	canonical_data = json.dumps(
		callback_data,
		sort_keys=True,
		separators=(',', ':'),
	)
	message = f'{timestamp}.{canonical_data}'.encode()
	expected_signature = hmac.new(
		secret.encode(),
		message,
		hashlib.sha256,
	).hexdigest()
	return hmac.compare_digest(expected_signature, signature)


def simulate_payment(checkout_request_id):
	"""Simulate a sandbox payment query for a checkout request."""
	if getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox').lower() != 'sandbox':
		raise ValueError('Payment simulation is available only in the sandbox environment')
	if not checkout_request_id:
		raise ValueError('checkout_request_id is required')

	response = query_payment_status(checkout_request_id)
	return response

# TODO: Service class or functions for M-PESA integration
# TODO: Implement Daraja OAuth2 flow
# TODO: Handle STK push and callbacks
# TODO: Query payment status
# TODO: Coordinate with transactions and wallet apps
