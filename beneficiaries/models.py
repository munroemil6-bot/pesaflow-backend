"""
Beneficiaries Models

Owner: Naomi
Responsibility: Beneficiary model and related database tables

Models to implement:
# TODO: Beneficiary model
#   - user (ForeignKey to User, cascade delete)
#   - name (CharField)
#   - phone (CharField)
#   - created_at (DateTimeField auto_now_add)
#   - updated_at (DateTimeField auto_now)
#   - Meta: unique_together on (user, phone) to prevent duplicates
#   - Methods: to_dict()
"""

from django.db import models

# TODO: Create Beneficiary model linked to User
# TODO: Add validation for phone number format
