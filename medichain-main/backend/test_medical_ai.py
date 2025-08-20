#!/usr/bin/env python3
"""
Test script for the Medical AI Assistant API endpoints
"""

import requests
import json

def test_medical_ai_assistant():
    """Test the medical AI assistant endpoint"""
    
    # Test data
    test_data = {
        "symptoms_history": "I have been feeling tired and have a sore throat for 3 days, also experiencing some headaches",
        "patient_data": {
            "age": 35,
            "gender": "female",
            "allergies": "Penicillin",
            "current_medications": "Birth control",
            "chronic_conditions": ["Hypertension"]
        }
    }
    
    try:
        print("🧪 Testing Medical AI Assistant Endpoint...")
        print("=" * 60)
        
        # Test the medical AI assistant endpoint
        response = requests.post(
            "http://localhost:5001/medical-ai-assistant",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Medical AI Assistant Response:")
            print("-" * 40)
            print(result.get("ai_assistant_response", "No response text"))
            print("-" * 40)
            print(f"Session ID: {result.get('session_id', 'N/A')}")
            print(f"Timestamp: {result.get('timestamp', 'N/A')}")
            
            # Show structured data
            structured = result.get("structured_data", {})
            analysis = structured.get("analysis", {})
            print(f"\n📊 Analysis Summary:")
            print(f"Primary Diagnosis: {analysis.get('primary_diagnosis', 'N/A')}")
            print(f"Confidence: {analysis.get('confidence', 'N/A')}")
            print(f"Symptoms Detected: {', '.join(analysis.get('symptoms_detected', []))}")
            
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the AI server is running on port 5001")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def test_other_endpoints():
    """Test other AI endpoints"""
    
    print("\n🔍 Testing Other Endpoints...")
    print("=" * 60)
    
    endpoints = [
        ("GET", "/health", None),
        ("GET", "/symptoms", None),
        ("GET", "/diagnoses", None),
        ("GET", "/learning-stats", None)
    ]
    
    for method, endpoint, data in endpoints:
        try:
            url = f"http://localhost:5001{endpoint}"
            
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
                
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {endpoint}: {len(str(result))} chars of data")
                
                # Show some key info
                if endpoint == "/symptoms":
                    symptoms = result.get("symptoms", [])
                    print(f"   Available symptoms: {', '.join(symptoms[:3])}...")
                elif endpoint == "/diagnoses":
                    diagnoses = result.get("diagnoses", [])
                    print(f"   Available diagnoses: {', '.join(diagnoses[:3])}...")
                elif endpoint == "/learning-stats":
                    model_info = result.get("model_info", {})
                    print(f"   Model: {model_info.get('name', 'N/A')} v{model_info.get('version', 'N/A')}")
                    
            else:
                print(f"❌ {endpoint}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)}")

if __name__ == "__main__":
    print("🩺 MediChain AI Backend Test Suite")
    print("=" * 60)
    
    # Test medical AI assistant (main new feature)
    test_medical_ai_assistant()
    
    # Test other endpoints
    test_other_endpoints()
    
    print("\n✅ Test completed!")
