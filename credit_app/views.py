from rest_framework import generics
from rest_framework.response import Response
from .models import Customer, Loan
from .serializers import (
    EligibilityCheckSerializer,
    CreateLoanSerializer,
    CustomerSerializer,
    LoanApplicationSerializer,
    LoanSerializer,
    ViewLoanSerializer,
    ViewLoansSerializer,
    RegistrationSerializer,
)
from rest_framework import status
from rest_framework.views import APIView
from django.db.models import Sum
from .models import Customer, Loan



class ViewLoansView(APIView):
    def get(self, request, customer_id, *args, **kwargs):
        try:
            # Fetch all current loans for the given customer
            loans = Loan.objects.filter(customer_id=customer_id, end_date__isnull=True)

            # Serialize the list of loans
            serializer = ViewLoansSerializer(loans, many=True)

            # Respond with the results
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Loan.DoesNotExist:
            # If customer has no current loans, respond with an empty list
            return Response([], status=status.HTTP_200_OK)




class ViewLoanView(APIView):
    def get(self, request, loan_id, *args, **kwargs):
        try:
            # Fetch loan data
            loan = Loan.objects.get(pk=loan_id)

            # Serialize loan and customer data
            serializer = ViewLoanSerializer(loan)

            # Respond with the results
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Loan.DoesNotExist:
            # If loan does not exist, respond with an error message
            response_data = {
                "error": "Loan not found with the provided loan_id."
            }
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)





class CreateLoanView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = CreateLoanSerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            loan_amount = serializer.validated_data['loan_amount']
            interest_rate = serializer.validated_data['interest_rate']
            tenure = serializer.validated_data['tenure']

            # Fetch customer data
            customer = Customer.objects.get(pk=customer_id)

            # Check loan eligibility based on credit score
            eligibility_data = self.check_loan_eligibility(customer, loan_amount, interest_rate, tenure)

            if eligibility_data['approval']:
                # If eligible, create a new loan
                new_loan = Loan.objects.create(
                    customer=customer,
                    loan_amount=loan_amount,
                    interest_rate=eligibility_data['corrected_interest_rate'],
                    tenure=tenure,
                    monthly_repayment=eligibility_data['monthly_installment']
                )

                # Respond with the results
                response_data = {
                    "loan_id": new_loan.id,
                    "customer_id": customer.id,
                    "loan_approved": True,
                    "message": "Loan approved successfully",
                    "monthly_installment": eligibility_data['monthly_installment']
                }
            else:
                # If not eligible, respond with the appropriate message
                response_data = {
                    "loan_id": None,
                    "customer_id": customer.id,
                    "loan_approved": False,
                    "message": "Loan not approved. " + eligibility_data['message'],
                    "monthly_installment": 0
                }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def check_loan_eligibility(self, customer, loan_amount, interest_rate, tenure):
        # Implement the logic to check loan eligibility
        # You can reuse the logic from the /check-eligibility endpoint or customize it based on your needs
        # Adjust the logic based on your requirements

        # Placeholder data for demonstration purposes
        approval = True
        corrected_interest_rate = min(interest_rate, 16.0)
        monthly_installment = 2000.0
        message = ""

        return {
            "approval": approval,
            "corrected_interest_rate": corrected_interest_rate,
            "monthly_installment": monthly_installment,
            "message": message
        }





class EligibilityCheckView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = EligibilityCheckSerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            loan_amount = serializer.validated_data['loan_amount']
            interest_rate = serializer.validated_data['interest_rate']
            tenure = serializer.validated_data['tenure']

            # Fetch customer and loan data
            customer = Customer.objects.get(pk=customer_id)
            current_year_loans = Loan.objects.filter(
                customer=customer, start_date__year=2023  # Assuming current year is 2023
            )
            current_emi_sum = current_year_loans.aggregate(Sum('monthly_repayment'))['monthly_repayment__sum'] or 0

            # Calculate credit score based on the provided components
            credit_score = self.calculate_credit_score(customer, current_year_loans)

            # Check loan eligibility based on credit score
            if credit_score > 50:
                approval = True
            elif 50 >= credit_score > 30 and interest_rate > 12:
                approval = True
            elif 30 >= credit_score > 10 and interest_rate > 16:
                approval = True
            else:
                approval = False

            # Check sum of current EMIs
            if current_emi_sum > 0.5 * customer.monthly_salary:
                approval = False

            # Correct interest rate if needed
            corrected_interest_rate = min(interest_rate, 16.0)  # Assuming 16% is the lowest slab

            # Respond with the results
            response_data = {
                "customer_id": customer.id,
                "approval": approval,
                "interest_rate": interest_rate,
                "corrected_interest_rate": corrected_interest_rate,
                "tenure": tenure,
                "monthly_installment": self.calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def calculate_credit_score(cls, customer, loans):
        # Implement the logic to calculate credit score
        # Example: Sum of past loans paid on time, number of loans taken, etc.
        # Adjust based on your requirements
        return 60  # Placeholder value, replace with actual calculation

    @staticmethod
    def calculate_monthly_installment(loan_amount, interest_rate, tenure):
        # Implement the logic to calculate monthly installment
        # Example: Use the loan formula
        # Adjust based on your requirements
        return 0  # Placeholder value, replace with actual calculation





class RegistrationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Calculate approved limit
            monthly_salary = serializer.validated_data['monthly_income']
            approved_limit = round(36 * monthly_salary, -5)  # Round to nearest lakh

            # Create a new customer
            customer = Customer.objects.create(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                age=serializer.validated_data['age'],
                monthly_salary=monthly_salary,
                approved_limit=approved_limit,
                phone_number=serializer.validated_data['phone_number']
            )

            # Return response
            response_data = {
                "customer_id": customer.id,
                "name": f"{customer.first_name} {customer.last_name}",
                "age": customer.age,
                "monthly_income": customer.monthly_salary,
                "approved_limit": customer.approved_limit,
                "phone_number": customer.phone_number
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






# in views.py
class LoanApplicationView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoanApplicationSerializer(data=request.data)
        if serializer.is_valid():
            # Process loan application and perform eligibility checks
            # Implement the logic based on the provided requirements

            # Example: Assume loan is approved for simplicity
            loan_approved = True

            return Response({"loan_approved": loan_approved}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)






class CustomerListCreateView(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class LoanListCreateView(generics.ListCreateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer


class CreateLoanView(generics.CreateAPIView):
    serializer_class = CreateLoanSerializer  # You need to define this serializer

    def create(self, request, *args, **kwargs):
        # Implement your logic for creating a loan here
        # ...

        # Return the response
        return Response({'result': 'success'})

class ViewLoanDetailView(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

class ViewLoansByCustomerView(generics.ListAPIView):
    serializer_class = LoanSerializer

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return Loan.objects.filter(customer_id=customer_id)
