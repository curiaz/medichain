#!/usr/bin/env python3
"""
Check what conditions in our dataset match the given symptoms better
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pandas as pd

def analyze_symptom_matches():
    print("🔍 Analyzing Better Symptom Matches")
    print("=" * 50)
    
    try:
        # Load the dataset
        df = pd.read_csv('final_enhanced_dataset.csv')
        
        # Our target symptoms
        target_symptoms = ['headache', 'fatigue', 'dizziness', 'shortness_of_breath']
        
        print(f"Target symptoms: {target_symptoms}")
        print(f"Dataset shape: {df.shape}")
        
        # Check which conditions have these symptoms
        symptom_matches = []
        
        for _, row in df.iterrows():
            matches = 0
            matched_symptoms = []
            
            for symptom in target_symptoms:
                if symptom in df.columns and str(row[symptom]) == '1':
                    matches += 1
                    matched_symptoms.append(symptom)
            
            if matches >= 2:  # At least 2 symptom matches
                symptom_matches.append({
                    'diagnosis': row.get('diagnosis', 'Unknown'),
                    'matches': matches,
                    'matched_symptoms': matched_symptoms,
                    'total_symptoms': sum([1 for col in target_symptoms if col in df.columns and str(row[col]) == '1'])
                })
        
        # Sort by number of matches
        symptom_matches.sort(key=lambda x: x['matches'], reverse=True)
        
        print(f"\n📊 Top conditions matching our symptoms:")
        print("-" * 50)
        
        seen_diagnoses = set()
        for match in symptom_matches[:10]:
            if match['diagnosis'] not in seen_diagnoses:
                seen_diagnoses.add(match['diagnosis'])
                print(f"{match['diagnosis']}: {match['matches']}/4 symptoms match")
                print(f"   Matched: {match['matched_symptoms']}")
                print()
        
        # Also check what conditions are most common for headache
        print("\n🔍 Most common diagnoses with headache:")
        headache_conditions = df[df['headache'] == '1']['diagnosis'].value_counts().head(10)
        for condition, count in headache_conditions.items():
            print(f"{condition}: {count} cases")
            
    except Exception as e:
        print(f"Error analyzing dataset: {e}")

if __name__ == "__main__":
    analyze_symptom_matches()