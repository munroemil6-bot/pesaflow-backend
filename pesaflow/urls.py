
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from django.http import JsonResponse


def api_root(request):
    """Return a small public readiness response for local setup checks."""
    return JsonResponse({
        "status": "ok",
        "service": "pesaflow-backend",
        "api_types": [
            "accounts",
            "wallet",
            "beneficiaries",
            "transactions",
            "payments",
            "admin-dashboard",
        ],
    })


def home(request):
    """Send local developers to the Django Admin sign-in page."""
    return redirect("admin:index")

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("api/", api_root, name="api-root"),

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
