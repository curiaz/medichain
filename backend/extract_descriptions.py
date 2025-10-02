#!/usr/bin/env python3
"""Extract correct diagnosis descriptions from the dataset"""

import pandas as pd
import json

def extract_diagnosis_descriptions():
    """Extract diagnosis descriptions from the enhanced dataset"""
    print("=== Extracting Diagnosis Descriptions from Dataset ===")
    
    # Load the dataset
    df = pd.read_csv('final_enhanced_dataset.csv')
    
    print(f"Loaded {len(df)} records")
    print(f"Columns: {list(df.columns)}")
    
    # Extract unique diagnosis descriptions
    diagnosis_info = {}
    
    for _, row in df.iterrows():
        diagnosis = row['diagnosis']  # The second diagnosis column
        description = row.get('diagnosis_description', '')
        action = row.get('recommended_action', '')
        
        if pd.notna(diagnosis) and pd.notna(description) and description.strip():
            if diagnosis not in diagnosis_info:
                diagnosis_info[diagnosis] = {
                    'description': description.strip(),
                    'action': action.strip() if pd.notna(action) else '',
                    'count': 0
                }
            diagnosis_info[diagnosis]['count'] += 1
    
    # Display extracted information
    print(f"\nExtracted descriptions for {len(diagnosis_info)} conditions:")
    
    for condition, info in sorted(diagnosis_info.items()):
        print(f"\n--- {condition} (appears {info['count']} times) ---")
        print(f"Description: {info['description']}")
        print(f"Action: {info['action']}")
    
    # Save to JSON for easy loading
    output_file = 'correct_diagnosis_descriptions.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(diagnosis_info, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved correct descriptions to {output_file}")
    
    return diagnosis_info

if __name__ == "__main__":
    extract_diagnosis_descriptions()