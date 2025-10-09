import pandas as pd
import sys
sys.path.append('backend')

def analyze_dataset():
    # Load and examine the dataset
    df = pd.read_csv('backend/final_enhanced_dataset.csv')
    print('Dataset Analysis:')
    print('=' * 40)
    print(f'Shape: {df.shape}')
    print(f'Columns: {list(df.columns)[:10]}...')
    print()

    # Check sample records for headache + dizziness
    print('Records with headache=1 AND dizziness=1:')
    sample = df[(df['headache'] == 1) & (df['dizziness'] == 1)].head(5)
    if not sample.empty:
        for idx, row in sample.iterrows():
            diagnosis = row['diagnosis']
            duration = row.get('duration_days', 'N/A')
            print(f'  {diagnosis} - Duration: {duration} days')
            # Show which symptoms are active
            symptoms = [col for col in df.columns if col not in ['diagnosis', 'duration_days', 'intensity'] and row[col] == 1]
            print(f'    Symptoms: {symptoms[:8]}')
    else:
        print('  No records found!')

    print()
    print('Records with fever=1 AND cough=1:')
    sample2 = df[(df['fever'] == 1) & (df['cough'] == 1)].head(5)
    if not sample2.empty:
        for idx, row in sample2.iterrows():
            diagnosis = row['diagnosis']
            duration = row.get('duration_days', 'N/A')
            print(f'  {diagnosis} - Duration: {duration} days')
            symptoms = [col for col in df.columns if col not in ['diagnosis', 'duration_days', 'intensity'] and row[col] == 1]
            print(f'    Symptoms: {symptoms[:8]}')
    else:
        print('  No records found!')

    print()
    print('Top 10 diagnoses in dataset:')
    print(df['diagnosis'].value_counts().head(10))
    
    # Check data types and values
    print()
    print('Sample data inspection:')
    print('Headache column values:', df['headache'].unique())
    print('Dizziness column values:', df['dizziness'].unique())
    print('Fever column values:', df['fever'].unique())
    print('Cough column values:', df['cough'].unique())

if __name__ == "__main__":
    analyze_dataset()