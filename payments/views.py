

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import requests

from wallet.models import Wallet
from wallet.services import get_or_create_wallet, add_funds_from_payment

from .serializers import MpesaSTKSerializer
from .services import initiate_stk_push, handle_mpesa_callback
from .models import MpesaPayment

User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stk_push(request):
	serializer = MpesaSTKSerializer(data=request.data)
	if not serializer.is_valid():
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	payment = MpesaPayment.objects.create(
		user=request.user,
		phone_number=serializer.validated_data['phone_number'],
		amount=serializer.validated_data['amount'],
	)
	try:
		result = initiate_stk_push(
			serializer.validated_data['phone_number'],
			serializer.validated_data['amount'],
		)
	except ValueError as exc:
		payment.status = MpesaPayment.Status.FAILED
		payment.result_description = str(exc)
		payment.save(update_fields=['status', 'result_description', 'updated_at'])
		return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
	except requests.RequestException as exc:
		payment.status = MpesaPayment.Status.FAILED
		payment.result_description = 'Unable to contact M-PESA at this time.'
		payment.save(update_fields=['status', 'result_description', 'updated_at'])
		return Response(
			{'detail': 'Unable to contact M-PESA at this time.'},
			status=status.HTTP_502_BAD_GATEWAY,
		)

	payment.merchant_request_id = result.get('merchant_request_id') or ''
	payment.checkout_request_id = result.get('checkout_request_id')
	payment.result_code = result.get('response_code') or ''
	payment.result_description = result.get('customer_message') or ''
	payment.save(update_fields=[
		'merchant_request_id', 'checkout_request_id', 'result_code',
		'result_description', 'updated_at',
	])
	result['payment_id'] = payment.id

	return Response(result, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
@permission_classes([AllowAny])
def callback(request):
	"""Debit/credit wallet only after a real Daraja success callback arrives."""
	payload = request.data or {}
	callback_data = handle_mpesa_callback(payload)
	checkout_request_id = callback_data.get('checkout_request_id')
	payment = MpesaPayment.objects.filter(checkout_request_id=checkout_request_id).first() if checkout_request_id else None
	if not callback_data.get('success'):
		if payment:
			payment.status = MpesaPayment.Status.FAILED
			payment.result_code = str(callback_data.get('result_code') or '')
			payment.result_description = callback_data.get('result_description') or ''
			payment.save(update_fields=['status', 'result_code', 'result_description', 'updated_at'])
		return Response({
			'success': False,
			'result_code': callback_data.get('result_code'),
			'result_description': callback_data.get('result_description'),
		}, status=status.HTTP_200_OK)

	phone_number = callback_data.get('phone_number')
	amount = callback_data.get('amount')
	if not checkout_request_id or not phone_number or not amount:
		return Response({'success': False, 'detail': 'Incomplete M-PESA callback payload.'}, status=status.HTTP_400_BAD_REQUEST)

	with transaction.atomic():
		payment = MpesaPayment.objects.select_for_update().filter(
			checkout_request_id=checkout_request_id,
		).first()

		if payment and payment.status == MpesaPayment.Status.SUCCESS:
			wallet = get_or_create_wallet(payment.user)
			wallet.refresh_from_db()
			return Response({
				'success': True,
				'user_id': payment.user_id,
				'wallet_balance': wallet.balance,
				'mpesa_receipt_number': payment.mpesa_receipt_number,
				'already_processed': True,
			}, status=status.HTTP_200_OK)

		normalized_phone = str(phone_number).strip().replace('+', '')
		if normalized_phone.startswith('0') and len(normalized_phone) == 10:
			normalized_phone = f'254{normalized_phone[1:]}'
		if payment:
			user = payment.user
			if Decimal(str(amount)) != payment.amount:
				return Response({'success': False, 'detail': 'Callback amount does not match the payment request.'}, status=status.HTTP_400_BAD_REQUEST)
		elif normalized_phone.startswith('254') and len(normalized_phone) == 12:
			user = User.objects.filter(phone=normalized_phone).first()
		else:
			user = User.objects.filter(phone__icontains=normalized_phone).first()

		if not user:
			return Response({'success': False, 'detail': 'No user matched this M-PESA callback number.'}, status=status.HTTP_404_NOT_FOUND)

		if payment is None:
			payment = MpesaPayment.objects.create(
				user=user,
				phone_number=normalized_phone,
				amount=Decimal(str(amount)),
				checkout_request_id=checkout_request_id,
			)

		wallet = get_or_create_wallet(payment.user)
		amount_decimal = Decimal(str(amount))
		try:
			add_funds_from_payment(wallet, amount_decimal, None)
			payment.status = MpesaPayment.Status.SUCCESS
			payment.amount = amount_decimal
			payment.mpesa_receipt_number = callback_data.get('mpesa_receipt_number')
			payment.result_code = str(callback_data.get('result_code') or '')
			payment.result_description = callback_data.get('result_description') or ''
			payment.save(update_fields=[
				'status', 'amount', 'mpesa_receipt_number', 'result_code',
				'result_description', 'updated_at',
			])
			wallet.refresh_from_db()
		except ValidationError as exc:
			return Response({'success': False, 'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

	return Response({
		'success': True,
		'user_id': payment.user_id,
		'wallet_balance': wallet.balance,
		'mpesa_receipt_number': callback_data.get('mpesa_receipt_number'),
	}, status=status.HTTP_200_OK)

# TODO: @api_view(['GET']) check_payment_status view
# TODO: @api_view(['POST']) simulate_payment view (for testing)
# TODO: @api_view(['GET']) get_access_token view (internal use)
