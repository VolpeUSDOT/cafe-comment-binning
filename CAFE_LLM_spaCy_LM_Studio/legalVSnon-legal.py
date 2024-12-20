import pandas as pd

# Load Excel file
df = pd.read_excel('no_blanks.xlsx')

# Update labels
df['BIN1'] = df['BIN1'].apply(lambda x: 'legal' if 'legal' in str(x).lower() else 'non-legal')

# Save updated Excel file
df.to_excel('legalVnon_legal.xlsx', index=False)