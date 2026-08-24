from decimal import Decimal

from marshmallow import Schema, ValidationError, fields, validate, validates_schema

# API SCHEMAS: Validate JSON request bodies and serialize JSON responses.
# TODO Naomi: class WalletSchema(Schema), BeneficiarySchema(Schema).
# TODO Nasra: class TransferSchema(Schema), TransactionSchema(Schema).
# TODO Myles: class MpesaSTKSchema(Schema) with phone_number and positive amount fields.
PHONE_PATTERN = r"^(?:\+254|254|0)7\d{8}$"


class RegisterSchema(Schema):
	"""Validate the credentials and identity details required to create an account."""

	full_name = fields.Str(required=True, validate=validate.Length(min=2, max=120))
	email = fields.Email(required=True, validate=validate.Length(max=255))
	phone = fields.Str(required=True, validate=validate.Regexp(PHONE_PATTERN))
	password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8, max=128))

	@validates_schema
	def reject_blank_name(self, data, **kwargs):
		if not data["full_name"].strip():
			raise ValidationError("Full name cannot be blank.", field_name="full_name")


class LoginSchema(Schema):
	"""Accept either the registered email address or phone number plus a password."""

	email = fields.Email(load_default=None, validate=validate.Length(max=255))
	phone = fields.Str(load_default=None, validate=validate.Regexp(PHONE_PATTERN))
	password = fields.Str(required=True, load_only=True, validate=validate.Length(min=1, max=128))

	@validates_schema
	def require_identity(self, data, **kwargs):
		if not data.get("email") and not data.get("phone"):
			raise ValidationError("Provide an email or phone number.", field_name="_schema")
		if data.get("email") and data.get("phone"):
			raise ValidationError(
				"Provide either email or phone, not both.", field_name="_schema"
			)


class UpdateProfileSchema(Schema):
	"""Validate the safe, editable parts of an authenticated user's profile."""

	full_name = fields.Str(validate=validate.Length(min=2, max=120))
	email = fields.Email(validate=validate.Length(max=255))
	phone = fields.Str(validate=validate.Regexp(PHONE_PATTERN))

	@validates_schema
	def require_change(self, data, **kwargs):
		if not data:
			raise ValidationError("Provide at least one profile field.", field_name="_schema")
		if "full_name" in data and not data["full_name"].strip():
			raise ValidationError("Full name cannot be blank.", field_name="full_name")


class MpesaSTKSchema(Schema):
	phone_number = fields.String(required=True, validate=validate.Length(min=9, max=30))
	amount = fields.Decimal(
		required=True,
		as_string=True,
		validate=validate.Range(min=Decimal("0.01")),
	)


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
