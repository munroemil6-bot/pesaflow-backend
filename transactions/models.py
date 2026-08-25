"""
Transactions Models

Owner: Nasra
Responsibility: Transaction model and related database tables

Models to implement:
# TODO: Transaction model
#   - sender (ForeignKey to User)
#   - recipient (ForeignKey to User)
#   - amount (DecimalField)
#   - fee (DecimalField)
#   - total_amount (DecimalField = amount + fee)
#   - status (CharField: pending, completed, failed)
#   - reference (CharField, unique)
#   - description (TextField, optional)
#   - created_at (DateTimeField auto_now_add)
#   - updated_at (DateTimeField auto_now)
#   - Meta: indexes on sender, recipient, status, created_at
#   - Methods: to_dict()
"""

from django.db import models

# TODO: Create Transaction model with sender and recipient relationships
# TODO: Add indexed fields for efficient querying
# TODO: Add status tracking (pending, completed, failed, cancelled)
