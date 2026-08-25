"""
Transactions Views

Owner: Nasra
Responsibility: API endpoints for transaction operations

API Endpoints to implement:
# TODO: GET /api/transactions/
#   - Returns: list of transactions (sent + received)
#   - Filters: date range, status
#   - Pagination: supported
#   - Status: 200 OK

# TODO: GET /api/transactions/<id>/
#   - Returns: transaction details
#   - Status: 200 OK or 404 NOT FOUND

# TODO: POST /api/transactions/
#   - Accepts: recipient_id (or recipient_phone), amount, description
#   - Returns: created transaction
#   - Coordinates with Wallet app (check balance)
#   - Coordinates with Payments app (if M-PESA)
#   - Status: 201 CREATED or 400 BAD REQUEST

# TODO: GET /api/transactions/summary/
#   - Returns: user's transaction summary
#   - Include: total sent, total received, transaction count
#   - Status: 200 OK

# TODO: GET /api/transactions/sent/
#   - Returns: only sent transactions
#   - Status: 200 OK

# TODO: GET /api/transactions/received/
#   - Returns: only received transactions
#   - Status: 200 OK
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# TODO: @api_view(['GET', 'POST']) transaction_list view
# TODO: @api_view(['GET']) transaction_detail view
# TODO: @api_view(['GET']) transaction_summary view
# TODO: @api_view(['GET']) sent_transactions view
# TODO: @api_view(['GET']) received_transactions view
