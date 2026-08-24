# TODO Myles: Starting imports for Marshmallow request validation and JSON serialization.
from marshmallow import Schema, fields, validate

# API SCHEMAS: Validate JSON request bodies and serialize JSON responses.
# TODO Mason: class RegisterSchema(Schema), LoginSchema(Schema), UpdateProfileSchema(Schema).
# TODO Naomi: class WalletSchema(Schema), BeneficiarySchema(Schema).
# TODO Nasra: class TransferSchema(Schema), TransactionSchema(Schema).
# TODO Myles: class MpesaSTKSchema(Schema) with phone_number and positive amount fields.
# TODO Mason: RegisterSchema for POST /api/auth/register: identity and password input.
# TODO Mason: LoginSchema for POST /api/auth/login: email/phone and password input.
# TODO Mason: UpdateProfileSchema for PUT /api/users/me: editable profile fields.
# TODO Naomi: WalletSchema for GET /api/wallet and GET /api/wallet/balance responses.
# TODO Naomi: BeneficiarySchema for beneficiary create, update, list, and detail payloads.
# TODO Nasra: TransferSchema for POST /api/transactions transfer input and money rules.
# TODO Nasra: TransactionSchema for transaction list and detail response payloads.
# TODO Myles: MpesaSTKSchema for POST /api/mpesa/stk-push: phone_number and amount.
# TODO Team: Return consistent JSON validation errors and never serialize secrets.

class WalletSchema(Schema):
    balance = fields.Decimal(as_string=True)
    currency = fields.String(validate=validate.Length(equal=3))
    user_id = fields.Integer()
