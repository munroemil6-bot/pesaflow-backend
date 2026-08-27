"""Authenticated transaction API endpoints."""

from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import TransactionListSerializer, TransactionSerializer, TransactionSummarySerializer, TransferSerializer
from .services import create_transaction, get_transaction, get_transaction_summary, get_user_transactions


def _filters(request, direction=None):
    return {"status": request.query_params.get("status"), "start_date": request.query_params.get("start_date"),
            "end_date": request.query_params.get("end_date"), "direction": direction}


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    if request.method == "POST":
        serializer = TransferSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        try:
            transfer = create_transaction(request.user, serializer.validated_data["recipient"], serializer.validated_data["amount"], serializer.validated_data["description"])
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TransactionSerializer(transfer).data, status=status.HTTP_201_CREATED)
    return Response(TransactionListSerializer(get_user_transactions(request.user, _filters(request)), many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transaction_detail(request, transaction_id):
    try:
        transfer = get_transaction(request.user, transaction_id)
    except PermissionDenied as exc:
        return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
    return Response(TransactionSerializer(transfer).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transaction_summary(request):
    return Response(TransactionSummarySerializer(get_transaction_summary(request.user)).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def sent_transactions(request):
    return Response(TransactionListSerializer(get_user_transactions(request.user, _filters(request, "sent")), many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def received_transactions(request):
    return Response(TransactionListSerializer(get_user_transactions(request.user, _filters(request, "received")), many=True).data)
