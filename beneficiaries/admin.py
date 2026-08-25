"""
Beneficiaries Admin

Owner: Naomi
Responsibility: Django admin interface for beneficiary management

Admin configuration to implement:
# TODO: BeneficiaryAdmin
#   - List display: id, user, name, phone, created_at
#   - Search: name, phone, user__email
#   - Filter: created_at
#   - Read-only: created_at, updated_at
"""



# TODO: Register Beneficiary model with BeneficiaryAdmin

from django.contrib import admin
from .models import Beneficiary  

@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    # List display configuration
    list_display = ('id', 'user', 'name', 'phone', 'created_at')
    
    # Search fields
    search_fields = ('name', 'phone', 'user__email')
    
    # Filter configuration
    list_filter = ('created_at',)
    
    # Read-only fields
    readonly_fields = ('created_at', 'updated_at')
    
    # Optional: Customize ordering
    ordering = ('-created_at',)
    
    