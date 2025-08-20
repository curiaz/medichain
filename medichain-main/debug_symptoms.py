#!/usr/bin/env python3
"""
Debug the symptoms parsing issue
"""

import requests
import json

def test_with_debug():
    """Test with verbose debugging"""
    
    url = "http://localhost:5001/predict"
    
    # Test data exactly as sent by frontend
    test_data = {
        "symptoms": "fever, cough, headache",
        "patient_data": {
            "age": 35,
            "gender": "Male",
            "patient_id": "temp_1723944729123",
            "name": "Patient"
        },
        "doctor_id": "doctor_001",
        "include_recommendations": True,
        "detailed_analysis": True
    }
    
    print("Sending request:")
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
            print("Success! Diagnosis received:")
            analysis = result.get('analysis', {})
            primary_diagnosis = analysis.get('primary_diagnosis', {})
            print(f"- Condition: {primary_diagnosis.get('condition')}")
            print(f"- Confidence: {primary_diagnosis.get('confidence')}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_with_debug()
