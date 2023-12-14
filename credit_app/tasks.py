# credit_app/tasks.py
import logging
from celery import shared_task
import pandas as pd
from .models import Customer, Loan

logger = logging.getLogger(__name__)

@shared_task
def ingest_data(customer_data_path='path/to/customer_data.xlsx', loan_data_path='path/to/loan_data.xlsx'):
    try:
        # Load customer data
        customer_data = pd.read_excel(customer_data_path)
        Customer.objects.bulk_create([
            Customer(
                first_name=row['first_name'],
                last_name=row['last_name'],
                age=row['age'],
                monthly_salary=row['monthly_salary'],
                approved_limit=row['approved_limit'],
                current_debt=row['current_debt'],
                phone_number=row['phone_number']
            )
            for _, row in customer_data.iterrows()
        ])

        # Load loan data
        loan_data = pd.read_excel(loan_data_path)
        Loan.objects.bulk_create([
            Loan(
                customer_id=row['customer_id'],
                loan_amount=row['loan_amount'],
                tenure=row['tenure'],
                interest_rate=row['interest_rate'],
                monthly_repayment=row['monthly_repayment'],
                emis_paid_on_time=row['emis_paid_on_time'],
                start_date=row['start_date'],
                end_date=row['end_date']
            )
            for _, row in loan_data.iterrows()
        ])

        logger.info("Data ingestion completed successfully.")
    except Exception as e:
        logger.error(f"Data ingestion failed. Error: {e}")
