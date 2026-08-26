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
    # List Display
    list_display = (
        'id',
        'user',
        'name',
        'phone',
        'created_at',
    )
    
    # Search Fields
    search_fields = (
        'name',
        'phone',
        'user__email',
    )
    
    # Filters
    list_filter = (
        'created_at',
        'updated_at'
    )
    
    # Read-only fields
    readonly_fields = (
        'created_at',
        'updated_at',
    )
    
    
    # Fieldsets for detailed view
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'name', 'phone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
   