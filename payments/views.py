

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import requests

from wallet.models import Wallet
from wallet.services import get_or_create_wallet, add_funds_from_payment

from .serializers import MpesaSTKSerializer
from .services import initiate_stk_push, handle_mpesa_callback

User = get_user_model()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def stk_push(request):
	serializer = MpesaSTKSerializer(data=request.data)
	if not serializer.is_valid():
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	try:
		result = initiate_stk_push(
			serializer.validated_data['phone_number'],
			serializer.validated_data['amount'],
		)
	except ValueError as exc:
		return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
	except requests.RequestException as exc:
		return Response(
			{'detail': 'Unable to contact M-PESA at this time.'},
			status=status.HTTP_502_BAD_GATEWAY,
		)

	return Response(result, status=status.HTTP_202_ACCEPTED)


@api_view(['POST'])
@permission_classes([AllowAny])
def callback(request):
	"""Debit/credit wallet only after a real Daraja success callback arrives."""
	payload = request.data or {}
	callback_data = handle_mpesa_callback(payload)
	if not callback_data.get('success'):
		return Response({
			'success': False,
			'result_code': callback_data.get('result_code'),
			'result_description': callback_data.get('result_description'),
		}, status=status.HTTP_200_OK)

	phone_number = callback_data.get('phone_number')
	amount = callback_data.get('amount')
	if not phone_number or not amount:
		return Response({'success': False, 'detail': 'Incomplete M-PESA callback payload.'}, status=status.HTTP_400_BAD_REQUEST)

	normalized_phone = str(phone_number).strip().replace('+', '')
	if normalized_phone.startswith('0') and len(normalized_phone) == 10:
		normalized_phone = f'254{normalized_phone[1:]}'
	if normalized_phone.startswith('254') and len(normalized_phone) == 12:
		user = User.objects.filter(phone=normalized_phone).first()
	else:
		user = User.objects.filter(phone__icontains=normalized_phone).first()

	if not user:
		return Response({'success': False, 'detail': 'No user matched this M-PESA callback number.'}, status=status.HTTP_404_NOT_FOUND)

	wallet = get_or_create_wallet(user)
	amount_decimal = Decimal(str(amount))
	try:
		add_funds_from_payment(wallet, amount_decimal, None)
		wallet.refresh_from_db()
	except ValidationError as exc:
		return Response({'success': False, 'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

	return Response({
		'success': True,
		'user_id': user.id,
		'wallet_balance': wallet.balance,
		'mpesa_receipt_number': callback_data.get('mpesa_receipt_number'),
	}, status=status.HTTP_200_OK)

# TODO: @api_view(['GET']) check_payment_status view
# TODO: @api_view(['POST']) simulate_payment view (for testing)
# TODO: @api_view(['GET']) get_access_token view (internal use)
