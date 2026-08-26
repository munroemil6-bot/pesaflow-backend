"""
Beneficiaries URLs

Owner: Naomi
Responsibility: Route URLs to beneficiary views

URL patterns to implement:
# TODO: path('', views.beneficiary_list)
# TODO: path('<int:beneficiary_id>/', views.beneficiary_detail)
"""

from django.urls import path
from . import views

app_name = 'beneficiaries'

urlpatterns = [
    # List and Create
    path('', views.BeneficiaryListCreateView.as_view(), name='list-create'),
    
    # Detail, Update, Delete
    path('<int:id>/', views.BeneficiaryDetailView.as_view(), name='detail'),
]