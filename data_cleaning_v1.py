import pandas as pd
# Loading the File 
df = pd.read_csv('customer_support_tickets.csv')


# Identify and keep only required columns
Required_columns = ['Customer Email', 'Ticket Description', 'Ticket Subject']
df = df[Required_columns]


# Clean the date 
df = df.dropna(subset=['Ticket Description' , 'Customer Email'])
df = df.drop_duplicates()


# performing Basic text cleaning
df['Ticket Description'] = df['Ticket Description'].str.strip().str.replace(r'\s+',' ', regex=True)


# PII Masking
df['Customer_ID'] = 'User_' +(df.groupby('Customer Email').ngroup()+ 1).astype(str)


# Final dataset Columns
final_df = df[['Customer_ID', 'Ticket Description', 'Ticket Subject']]


# Save as CSV
final_df.to_csv('Cleaned_sentiment_data.csv', index=False)


# Display final result
final_df.head()