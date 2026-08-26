"""
Wallet URLs

Owner: Naomi
Responsibility: Route URLs to wallet views

URL patterns to implement:
# TODO: path('', views.wallet_detail)
# TODO: path('balance/', views.wallet_balance)
# TODO: path('analytics/', views.wallet_analytics)
# TODO: path('history/', views.wallet_history)
# TODO: path('add-funds/', views.add_funds)
"""

from django.urls import path

from admin_dashboard import views

app_name = 'wallet'


urlpatterns = [
    path('', views.wallet_detail, name='wallet-detail'),
    path('balance/', views.wallet_balance, name='wallet-balance'),
    path('analytics/', views.wallet_analytics, name='wallet-analytics'),
    path('history/', views.wallet_history, name='wallet-history'),
    path('add-funds/', views.add_funds, name='wallet-add-funds'),
]