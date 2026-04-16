import pandas as pd
import re

# Load data
df = pd.read_csv('Cleaned_sentiment_data.csv')

def deep_clean_text(text):
    if pd.isna(text):
        return ""

    # 1. Brackets, quotes, underscores, and special symbols removal
    text = re.sub(r'[{}_"“”@#$%^&*()\-+=/\\<>|~`\[\]]', ' ', text)

    # 2. Only letters, numbers, spaces, and FULL STOPS mathrame unchadam
    # [^a-zA-Z0-9\s.] ante letters, numbers, spaces, full stop thappa anni lepey ani artham
    text = re.sub(r'[^a-zA-Z0-9\s.]', '', text)

    # 3. Clean extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Apply cleaning
df['Ticket Description'] = df['Ticket Description'].apply(deep_clean_text)

# Save Final version
df.to_csv('Final_Perfect_Data.csv', index=False)