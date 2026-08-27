"""
Transactions URLs

Owner: Nasra
Responsibility: Route URLs to transaction views

URL patterns to implement:
# TODO: path('', views.transaction_list)
# TODO: path('<int:transaction_id>/', views.transaction_detail)
# TODO: path('summary/', views.transaction_summary)
# TODO: path('sent/', views.sent_transactions)
# TODO: path('received/', views.received_transactions)
"""

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
