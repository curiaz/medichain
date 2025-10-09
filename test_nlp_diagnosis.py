#!/usr/bin/env python3
"""
Test script for NLP-based diagnosis functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from comprehensive_ai_diagnosis import ComprehensiveAIDiagnosis

def test_nlp_diagnosis():
    """Test the NLP-based diagnosis functionality"""
    
    # Initialize the AI diagnosis engine
    ai_engine = ComprehensiveAIDiagnosis()
    
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