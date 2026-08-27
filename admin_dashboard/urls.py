"""
Admin Dashboard URLs

Owner: Nasra
Responsibility: Route URLs to admin dashboard views

URL patterns to implement:
# TODO: path('summary/', views.dashboard_summary)
# TODO: path('users/', views.user_list)
# TODO: path('users/<int:user_id>/', views.user_detail)
# TODO: path('transactions/', views.transaction_list)
# TODO: path('wallets/', views.wallet_list)
# TODO: path('analytics/', views.analytics)
# TODO: path('revenue/', views.revenue_report)
# TODO: path('top-users/', views.top_users)
# TODO: path('payment-status/', views.payment_statistics)

Note: All endpoints require admin authentication
"""

from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('summary/', views.dashboard_summary, name='summary'),
    path('users/', views.user_list, name='users'),
    path('users/<int:user_id>/', views.user_detail, name='user-detail'),
    path('transactions/', views.transaction_list, name='transactions'),
    path('wallets/', views.wallet_list, name='wallets'),
    path('analytics/', views.analytics, name='analytics'),
    path('revenue/', views.revenue_report, name='revenue'),
    path('top-users/', views.top_users, name='top-users'),
    path('payment-status/', views.payment_statistics, name='payment-statistics'),
]
