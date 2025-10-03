#!/usr/bin/env python3
"""
Test script for AI diagnosis API
"""

import requests
import json

def test_diagnosis():
    url = "http://localhost:5000/api/ai/diagnose"
    
    data = {
        "symptoms": "i have severe headache for 3 days, shortness of breath, cough and nausea",
        "patientAge": "Senior (65+ years)",
        "patientGender": "Male"
    }
    
    try:
        response = requests.post(url, json=data)
        
        print("Status Code:", response.status_code)
        print("Response:")
        
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2))
            
            # Check if we get the structured SLIDE response
            if 'formatted_response' in result:
                print("\n=== FORMATTED RESPONSE ===")
                print(result['formatted_response'])
        else:
            print("Error:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Make sure it's running on port 5000")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_diagnosis()