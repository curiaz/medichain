#!/usr/bin/env python3
import pandas as pd
import os

# Load the CSV file
csv_path = os.path.join('backend', 'final_enhanced_dataset.csv')
try:
    df = pd.read_csv(csv_path)
    print("=== CSV Dataset Analysis ===")
    print(f"Total records: {len(df)}")
    print("\n=== Unique Diagnoses in CSV ===")
    diagnosis_counts = df['diagnosis'].value_counts()
    print(diagnosis_counts)
    
    print("\n=== Sample Records ===")
    print("First 5 records:")
    for idx, row in df.head().iterrows():
        symptoms = [col for col in df.columns if col in ['fever', 'cough', 'fatigue', 'headache', 'nausea', 'dizziness'] and str(row[col]) == '1']
        print(f"Row {idx+1}: Symptoms: {symptoms} -> Diagnosis: {row['diagnosis']}")
        
    print("\n=== Diagnosis Distribution ===")
    total = len(df)
    for diag, count in diagnosis_counts.items():
        percentage = (count / total) * 100
        print(f"{diag}: {count} records ({percentage:.1f}%)")
        
except Exception as e:
    print(f"Error reading CSV: {e}")