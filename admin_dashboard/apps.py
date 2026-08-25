"""
Admin Dashboard App Configuration

Owner: Nasra
Responsibility: Admin panel API endpoints and analytics

This app handles:
- Admin-only data retrieval
- User management
- Transaction monitoring
- Wallet analytics
- System statistics
- Profit calculations
"""

from django.apps import AppConfig


class AdminDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_dashboard'
    verbose_name = 'Admin Dashboard'
