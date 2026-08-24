# TODO Myles: Starting imports for service-layer database access and Daraja HTTP calls.
import re

from flask_jwt_extended import create_access_token, get_jwt_identity
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class ServiceError(Exception):
	"""A business-rule error that routes can safely return as JSON."""

	def __init__(self, message, status_code):
		super().__init__(message)
		self.message = message
		self.status_code = status_code

# TODO Team: Import db/models inside the service implementation to avoid circular imports.
# SERVICE LAYER: Business rules, database operations, and external API clients live here.
# AUTHENTICATION AND PROFILE: Mason implements register_user, login_user, update_profile.
def _normalise_phone(phone):
	"""Store Kenyan mobile numbers in one canonical +254XXXXXXXXX form."""
	phone = re.sub(r"[\s-]", "", phone)
	if phone.startswith("0"):
		return f"+254{phone[1:]}"
	if phone.startswith("254"):
		return f"+{phone}"
	return phone


def _normalise_registration_data(data):
	data = data.copy()
	data["full_name"] = data["full_name"].strip()
	data["email"] = data["email"].strip().lower()
	data["phone"] = _normalise_phone(data["phone"])
	return data


def _identity_conflict(email=None, phone=None, exclude_user_id=None):
	from app.models import User

	query = User.query
	if exclude_user_id is not None:
		query = query.filter(User.id != exclude_user_id)
	if email and query.filter(func.lower(User.email) == email.lower()).first():
		return "email"
	if phone and query.filter(User.phone == phone).first():
		return "phone"
	return None


def register_user(data):
	"""Create a user and its empty wallet in one database transaction."""
	from app.models import User, Wallet

	data = _normalise_registration_data(data)
	conflict = _identity_conflict(data["email"], data["phone"])
	if conflict:
		raise ServiceError(f"An account with that {conflict} already exists.", 409)

	user = User(
		full_name=data["full_name"],
		email=data["email"],
		phone=data["phone"],
		password_hash=generate_password_hash(data["password"]),
	)
	db.session.add(user)
	# Assign through the relationship so Naomi's Wallet model remains the source
	# of truth for its defaults (balance and currency).
	user.wallet = Wallet()
	try:
		db.session.commit()
	except Exception:
		db.session.rollback()
		raise
	return user


def login_user(data):
	"""Validate credentials and return a JWT access token and public profile."""
	from app.models import User

	user = None
	if data.get("email"):
		user = User.query.filter(func.lower(User.email) == data["email"].strip().lower()).first()
	else:
		user = User.query.filter_by(phone=_normalise_phone(data["phone"])).first()
	if not user or not check_password_hash(user.password_hash, data["password"]):
		raise ServiceError("Invalid email/phone or password.", 401)
	if not user.is_active:
		raise ServiceError("This account is inactive.", 403)

	return {
		"access_token": create_access_token(
			identity=str(user.id), additional_claims={"role": user.role}
		),
		"user": user.to_dict(),
	}


def get_current_user():
	"""Fetch the user represented by the verified JWT identity."""
	from app.models import User

	identity = get_jwt_identity()
	try:
		user_id = int(identity)
	except (TypeError, ValueError):
		raise ServiceError("Invalid authentication identity.", 401)
	user = db.session.get(User, user_id)
	if not user or not user.is_active:
		raise ServiceError("User account was not found or is inactive.", 401)
	return user


def update_profile(user, data):
	"""Apply approved profile changes after checking identity uniqueness."""
	updates = data.copy()
	if "full_name" in updates:
		updates["full_name"] = updates["full_name"].strip()
	if "email" in updates:
		updates["email"] = updates["email"].strip().lower()
	if "phone" in updates:
		updates["phone"] = _normalise_phone(updates["phone"])

	conflict = _identity_conflict(
		updates.get("email"), updates.get("phone"), exclude_user_id=user.id
	)
	if conflict:
		raise ServiceError(f"An account with that {conflict} already exists.", 409)
	for field, value in updates.items():
		setattr(user, field, value)
	try:
		db.session.commit()
	except Exception:
		db.session.rollback()
		raise
	return user
# WALLET AND BENEFICIARIES: Naomi implements wallet/balance and beneficiary CRUD services.
# TODO Naomi: def get_wallet(user), def get_wallet_balance(user), beneficiary CRUD functions.
# TRANSACTIONS AND ADMIN: Nasra implements transfer, history, detail, and admin services.
# TODO Nasra: def create_transaction(user, data), def get_transactions(user, filters), admin functions.
# M-PESA API TYPE: Myles implements HTTPS requests to Safaricom Daraja REST endpoints.
# TODO Myles: get_mpesa_access_token uses Daraja OAuth credentials from environment config.
# TODO Myles: def get_mpesa_access_token(), def initiate_stk_push(user, phone_number, amount).
# TODO Myles: initiate_stk_push validates input, calls Daraja, and records status=pending.
# TODO Myles: handle_mpesa_callback finds the linked transaction and reads callback results.
# TODO Myles: def handle_mpesa_callback(data) returns a JSON-safe acknowledgement to Daraja.
# TODO Myles: Mark success or failure idempotently; update Wallet only after confirmed success.
# TODO Team: Keep routes thin, return service results, and make external calls mockable in tests.
