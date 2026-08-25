"""
Transactions Admin

Owner: Nasra
Responsibility: Django admin interface for transaction management

Admin configuration to implement:
# TODO: TransactionAdmin
#   - List display: id, sender, recipient, amount, status, created_at
#   - Search: reference, sender__email, recipient__email
#   - Filter: status, created_at
#   - Read-only: created_at, updated_at, reference
#   - List filter: status, date created
"""

from django.contrib import admin

# TODO: Register Transaction model with TransactionAdmin
