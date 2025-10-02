#!/usr/bin/env python3
"""
Update the enhanced dataset to use age groups instead of numeric ages
"""

import pandas as pd

def convert_age_to_group(age_str):
    """Convert age group string to standardized format"""
    if not age_str or pd.isna(age_str):
        return 'adult'  # Default fallback
    
    age_str = str(age_str).lower().strip()
    
    if age_str in ['child']:
        return 'child'
    elif age_str in ['teen']:
        return 'teen'  
    elif age_str in ['adult']:
        return 'adult'
    elif age_str in ['senior']:
        return 'senior'
    else:
        # If it's not a recognized age group, default to adult
        return 'adult'

def main():
    # Load the current dataset
    df = pd.read_csv('final_enhanced_dataset.csv')
    
    print(f"Original dataset shape: {df.shape}")
    print(f"Original age_group values: {df['age_group'].value_counts()}")
    
    # Update age groups to use standardized format
    df['age_group'] = df['age_group'].apply(convert_age_to_group)
    
    print(f"\nUpdated age_group values: {df['age_group'].value_counts()}")
    
    # Save the updated dataset
    df.to_csv('final_enhanced_dataset.csv', index=False)
    print(f"\nDataset updated successfully!")
    print(f"Total records: {len(df)}")
    print(f"Unique diagnoses: {df['diagnosis'].nunique()}")
    print(f"Age group distribution:")
    print(df['age_group'].value_counts())

if __name__ == "__main__":
    main()