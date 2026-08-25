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
from django.utils.html import format_html
from .models import Beneficiary

@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    # List Display
    list_display = (
        'id', 
        'user', 
        'name', 
        'phone', 
        'email',
        'bank_name',
        'is_active',
        'is_favorite',
        'created_at_display'
    )
    
    # Search Fields
    search_fields = (
        'name', 
        'phone', 
        'email',
        'user__username',
        'user__email',
        'bank_name',
        'account_number'
    )
    
    # Filters
    list_filter = (
        'is_active',
        'is_favorite',
        'account_type',
        'created_at',
        'updated_at'
    )
    
    # Read-only fields
    readonly_fields = (
        'created_at', 
        'updated_at',
        'created_at_display',
        'updated_at_display'
    )
    
    
    # Fieldsets for detailed view
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'name', 'phone', 'email')
        }),
        ('Bank Details', {
            'fields': ('bank_name', 'account_number', 'account_type')
        }),
        ('Additional Information', {
            'fields': ('address', 'notes'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_favorite')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'created_at_display', 'updated_at_display'),
            'classes': ('collapse',)
        }),
    )
    
   