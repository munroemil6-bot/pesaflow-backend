"""
Payments Models

Owner: Myles
Responsibility: M-PESA payment model and related database tables

Models to implement:
# TODO: MpesaTransaction model
#   - transaction (OneToOneField or ForeignKey to Transaction, optional)
#   - phone (CharField - customer phone)
#   - amount (DecimalField)
#   - merchant_request_id (CharField, unique)
#   - checkout_request_id (CharField, unique)
#   - mpesa_receipt_number (CharField, unique, optional)
#   - result_code (IntegerField, optional)
#   - result_description (CharField, optional)
#   - status (CharField: pending, completed, failed, expired, cancelled)
#   - initiated_at (DateTimeField auto_now_add)
#   - completed_at (DateTimeField, optional)
#   - created_at (DateTimeField auto_now_add)
#   - updated_at (DateTimeField auto_now)
#   - Meta: indexes on phone, checkout_request_id, status, created_at
#   - Methods: to_dict()

# TODO: PaymentAccessToken model (cache M-PESA tokens)
#   - token (TextField)
#   - expires_at (DateTimeField)
#   - created_at (DateTimeField auto_now_add)
"""

from django.db import models

# TODO: Create MpesaTransaction model
# TODO: Create PaymentAccessToken model for token caching
# TODO: Add necessary indexes and fields
