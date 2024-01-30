from main import *

file = 'data/data_set.xlsx'
column_id_client = 'customer_id'
column_purchase_date = 'transaction_date'
column_purchase_id = 'transaction_id'
sheet='Transactions'

# data from https://www.kaggle.com/datasets/archit9406/customer-transaction-dataset/data
data = pd.read_excel(file, sheet_name=sheet)

matrix = cohort_matrix(data, column_id_client, column_purchase_date, column_purchase_id)
plot(matrix)
