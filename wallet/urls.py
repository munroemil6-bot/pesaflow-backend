from django.urls import path

from . import views

app_name = 'wallet'


urlpatterns = [
    path('', views.wallet_detail, name='wallet-detail'),
    path('balance/', views.wallet_balance, name='wallet-balance'),
    path('analytics/', views.wallet_analytics, name='wallet-analytics'),
    path('history/', views.wallet_history, name='wallet-history'),
    path('add-funds/', views.add_funds, name='wallet-add-funds'),
]