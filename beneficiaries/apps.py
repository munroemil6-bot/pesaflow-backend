

from django.apps import AppConfig


class BeneficiariesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'beneficiaries'
    verbose_name = 'Beneficiaries'

    
    def ready(self):
        """Override ready() to connect signals or perform startup tasks"""
        # Import signals when app is ready
        try:
            import beneficiaries.signals  # noqa
        except ImportError:
            pass