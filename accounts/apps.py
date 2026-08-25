"""
Accounts App Configuration

Owner: Mason
Responsibility: User authentication and account management

This app handles:
- User registration
- User login
- JWT token generation and refresh
- User profile management
- Authentication middleware
"""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Accounts & Authentication'
