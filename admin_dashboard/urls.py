

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
