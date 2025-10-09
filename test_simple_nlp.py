#!/usr/bin/env python3
"""
Standalone NLP-based diagnosis functionality for testing
"""

import re
from typing import Dict, List, Any

class SimpleNLPDiagnosis:
    def __init__(self):
        """Initialize with condition patterns based on dataset analysis"""
        self.condition_patterns = {
            'migraine': [
                'headache', 'head pain', 'severe headache', 'throbbing', 
                'sensitivity to light', 'photophobia', 'nausea', 'vomiting',
                'aura', 'visual disturbances'
            ],
            'tension headache': [
                'headache', 'head pain', 'tight band', 'pressure', 
                'stress', 'tension', 'neck pain', 'shoulder pain'
            ],
            'pneumonia': [
                'cough', 'fever', 'shortness of breath', 'difficulty breathing',
                'chest pain', 'phlegm', 'sputum', 'chills', 'fatigue'
            ],
            'bronchitis': [
                'cough', 'persistent cough', 'phlegm', 'sputum', 'chest discomfort',
                'wheezing', 'shortness of breath', 'fatigue'
            ],
            'anxiety disorder': [
                'anxiety', 'anxious', 'worry', 'restless', 'restlessness',
                'panic', 'nervousness', 'trouble sleeping', 'insomnia',
                'racing heart', 'palpitations'
            ],
            'depression': [
                'sad', 'sadness', 'depressed', 'hopeless', 'worthless',
                'loss of interest', 'fatigue', 'sleep problems', 'appetite changes'
            ],
            'common cold': [
                'runny nose', 'stuffy nose', 'sneezing', 'sore throat',
                'mild cough', 'congestion', 'nasal discharge'
            ],
            'flu': [
                'fever', 'body aches', 'muscle aches', 'fatigue', 'chills',
                'headache', 'cough', 'sore throat', 'weakness'
            ],
            'diabetes': [
                'excessive thirst', 'frequent urination', 'hunger',
                'weight loss', 'blurred vision', 'fatigue', 'slow healing'
            ],
            'hypertension': [
                'high blood pressure', 'headache', 'dizziness', 'chest pain',
                'shortness of breath', 'nosebleeds'
            ]
        }
    
    def extract_conditions_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract matching conditions and keywords from input text"""
        text_lower = text.lower()
        matches = {}
        
        for condition, keywords in self.condition_patterns.items():
            matched_keywords = []
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                matches[condition] = matched_keywords
        
        return matches
    
    def predict_nlp_diagnosis(self, symptoms_text: str, patient_conditions: List[str] = None) -> Dict[str, Any]:
        """
        Predict diagnosis using NLP keyword matching
        """
        try:
            # Extract conditions from text
            condition_matches = self.extract_conditions_from_text(symptoms_text)
            
            if not condition_matches:
                return {
                    'diagnosis': 'Unable to determine',
                    'reasoning': 'No matching conditions found based on the provided symptoms.',
                    'matched_keywords': [],
                    'alternative_conditions': [],
                    'description': 'Please consult with a healthcare professional for proper evaluation.'
                }
            
            # Sort by number of matched keywords
            sorted_conditions = sorted(
                condition_matches.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )
            
            primary_condition = sorted_conditions[0]
            primary_diagnosis = primary_condition[0]
            primary_keywords = primary_condition[1]
            
            # Create alternative conditions list
            alternative_conditions = []
            for condition, keywords in sorted_conditions[1:4]:  # Top 3 alternatives
                alternative_conditions.append({
                    'condition': condition.title(),
                    'matched_keywords': keywords
                })
            
            # Generate reasoning
            reasoning = f"Based on reported symptoms matching {len(primary_keywords)} key indicators for {primary_diagnosis}"
            
            return {
                'diagnosis': primary_diagnosis.title(),
                'reasoning': reasoning,
                'matched_keywords': primary_keywords,
                'alternative_conditions': alternative_conditions,
                'description': f"The symptoms align with patterns commonly associated with {primary_diagnosis}. Please consult a healthcare professional for proper diagnosis and treatment.",
                'extracted_conditions': list(condition_matches.keys())
            }
            
        except Exception as e:
            return {
                'diagnosis': 'Analysis Error',
                'reasoning': f'Error during analysis: {str(e)}',
                'matched_keywords': [],
                'alternative_conditions': [],
                'description': 'Please try again or consult with a healthcare professional.'
            }

def test_nlp_diagnosis():
    """Test the NLP-based diagnosis functionality"""
    
    # Initialize the AI diagnosis engine
    ai_engine = SimpleNLPDiagnosis()
    
    # Test cases
    test_cases = [
        {
            'symptoms': 'I have been experiencing severe headaches, sensitivity to light, and nausea for the past two days',
            'expected_conditions': ['migraine', 'tension headache']
        },
        {
            'symptoms': 'I have a persistent cough, fever, and difficulty breathing',
            'expected_conditions': ['pneumonia', 'bronchitis', 'flu']
        },
        {
            'symptoms': 'I feel anxious, restless, and have trouble sleeping',
            'expected_conditions': ['anxiety', 'insomnia']
        }
    ]
    
    print("Testing NLP-based Diagnosis System")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"Symptoms: {test_case['symptoms']}")
        
        try:
            # Call the NLP diagnosis method
            result = ai_engine.predict_nlp_diagnosis(test_case['symptoms'])
            
            print(f"\nResults:")
            print(f"Primary Diagnosis: {result.get('diagnosis', 'Not found')}")
            print(f"Reasoning: {result.get('reasoning', 'No reasoning provided')}")
            
            if result.get('matched_keywords'):
                print(f"Matched Keywords: {', '.join(result['matched_keywords'])}")
            
            if result.get('alternative_conditions'):
                print("Alternative Conditions:")
                for alt in result['alternative_conditions']:
                    print(f"  - {alt['condition']} (matches: {', '.join(alt['matched_keywords'])})")
            
            print("-" * 30)
            
        except Exception as e:
            print(f"Error testing case {i}: {str(e)}")
            print("-" * 30)

if __name__ == "__main__":
    test_nlp_diagnosis()