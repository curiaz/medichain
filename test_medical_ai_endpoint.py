#!/usr/bin/env python3
"""
Test the enhanced medical-ai-assistant endpoint
"""
import requests
import json

def test_medical_ai_assistant():
    """Test the medical AI assistant endpoint with comprehensive response"""
    
    url = "http://localhost:5001/medical-ai-assistant"
    
    test_data = {
        "symptoms_history": "I have been experiencing severe headache, fever, and fatigue for the past 3 days. The headache is throbbing and gets worse with movement.",
        "patient_data": {
            "age": 35,
            "gender": "male",
            "allergies": "penicillin",
            "current_medications": "ibuprofen 400mg",
            "chronic_conditions": ["hypertension"]
        }
    }
    
    try:
        print("🧪 Testing medical-ai-assistant endpoint...")
        print(f"📤 Request URL: {url}")
        print(f"📋 Request Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"\n📡 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Response received successfully!")
            print(f"📊 Response Data Structure:")
            print(json.dumps(result, indent=2))
            
            # Check for structured data
            if 'structured_data' in result:
                structured = result['structured_data']
                print(f"\n🔍 Structured Data Analysis:")
                print(f"Primary Diagnosis: {structured.get('primary_diagnosis', 'Not found')}")
                print(f"Confidence: {structured.get('confidence', 'Not found')}")
                print(f"Detected Symptoms: {structured.get('symptoms_detected', [])}")
                print(f"Medications: {len(structured.get('medications', []))} items")
                print(f"Treatments: {len(structured.get('treatments', []))} items")
                print(f"Warnings: {len(structured.get('warnings', []))} items")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed: AI server is not running")
        print("💡 Please start the AI server with: python run_ai_server.py")
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    test_medical_ai_assistant()
