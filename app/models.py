# TODO Myles: Starting imports for SQLAlchemy models and migration metadata.
from datetime import datetime

from app import db
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import relationship

# DATABASE MODELS: SQLAlchemy classes mapped to PostgreSQL tables.
# TODO Myles: Confirm the shared Base/SQLAlchemy extension and migration workflow.
# TODO Myles: Shared class naming: User, Wallet, Beneficiary, Transaction, MpesaTransaction.
# TODO Naomi: class Wallet(db.Model): user_id is a unique foreign key to User.id.
# TODO Naomi: class Beneficiary(db.Model): user_id is a foreign key to User.id.
# TODO Nasra: class Transaction(db.Model): sender_id and recipient_id both reference User.id.
# TODO Myles: class MpesaTransaction(db.Model): transaction_id references Transaction.id.
class User(db.Model):
	"""An account that can own a wallet, beneficiaries, and transactions."""

	__tablename__ = "users"

	id = db.Column(db.Integer, primary_key=True)
	full_name = db.Column(db.String(120), nullable=False)
	email = db.Column(db.String(255), nullable=False, unique=True, index=True)
	phone = db.Column(db.String(20), nullable=False, unique=True, index=True)
	password_hash = db.Column(db.String(255), nullable=False)
	role = db.Column(db.String(20), nullable=False, default="user", server_default="user")
	is_active = db.Column(db.Boolean, nullable=False, default=True, server_default="1")
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	updated_at = db.Column(
		db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
	)

	# These string references deliberately keep this shared model independent of the
	# implementation order of the wallet and transaction modules.
	wallet = relationship(
		"Wallet", back_populates="user", uselist=False, cascade="all, delete-orphan"
	)
	beneficiaries = relationship(
		"Beneficiary", back_populates="user", cascade="all, delete-orphan"
	)
	sent_transactions = relationship(
		"Transaction",
		foreign_keys="Transaction.sender_id",
		back_populates="sender",
	)
	received_transactions = relationship(
		"Transaction",
		foreign_keys="Transaction.recipient_id",
		back_populates="recipient",
	)

	def to_dict(self):
		"""Return the public account representation; never expose password_hash."""
		return {
			"id": self.id,
			"full_name": self.full_name,
			"email": self.email,
			"phone": self.phone,
			"role": self.role,
			"is_active": self.is_active,
			"created_at": self.created_at.isoformat() if self.created_at else None,
			"updated_at": self.updated_at.isoformat() if self.updated_at else None,
		}


class MpesaTransaction(db.Model):
	__tablename__ = "mpesa_transactions"

	id = db.Column(db.Integer, primary_key=True)
	transaction_id = db.Column(
		db.Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, unique=True
	)
	phone = db.Column(String(30), nullable=False)
	amount = db.Column(Numeric(18, 2), nullable=False)
	merchant_request_id = db.Column(String(100), nullable=True, index=True)
	checkout_request_id = db.Column(String(100), nullable=True, unique=True, index=True)
	receipt = db.Column(String(100), nullable=True, unique=True)
	result_code = db.Column(db.Integer, nullable=True)
	result_description = db.Column(String(255), nullable=True)
	status = db.Column(
		String(20), nullable=False, default="pending", server_default="pending", index=True
	)
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	updated_at = db.Column(
		db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
	)

	transaction = relationship("Transaction", back_populates="mpesa_transaction")


# TODO Naomi: Wallet fields: id, user_id, balance, currency, timestamps.
# TODO Naomi: Relationship: Wallet belongs to exactly one User through user_id.
# TODO Naomi: Beneficiary fields: id, user_id, name, phone, created_at.
# TODO Naomi: Relationship: User has many Beneficiaries; delete behavior must be decided.
# TODO Nasra: Transaction fields: sender_id, recipient_id, amount, fee, total_amount,
# TODO Nasra: status, reference, description, and created_at.
# TODO Nasra: Relationships: Transaction links sender and recipient to User records.
# TODO Myles: MpesaTransaction fields: transaction_id, phone, amount, request IDs,
# TODO Myles: receipt, result code/description, status, and timestamps.
# TODO Myles: Relationship: each MpesaTransaction belongs to one Transaction.
# TODO Team: Add constraints, indexes, decimal money types, and migration-ready metadata.
