"""
URL configuration for the PesaFlow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/

Each app has its own urls.py file that handles its specific routes.

ROUTING STRUCTURE:
    - api/accounts/      → Mason (User Authentication)
    - api/wallet/        → Naomi (Wallet Management)
    - api/transactions/  → Nasra (Money Transfers)
    - api/payments/      → Myles (M-PESA Integration)
    - api/beneficiaries/ → Naomi (Saved Recipients)
    - api/admin-dashboard/ → Nasra (Admin Operations)
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    # Mason: User Authentication & Accounts
    path("api/accounts/", include("accounts.urls")),

    # Naomi: Wallet Management
    path("api/wallet/", include("wallet.urls")),

    # Naomi: Beneficiary Management
    path("api/beneficiaries/", include("beneficiaries.urls")),

    # Nasra: Transaction History & Transfers
    path("api/transactions/", include("transactions.urls")),

    # Myles: M-PESA Payments
    path("api/payments/", include("payments.urls")),

    # Nasra: Admin Dashboard & Analytics
    path("api/admin-dashboard/", include("admin_dashboard.urls")),
]
