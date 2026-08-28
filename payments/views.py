

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import requests

from .serializers import MpesaSTKSerializer
from .services import initiate_stk_push


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

# TODO: @api_view(['GET']) check_payment_status view
# TODO: @api_view(['POST']) payment_callback view (AllowAny for webhooks)
# TODO: @api_view(['POST']) simulate_payment view (for testing)
# TODO: @api_view(['GET']) get_access_token view (internal use)
