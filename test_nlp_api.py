#!/usr/bin/env python3
"""
Test the NLP API endpoint
"""

import requests
import json
import time

def test_api():
    """Test the NLP diagnosis API"""
    
    # API endpoint
    url = 'http://localhost:5000/api/ai/diagnose'
    
    # Test data
    test_data = {
        'symptoms': 'I have been experiencing severe headaches, sensitivity to light, and nausea for the past two days',
        'patient_age': '25',
        'patient_gender': 'female'
    }
    
    try:
        print("Testing NLP Diagnosis API...")
        print(f"URL: {url}")
        print(f"Test Data: {json.dumps(test_data, indent=2)}")
        
        # Wait a moment for server to be ready
        print("Waiting for server...")
        time.sleep(2)
        
        # Make API request
        response = requests.post(url, json=test_data, timeout=10)
        
        print(f"\nStatus Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("API Response:")
            print(json.dumps(result, indent=2))
            
            if result.get('success'):
                diagnosis = result.get('diagnosis', {})
                print(f"\nDiagnosis Summary:")
                print(f"Primary Condition: {diagnosis.get('diagnosis')}")
                print(f"Reasoning: {diagnosis.get('reasoning')}")
                print(f"Matched Keywords: {diagnosis.get('matched_keywords')}")
                
                if diagnosis.get('alternative_conditions'):
                    print("Alternative Conditions:")
                    for alt in diagnosis['alternative_conditions']:
                        print(f"  - {alt['condition']}: {', '.join(alt['matched_keywords'])}")
        else:
            print(f"API Error: {response.text}")
            
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_api()