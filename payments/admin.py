"""
Payments Admin

Owner: Myles
Responsibility: Django admin interface for payment management

Admin configuration to implement:
# TODO: MpesaTransactionAdmin
#   - List display: id, phone, amount, status, merchant_request_id, completed_at
#   - Search: phone, checkout_request_id, mpesa_receipt_number
#   - Filter: status, created_at, completed_at
#   - Read-only: merchant_request_id, checkout_request_id, created_at, updated_at
#   - Actions: mark_as_completed, mark_as_failed

# TODO: PaymentAccessTokenAdmin (if implemented)
#   - List display: expires_at, created_at
#   - Read-only: token, created_at
"""

from django.contrib import admin

# TODO: Register MpesaTransaction model with MpesaTransactionAdmin
