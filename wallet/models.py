"""
Wallet Models

Owner: Naomi
Responsibility: Wallet model and related database tables

Models to implement:
# TODO: Wallet model
#   - user (OneToOneField to User, cascade delete)
#   - balance (DecimalField, precision 12.2)
#   - currency (CharField default='KES')
#   - created_at (DateTimeField auto_now_add)
#   - updated_at (DateTimeField auto_now)
#   - Methods: get_balance(), add_funds(), deduct_funds(), to_dict()

# TODO: WalletTransaction model (optional, for detailed history)
#   - wallet (ForeignKey)
#   - amount
#   - transaction_type (credit, debit)
#   - description
#   - balance_before
#   - balance_after
#   - created_at
"""

from django.db import models

# TODO: Create Wallet model linked to User
# TODO: Create WalletTransaction model for audit trail
