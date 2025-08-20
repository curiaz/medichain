#!/usr/bin/env python3
"""
Test AI diagnosis server connectivity
"""

import requests
import json

def test_ai_server():
    """Test the AI diagnosis server"""
    
    # Test different URLs
    urls_to_test = [
        "http://localhost:5001",
        "http://127.0.0.1:5001"
    ]
    
    for base_url in urls_to_test:
        print(f"\n=== Testing {base_url} ===")
        
        # Test health endpoint
        try:
            print("Testing /health endpoint...")
            health_response = requests.get(f"{base_url}/health", timeout=5)
            print(f"Health Status: {health_response.status_code}")
            print(f"Health Response: {health_response.text}")
        except Exception as e:
            print(f"Health check failed: {e}")
        
        # Test predict endpoint (correct endpoint name)
        try:
            print("Testing /predict endpoint...")
            test_data = {
                "symptoms": "fever, cough, headache",
                "patient_data": {
                    "age": 35,
                    "gender": "Male",
                    "patient_id": "test_001",
                    "name": "Test Patient"
                },
                "doctor_id": "doctor_001",
                "include_recommendations": True,
                "detailed_analysis": True
            }
            
            response = requests.post(
                f"{base_url}/predict",
                json=test_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"Predict Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                # Extract diagnosis from the new nested structure
                analysis = result.get('analysis', {})
                primary_diagnosis = analysis.get('primary_diagnosis', {})
                diagnosis = primary_diagnosis.get('condition', 'Not found')
                confidence = primary_diagnosis.get('confidence', 'Not found')
                
                print(f"Diagnosis: {diagnosis}")
                print(f"Confidence: {confidence}")
                print(f"Response keys: {list(result.keys())}")
                
                # Show some additional details
                if 'analysis' in result:
                    symptoms = analysis.get('symptom_analysis', {})
                    present_symptoms = symptoms.get('present_symptoms', [])
                    print(f"Detected symptoms: {present_symptoms}")
                    
                    # Show recommendations if available
                    recommendations = result.get('recommendations', {})
                    if recommendations:
                        print(f"Has recommendations: {list(recommendations.keys())}")
            else:
                print(f"Error Response: {response.text}")
                
        except Exception as e:
            print(f"Predict test failed: {e}")

if __name__ == "__main__":
    test_ai_server()
