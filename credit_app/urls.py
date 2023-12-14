# credit_app/urls.py
from django.urls import path
from .views import CustomerListCreateView, LoanListCreateView, EligibilityCheckView, CreateLoanView, ViewLoanDetailView, ViewLoansByCustomerView
from .views import RegistrationView, LoanApplicationView
urlpatterns = [
    path('customers/', CustomerListCreateView.as_view(), name='customer-list-create'),
    path('loans/', LoanListCreateView.as_view(), name='loan-list-create'),
     path('check-eligibility/', EligibilityCheckView.as_view(), name='check-eligibility'),
    path('create-loan/', CreateLoanView.as_view(), name='create-loan'),
    path('view-loan/<int:pk>/', ViewLoanDetailView.as_view(), name='view-loan-detail'),
    path('view-loans/<int:customer_id>/', ViewLoansByCustomerView.as_view(), name='view-loans-by-customer'),
      path('register/', RegistrationView.as_view(), name='register'),
    path('apply-loan/', LoanApplicationView.as_view(), name='apply-loan'),
]
