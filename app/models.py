# TODO Myles: Starting imports for SQLAlchemy models and migration metadata.
from ast import Index
from datetime import datetime

from app import db
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import relationship

# DATABASE MODELS: SQLAlchemy classes mapped to PostgreSQL tables.
# TODO Myles: Confirm the shared Base/SQLAlchemy extension and migration workflow.
# TODO Myles: Shared class naming: User, Wallet, Beneficiary, Transaction, MpesaTransaction.
# TODO Mason: class User(db.Model): one User owns one Wallet and many Beneficiaries.
# TODO Mason: User also connects to Transactions through sender_id and recipient_id.
# TODO Naomi: class Beneficiary(db.Model): user_id is a foreign key to User.id.
# TODO Naomi: class Wallet(db.Model): user_id is a unique foreign key to User.id.
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

class Wallet(db.Model):
    __tablename__ = 'wallets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    balance = db.Column(Numeric(12, 2), default=0.00, nullable=False)
    currency = db.Column(db.String(3), default='KES', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class Beneficiary(db.Model):  
    __tablename__ = 'beneficiaries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)

    __table_args__ = (  
        Index('idx_beneficiary_user_id', 'user_id'),
    )
