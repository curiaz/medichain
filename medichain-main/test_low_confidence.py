#!/usr/bin/env python3
"""
Test low confidence case that triggers unknown case handling
"""

import requests
import json

def test_low_confidence():
    """Test a symptom combination that might give low confidence"""
    
    url = "http://localhost:5001/predict"
    
    # Test with unusual symptom combination that might trigger low confidence
    test_data = {
        "symptoms": "unusual_symptom, rare_condition, strange_feeling",
        "patient_data": {
            "age": 35,
            "gender": "Male"
        }
    }
    
    print("Testing low confidence case:")
    print(json.dumps(test_data, indent=2))
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response received:")
            
            # Check if this is an unknown case response
            if 'status' in result and result['status'] == 'unknown_case':
                print("✅ Unknown case handling triggered correctly")
                print(f"Message: {result.get('message')}")
                print(f"Recommendation: {result.get('recommendation')}")
            else:
                # Normal diagnosis response
                analysis = result.get('analysis', {})
                primary_diagnosis = analysis.get('primary_diagnosis', {})
                condition = primary_diagnosis.get('condition', 'Not found')
                confidence = primary_diagnosis.get('confidence', 'Not found')
                print(f"Normal diagnosis: {condition} (confidence: {confidence})")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_low_confidence()
