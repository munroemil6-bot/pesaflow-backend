from flask import Flask, jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.schemas import LoginSchema, RegisterSchema, UpdateProfileSchema
from app.services import ServiceError, get_current_user, login_user, register_user, update_profile


def _json_body(schema):
	data = request.get_json(silent=True)
	if not isinstance(data, dict):
		return None, (jsonify({"error": "Request body must be a JSON object."}), 400)
	try:
		return schema.load(data), None
	except ValidationError as error:
		return None, (jsonify({"errors": error.messages}), 400)


def register_routes(app: Flask) -> None:
	"""Register direct @app routes; this project deliberately does not use blueprints."""

	@app.get("/api/health")
	def health_check():
		"""Return a readiness response for local development and monitoring."""
		return jsonify({"status": "ok", "service": "pesaflow-backend"})

	@app.errorhandler(ServiceError)
	def handle_service_error(error):
		return jsonify({"error": error.message}), error.status_code

	# API TYPE: REST over HTTP. Requests and responses use JSON.
	# AUTHENTICATION: Protected routes require a JWT bearer token after login.
	# AUTHORIZATION: Admin routes additionally require the authenticated user role=admin.
	# STATUS CODES: Use 200/201 for success, 400 for invalid input, 401 for missing/invalid
	# STATUS CODES: JWT, 403 for forbidden roles, 404 for missing records, and 409 for conflicts.

	# MASON: AUTHENTICATION AND PROFILE
	# POST /api/auth/register -> JSON {full_name, email, phone, password}; create User and Wallet.
	@app.post("/api/auth/register")
	def register():
		data, error = _json_body(RegisterSchema())
		if error:
			return error
		user = register_user(data)
		return jsonify({"user": user.to_dict()}), 201
	# POST /api/auth/login -> JSON {email, password}; verify password hash and return JWT.
	@app.post("/api/auth/login")
	def login():
		data, error = _json_body(LoginSchema())
		if error:
			return error
		return jsonify(login_user(data))
	# GET /api/auth/me -> JWT; return the authenticated User profile as JSON.
	@app.get("/api/auth/me")
	@jwt_required()
	def auth_me():
		return jsonify({"user": get_current_user().to_dict()})
	# GET /api/users/me -> JWT; return the authenticated User profile as JSON.
	@app.get("/api/users/me")
	@jwt_required()
	def current_profile():
		return jsonify({"user": get_current_user().to_dict()})
	# PUT /api/users/me -> JWT + JSON editable profile fields; update the User record.
	@app.put("/api/users/me")
	@jwt_required()
	def update_current_profile():
		data, error = _json_body(UpdateProfileSchema())
		if error:
			return error
		user = update_profile(get_current_user(), data)
		return jsonify({"user": user.to_dict()})

	# NAOMI: WALLET AND BENEFICIARIES
	# GET /api/wallet -> JWT; return the authenticated user's Wallet and balance.
	# @app.get("/api/wallet") -> Naomi adds handler calling get_wallet().
	# GET /api/wallet/balance -> JWT; return JSON {balance, currency} for the dashboard.
	# @app.get("/api/wallet/balance") -> Naomi adds handler calling get_wallet_balance().
	# GET /api/beneficiaries -> JWT; return only Beneficiary rows owned by current User.
	# @app.get("/api/beneficiaries") -> Naomi adds handler calling get_beneficiaries().
	# POST /api/beneficiaries -> JWT + JSON {name, phone}; create a Beneficiary for current User.
	# @app.post("/api/beneficiaries") -> Naomi adds handler calling create_beneficiary().
	# GET /api/beneficiaries/<id> -> JWT; return the record only when current User owns it.
	# @app.get("/api/beneficiaries/<int:beneficiary_id>") -> Naomi adds detail handler.
	# PUT /api/beneficiaries/<id> -> JWT + JSON fields; update the owned Beneficiary.
	# @app.put("/api/beneficiaries/<int:beneficiary_id>") -> Naomi adds update handler.
	# DELETE /api/beneficiaries/<id> -> JWT; delete the owned Beneficiary and return 204.
	# @app.delete("/api/beneficiaries/<int:beneficiary_id>") -> Naomi adds delete handler.

	# NASRA: TRANSFERS AND ADMIN WORKSPACE
	# POST /api/transactions -> JWT + JSON {recipient_id|phone, amount, description}; create transfer.
	# @app.post("/api/transactions") -> Nasra adds handler calling create_transaction().
	# GET /api/transactions -> JWT; return current user's transactions with optional status/type filters.
	# @app.get("/api/transactions") -> Nasra adds handler calling get_transactions().
	# GET /api/transactions/<id> -> JWT; return a transaction visible to its sender or recipient.
	# @app.get("/api/transactions/<int:transaction_id>") -> Nasra adds detail handler.
	# GET /api/admin/users -> JWT + admin role; return users, balances, counts, and account statuses.
	# @app.get("/api/admin/users") -> Nasra adds handler calling get_admin_users().
	# GET /api/admin/transactions -> JWT + admin role; return searchable platform transactions.
	# @app.get("/api/admin/transactions") -> Nasra adds handler calling get_admin_transactions().
	# GET /api/admin/analytics -> JWT + admin role; return volume, revenue, growth, and active users.
	# @app.get("/api/admin/analytics") -> Nasra adds handler calling get_admin_analytics().

	# MYLES: M-PESA DARAJA INTEGRATION
	# POST /api/mpesa/stk-push -> JWT + JSON {phone_number, amount}; create pending wallet funding.
	# @app.post("/api/mpesa/stk-push") -> Myles adds handler calling initiate_stk_push().
	# POST /api/mpesa/callback -> public Daraja JSON callback; verify and finalize pending funding.
	# @app.post("/api/mpesa/callback") -> Myles adds handler calling handle_mpesa_callback().
	# Never trust STK initiation alone: wallet balance changes only after callback success.
