#!/usr/bin/env python3
"""
Quick test to verify the AI server is running on port 5000
"""

import requests
import json

def test_ai_server():
    """Test if the AI server is responding on port 5000"""
    
    try:
        # Test health endpoint
        print("Testing AI server health endpoint...")
        health_response = requests.get('http://localhost:5000/api/ai/health', timeout=5)
        print(f"Health check status: {health_response.status_code}")
        
        if health_response.status_code == 200:
            print("✅ AI server is running successfully on port 5000")
            health_data = health_response.json()
            print(f"Server info: {health_data}")
            
            # Test diagnosis endpoint
            print("\nTesting diagnosis endpoint...")
            test_data = {
                'symptoms': 'headache, fever, cough and fatigue',
                'patientAge': '25',
                'patientGender': 'male'
            }
            
            diagnosis_response = requests.post(
                'http://localhost:5000/api/ai/diagnose', 
                json=test_data,
                timeout=10
            )
            
            print(f"Diagnosis status: {diagnosis_response.status_code}")
            
            if diagnosis_response.status_code == 200:
                print("✅ Diagnosis endpoint is working")
                result = diagnosis_response.json()
                if result.get('success'):
                    diagnosis = result['analysis']['diagnosis_data']
                    print(f"Sample diagnosis: {diagnosis.get('diagnosis', 'Unknown')}")
                else:
                    print(f"❌ Diagnosis failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ Diagnosis endpoint failed: {diagnosis_response.text}")
                
        else:
            print(f"❌ AI server health check failed: {health_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to AI server on port 5000")
        print("   Make sure the server is running with: python nlp_app.py")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_ai_server()