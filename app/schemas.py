# TODO Myles: Starting imports for Marshmallow request validation and JSON serialization.
from decimal import Decimal

from marshmallow import Schema, fields, validate

# API SCHEMAS: Validate JSON request bodies and serialize JSON responses.
# TODO Mason: class RegisterSchema(Schema), LoginSchema(Schema), UpdateProfileSchema(Schema).
# TODO Naomi: class WalletSchema(Schema), BeneficiarySchema(Schema).
# TODO Nasra: class TransferSchema(Schema), TransactionSchema(Schema).


class MpesaSTKSchema(Schema):
	phone_number = fields.String(required=True, validate=validate.Length(min=9, max=30))
	amount = fields.Decimal(
		required=True,
		as_string=True,
		validate=validate.Range(min=Decimal("0.01")),
	)

# TODO Mason: RegisterSchema for POST /api/auth/register: identity and password input.
# TODO Mason: LoginSchema for POST /api/auth/login: email/phone and password input.
# TODO Mason: UpdateProfileSchema for PUT /api/users/me: editable profile fields.
# TODO Naomi: WalletSchema for GET /api/wallet and GET /api/wallet/balance responses.
# TODO Naomi: BeneficiarySchema for beneficiary create, update, list, and detail payloads.
# TODO Nasra: TransferSchema for POST /api/transactions transfer input and money rules.
# TODO Nasra: TransactionSchema for transaction list and detail response payloads.
# TODO Myles: MpesaSTKSchema for POST /api/mpesa/stk-push: phone_number and amount.
# TODO Team: Return consistent JSON validation errors and never serialize secrets.