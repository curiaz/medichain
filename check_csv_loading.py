import csv
import pandas as pd

def check_csv_loading():
    print('Checking CSV loading methods:')
    print('=' * 40)

    # Method 1: CSV DictReader (used by AI engine)
    with open('backend/final_enhanced_dataset.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        dataset = list(reader)
        sample_row = dataset[0]
        print('CSV DictReader:')
        print(f'  headache value: {repr(sample_row["headache"])}, type: {type(sample_row["headache"])}')
        print(f'  dizziness value: {repr(sample_row["dizziness"])}, type: {type(sample_row["dizziness"])}')
        
        # Count rows with headache=1 and dizziness=1 (as strings)
        matches = []
        for i, row in enumerate(dataset):
            if row.get('headache') == '1' and row.get('dizziness') == '1':
                matches.append((i, row['diagnosis']))
            if len(matches) >= 3:
                break
        
        print(f'  Rows with headache="1" and dizziness="1": {len(matches)}')
        for i, diag in matches:
            print(f'    Row {i}: {diag}')

    # Method 2: pandas (for comparison)
    print()
    df = pd.read_csv('backend/final_enhanced_dataset.csv')
    sample_row_pd = df.iloc[0]
    print('Pandas:')
    print(f'  headache value: {repr(sample_row_pd["headache"])}, type: {type(sample_row_pd["headache"])}')
    print(f'  dizziness value: {repr(sample_row_pd["dizziness"])}, type: {type(sample_row_pd["dizziness"])}')
    matching_pd = df[(df['headache'] == 1) & (df['dizziness'] == 1)]
    print(f'  Rows with headache=1 and dizziness=1: {len(matching_pd)}')
    if len(matching_pd) > 0:
        for i, row in matching_pd.head(3).iterrows():
            print(f'    Row {i}: {row["diagnosis"]}')

if __name__ == "__main__":
    check_csv_loading()