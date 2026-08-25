"""
Beneficiaries App Configuration

Owner: Naomi
Responsibility: Beneficiary (saved recipients) management

This app handles:
- Adding beneficiaries
- Viewing beneficiaries
- Updating beneficiaries
- Deleting beneficiaries
- Quick access for transfers
"""

from django.apps import AppConfig


class BeneficiariesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'beneficiaries'
    verbose_name = 'Beneficiaries'
