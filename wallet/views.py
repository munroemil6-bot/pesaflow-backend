from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# TODO: @api_view(['GET']) wallet_detail view
# TODO: @api_view(['GET']) wallet_balance view
# TODO: @api_view(['GET']) wallet_analytics view
# TODO: @api_view(['GET']) wallet_history view
# TODO: @api_view(['POST']) add_funds view


from .serializers import (
    WalletSerializer,
    WalletBalanceSerializer,
    WalletAnalyticsSerializer,
    WalletTransactionSerializer,
    AddFundsSerializer,
    WithdrawFundsSerializer,
)
from . import services
from payments.services import initiate_mpesa_withdrawal


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_detail(request):
    wallet = services.get_or_create_wallet(request.user)
    serializer = WalletSerializer(wallet)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_balance(request):
    wallet = services.get_or_create_wallet(request.user)
    data = services.get_balance(wallet)
    serializer = WalletBalanceSerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_analytics(request):
    wallet = services.get_or_create_wallet(request.user)
    data = services.get_wallet_analytics(wallet)
    serializer = WalletAnalyticsSerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def wallet_history(request):
    wallet = services.get_or_create_wallet(request.user)
    transactions = wallet.transactions.all()
    serializer = WalletTransactionSerializer(transactions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_funds(request):
    wallet = services.get_or_create_wallet(request.user)
    serializer = AddFundsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        wallet_transaction = services.add_funds(
            wallet,
            serializer.validated_data['amount'],
            serializer.validated_data.get('description', 'Wallet funding'),
        )
    except Exception as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

    result = WalletTransactionSerializer(wallet_transaction)
    return Response({
        'message': 'Wallet funded successfully.',
        'wallet': {
            'balance': wallet.balance,
            'currency': wallet.currency,
        },
        **result.data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def withdraw_funds(request):
    serializer = WithdrawFundsSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    wallet = services.get_or_create_wallet(request.user)

    try:
        wallet_transaction = services.withdraw_funds(
            wallet,
            serializer.validated_data['amount'],
            serializer.validated_data['phone_number'],
            initiate_mpesa_withdrawal,
        )
    except ValueError as exc:
        return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as exc:
        from requests import RequestException
        if isinstance(exc, RequestException):
            return Response(
                {'detail': 'Unable to contact M-PESA at this time.'},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        from django.core.exceptions import ValidationError
        if isinstance(exc, ValidationError):
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        raise

    wallet.refresh_from_db()
    return Response({
        'message': 'Withdrawal requested successfully. No withdrawal fee was charged.',
        'wallet': {'balance': wallet.balance, 'currency': wallet.currency},
        **WalletTransactionSerializer(wallet_transaction).data,
    }, status=status.HTTP_202_ACCEPTED)