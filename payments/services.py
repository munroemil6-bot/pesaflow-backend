"""
Payments Services

Owner: Myles
Responsibility: Daraja API integration and M-PESA processing

Service functions to implement:
# TODO: get_access_token()
#   - Make OAuth2 request to Daraja
#   - Use consumer_key and consumer_secret
#   - Cache token with expiration
#   - Return access token

# TODO: initiate_stk_push(phone, amount, account_reference, description)
#   - Get access token (call get_access_token())
#   - Prepare STK push request payload
#   - Make request to Daraja
#   - Create MpesaTransaction record with PENDING status
#   - Return merchant_request_id and checkout_request_id
#   - Coordinate with Wallet app to record pending transaction

# TODO: handle_mpesa_callback(callback_data)
#   - Extract data from callback JSON
#   - Validate signature
#   - Extract checkout_request_id
#   - Extract result code and description
#   - Find MpesaTransaction by checkout_request_id
#   - If result_code == 0 (success):
#       - Update status to COMPLETED
#       - Extract receipt number
#       - Update wallet balance (call wallet service)
#       - Return success
#   - Else:
#       - Update status to FAILED
#       - Log error
#       - Return failure

# TODO: query_payment_status(checkout_request_id)
#   - Get access token
#   - Query M-PESA for payment status
#   - Update local MpesaTransaction record
#   - Return current status

# TODO: validate_callback_signature(callback_data, timestamp, signature)
#   - Reconstruct signature
#   - Compare with provided signature
#   - Return boolean

# TODO: generate_timestamp()
#   - Return current timestamp in Daraja format

# TODO: simulate_payment(checkout_request_id)
#   - For sandbox testing
#   - Call Daraja simulation endpoint
#   - Return result
"""
import base64
import requests
from django.conf import settings


def get_mpesa_access_token():
    credentials = (
        f"{settings.MPESA_CONSUMER_KEY}:"
        f"{settings.MPESA_CONSUMER_SECRET}"
    )

    encoded_credentials = base64.b64encode(
        credentials.encode()
    ).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }

    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()["access_token"]

# TODO: Service class or functions for M-PESA integration
# TODO: Implement Daraja OAuth2 flow
# TODO: Handle STK push and callbacks
# TODO: Query payment status
# TODO: Coordinate with transactions and wallet apps
