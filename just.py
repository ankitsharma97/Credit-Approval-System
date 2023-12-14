import pandas as pd

# Example script using pandas
excel_path = 'path/to/loan_data.xlsx'
df = pd.read_excel(excel_path)
print(df.head())  # Print the first few rows of the dataframe