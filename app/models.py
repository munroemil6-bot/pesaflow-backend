# TODO Myles: Starting imports for SQLAlchemy models and migration metadata.
from datetime import datetime

from app import db
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import relationship

# DATABASE MODELS: SQLAlchemy classes mapped to PostgreSQL tables.
# TODO Myles: Confirm the shared Base/SQLAlchemy extension and migration workflow.
# TODO Myles: Shared class naming: User, Wallet, Beneficiary, Transaction, MpesaTransaction.
# TODO Mason: class User(db.Model): one User owns one Wallet and many Beneficiaries.
# TODO Mason: User also connects to Transactions through sender_id and recipient_id.
# TODO Naomi: class Wallet(db.Model): user_id is a unique foreign key to User.id.
# TODO Naomi: class Beneficiary(db.Model): user_id is a foreign key to User.id.
# TODO Nasra: class Transaction(db.Model): sender_id and recipient_id both reference User.id.
# TODO Myles: class MpesaTransaction(db.Model): transaction_id references Transaction.id.
# TODO Mason: User fields: id, full_name, email, phone, password_hash, role, timestamps.
# TODO Mason: Relationship: User has one Wallet and many Beneficiaries and Transactions.
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