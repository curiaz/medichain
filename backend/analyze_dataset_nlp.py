#!/usr/bin/env python3
"""
Analyze dataset for NLP condition extraction
"""

import pandas as pd
import re
from collections import Counter

def analyze_dataset():
    """Analyze the dataset to extract conditions and create NLP patterns"""
    
    print("🔍 ANALYZING DATASET FOR NLP EXTRACTION")
    print("="*50)
    
    # Load dataset
    df = pd.read_csv('final_enhanced_dataset.csv')
    
    # Get unique conditions
    unique_conditions = df['diagnosis'].unique()
    print(f"📊 Total unique conditions: {len(unique_conditions)}")
    print("🏥 All conditions:")
    for i, condition in enumerate(sorted(unique_conditions), 1):
        print(f"   {i:2d}. {condition}")
    
    # Analyze symptoms column for NLP patterns
    print(f"\n💬 SAMPLE SYMPTOM DESCRIPTIONS:")
    sample_symptoms = df['symptoms'].dropna().head(10)
    for i, symptom in enumerate(sample_symptoms, 1):
        condition = df.iloc[i-1]['diagnosis']
        print(f"   {i}. \"{symptom}\" → {condition}")
    
    # Create condition keywords mapping
    print(f"\n🧠 CONDITION KEYWORD PATTERNS:")
    condition_keywords = {}
    
    # Define keyword patterns for each condition
    condition_patterns = {
        'Common Cold': ['cold', 'runny nose', 'sneezing', 'congestion'],
        'Flu': ['flu', 'influenza', 'fever', 'body aches', 'chills'],
        'COVID-19': ['covid', 'coronavirus', 'loss of taste', 'loss of smell'],
        'Pneumonia': ['pneumonia', 'chest infection', 'productive cough'],
        'Bronchitis': ['bronchitis', 'persistent cough', 'phlegm'],
        'Asthma': ['asthma', 'wheezing', 'breathing problems'],
        'Allergies': ['allergies', 'sneezing', 'itchy eyes', 'seasonal'],
        'Sinusitis': ['sinus', 'facial pressure', 'nasal congestion'],
        'Migraine': ['migraine', 'severe headache', 'light sensitivity'],
        'Tension Headache': ['tension headache', 'pressure headache'],
        'Gastroenteritis': ['stomach bug', 'food poisoning', 'stomach flu'],
        'UTI': ['urinary', 'burning urination', 'frequent urination'],
        'Strep Throat': ['strep', 'severe sore throat', 'throat infection'],
        'Ear Infection': ['ear infection', 'ear pain', 'hearing problems'],
        'Hypertension': ['high blood pressure', 'hypertension', 'elevated bp'],
        'Diabetes': ['diabetes', 'high blood sugar', 'frequent urination'],
        'Anxiety': ['anxiety', 'panic', 'worry', 'nervousness'],
        'Depression': ['depression', 'sadness', 'low mood', 'hopelessness'],
        'Arthritis': ['arthritis', 'joint pain', 'stiffness'],
        'Back Pain': ['back pain', 'lower back', 'spine pain']
    }
    
    for condition, keywords in condition_patterns.items():
        if condition in unique_conditions:
            condition_keywords[condition] = keywords
            print(f"   • {condition}: {', '.join(keywords)}")
    
    return condition_keywords

def create_nlp_extractor():
    """Create NLP-based condition extractor"""
    
    condition_keywords = analyze_dataset()
    
    print(f"\n🚀 CREATING NLP CONDITION EXTRACTOR")
    print("-" * 40)
    
    # Generate NLP extraction code
    nlp_code = '''
def extract_conditions_from_text(user_input):
    """
    Extract possible conditions from user input using NLP and keyword matching
    
    Args:
        user_input (str): User's symptom description
        
    Returns:
        list: List of possible conditions with reasoning
    """
    
    user_text = user_input.lower()
    possible_conditions = []
    
    # Condition keyword patterns (generated from dataset analysis)
    condition_patterns = {'''
    
    for condition, keywords in condition_keywords.items():
        keyword_list = "', '".join(keywords)
        nlp_code += f'''
        '{condition}': ['{keyword_list}'],'''
    
    nlp_code += '''
    }
    
    # Extract conditions based on keyword matching
    for condition, keywords in condition_patterns.items():
        matches = []
        for keyword in keywords:
            if keyword in user_text:
                matches.append(keyword)
        
        if matches:
            confidence_score = len(matches) / len(keywords)  # Simple scoring
            possible_conditions.append({
                'condition': condition,
                'matched_keywords': matches,
                'reasoning': f"Detected keywords: {', '.join(matches)}",
                'match_score': confidence_score
            })
    
    # Sort by match score (most likely first)
    possible_conditions.sort(key=lambda x: x['match_score'], reverse=True)
    
    return possible_conditions[:3]  # Return top 3 matches
'''
    
    print("Generated NLP extraction function!")
    return nlp_code

if __name__ == "__main__":
    nlp_code = create_nlp_extractor()
    
    # Save to file
    with open('nlp_condition_extractor.py', 'w') as f:
        f.write(nlp_code)
    
    print(f"\n✅ NLP extractor saved to 'nlp_condition_extractor.py'")
    print("🎯 Next steps:")
    print("   1. Remove confidence levels from AI responses")
    print("   2. Integrate NLP condition extraction")
    print("   3. Update frontend to show extracted conditions")