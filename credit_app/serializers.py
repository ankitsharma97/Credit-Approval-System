# credit_app/serializers.py
from rest_framework import serializers
from .models import Customer, Loan
from rest_framework.views import APIView
from rest_framework.response import Response


class ViewLoansSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_installment', 'repayments_left']


class ViewLoanSerializer(serializers.ModelSerializer):
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Loan
        fields = ['loan_id', 'customer', 'loan_approved', 'loan_amount', 'interest_rate', 'monthly_installment', 'tenure']

    def get_customer(self, obj):
        # Customize this method to include the necessary customer details
        customer_data = {
            "id": obj.customer.id,
            "first_name": obj.customer.first_name,
            "last_name": obj.customer.last_name,
            "phone_number": obj.customer.phone_number,
            "age": obj.customer.age
        }
        return customer_data


class RegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    age = serializers.IntegerField()
    monthly_income = serializers.IntegerField()
    phone_number = serializers.IntegerField()


class LoanApplicationSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()


class CreateLoanSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

    def create(self, validated_data):
        # Your logic to create a loan object in the database goes here
        pass
class EligibilityCheckSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

# Example view using the serializer
class CheckEligibilityView(APIView):
    def post(self, request, *args, **kwargs):
        # Use the serializer to validate and process data
        serializer = EligibilityCheckSerializer(data=request.data)
        if serializer.is_valid():
            # Do something with the validated data
            data = serializer.validated_data
            return Response({"status": "success", "data": data})
        else:
            return Response({"status": "error", "errors": serializer.errors})


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

