import pandas as pd

def check_empty_diagnoses():
    df = pd.read_csv('backend/final_enhanced_dataset.csv')
    print('Checking for empty diagnoses:')
    print('Total records:', len(df))
    
    # Check for empty, null, or whitespace-only diagnoses
    empty_diag = df[df['diagnosis'].isna() | (df['diagnosis'] == '') | (df['diagnosis'].str.strip() == '')]
    print('Records with empty diagnosis:', len(empty_diag))
    
    if len(empty_diag) > 0:
        print('\nSample empty diagnosis records:')
        for idx, row in empty_diag.head(10).iterrows():
            symptoms = [col for col in df.columns if col not in ['diagnosis', 'duration_days', 'intensity', 'age_group', 'gender'] and row[col] == 1]
            print(f'  Row {idx}: symptoms={symptoms[:8]}')
            print(f'    diagnosis="{row["diagnosis"]}"')
    
    # Also check unique diagnosis values
    print('\nUnique diagnosis values:')
    unique_diags = df['diagnosis'].unique()
    print('Total unique diagnoses:', len(unique_diags))
    
    # Look for suspicious values
    suspicious = [d for d in unique_diags if pd.isna(d) or str(d).strip() == '' or len(str(d).strip()) < 3]
    if suspicious:
        print('Suspicious diagnosis values:', suspicious)
    
    # Check the first few and last few records
    print('\nFirst 5 diagnosis values:')
    print(df['diagnosis'].head().tolist())
    
    print('\nDiagnosis column data type:', df['diagnosis'].dtype)

if __name__ == "__main__":
    check_empty_diagnoses()