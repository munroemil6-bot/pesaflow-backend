"""
Payments Views

Owner: Myles
Responsibility: API endpoints for M-PESA payment operations

API Endpoints to implement:
# TODO: POST /api/payments/stk-push/
#   - Accepts: phone_number, amount
#   - Returns: merchant_request_id, checkout_request_id
#   - Coordinates with Wallet app (create pending wallet transaction)
#   - Initiates M-PESA STK push
#   - Status: 202 ACCEPTED or 400 BAD REQUEST

# TODO: GET /api/payments/<checkout_request_id>/
#   - Returns: payment status
#   - Calls M-PESA query API
#   - Status: 200 OK

# TODO: POST /api/payments/callback/
#   - Receives M-PESA callback (from Safaricom)
#   - Validates callback signature
#   - Updates MpesaTransaction status
#   - Updates Wallet balance if successful
#   - Status: 200 OK (always for Safaricom)

# TODO: POST /api/payments/simulate/
#   - For sandbox testing
#   - Simulates payment completion
#   - Status: 200 OK

# TODO: GET /api/payments/access-token/
#   - Returns cached or fresh access token
#   - Used internally
#   - Status: 200 OK
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

# TODO: @api_view(['POST']) stk_push view
# TODO: @api_view(['GET']) check_payment_status view
# TODO: @api_view(['POST']) payment_callback view (AllowAny for webhooks)
# TODO: @api_view(['POST']) simulate_payment view (for testing)
# TODO: @api_view(['GET']) get_access_token view (internal use)
