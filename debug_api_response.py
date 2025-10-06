#!/usr/bin/env python3
"""
Debug API Response Structure
Check what the actual API response looks like for the frontend
"""

import requests
import json

def debug_api_response():
    """Debug the API response to understand the data structure"""
    
    print("🔍 DEBUGGING API RESPONSE STRUCTURE")
    print("="*50)
    
    test_data = {
        "symptoms": "I have headache, shortness of breath, cough and fatigue",
        "age": 30,
        "gender": "male"
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/api/ai/diagnose",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("📋 FULL API RESPONSE:")
            print(json.dumps(result, indent=2))
            
            print(f"\n🔑 TOP-LEVEL KEYS:")
            for key in result.keys():
                print(f"   • {key}: {type(result[key])}")
            
            # Check for diagnosis fields
            diagnosis_fields = ['diagnosis', 'primary_diagnosis', 'formatted_response']
            print(f"\n🩺 DIAGNOSIS FIELDS:")
            for field in diagnosis_fields:
                if field in result:
                    print(f"   ✅ {field}: {result[field]}")
                else:
                    print(f"   ❌ {field}: Missing")
            
            # Check for prediction fields
            prediction_fields = ['top_predictions', 'top_3_predictions', 'differential_diagnoses']
            print(f"\n📊 PREDICTION FIELDS:")
            for field in prediction_fields:
                if field in result:
                    predictions = result[field]
                    print(f"   ✅ {field}: {len(predictions) if isinstance(predictions, list) else 'Not a list'}")
                    if isinstance(predictions, list) and len(predictions) > 0:
                        print(f"      Sample: {predictions[0]}")
                else:
                    print(f"   ❌ {field}: Missing")
            
            # Check for symptom fields
            symptom_fields = ['detected_symptoms', 'matched_symptoms', 'active_symptoms_count']
            print(f"\n🎯 SYMPTOM FIELDS:")
            for field in symptom_fields:
                if field in result:
                    print(f"   ✅ {field}: {result[field]}")
                else:
                    print(f"   ❌ {field}: Missing")
            
            # Check confidence fields
            confidence_fields = ['confidence', 'confidence_percent']
            print(f"\n📈 CONFIDENCE FIELDS:")
            for field in confidence_fields:
                if field in result:
                    print(f"   ✅ {field}: {result[field]}")
                else:
                    print(f"   ❌ {field}: Missing")
            
        else:
            print(f"❌ API Error: Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_api_response()