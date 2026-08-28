
from django.urls import path

from . import views

app_name = 'transactions'

urlpatterns = [
    path('', views.transaction_list, name='transaction-list'),
    path('summary/', views.transaction_summary, name='transaction-summary'),
    path('sent/', views.sent_transactions, name='sent-transactions'),
    path('received/', views.received_transactions, name='received-transactions'),
    path('<int:transaction_id>/', views.transaction_detail, name='transaction-detail'),
]
