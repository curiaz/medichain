#!/usr/bin/env python3
"""
Direct test of diagnosis endpoint with detailed error info
"""

import requests
import json

def test_diagnosis_direct():
    """Test diagnosis endpoint directly with full error details"""
    
    print("🔍 DIRECT DIAGNOSIS ENDPOINT TEST")
    print("=" * 40)
    
    url = "http://localhost:5000/api/ai/diagnose"
    data = {
        "text": "I have fever, bad cough, and difficulty breathing",
        "age": 30,
        "gender": "male"
    }
    
    print(f"🌐 URL: {url}")
    print(f"📋 Data: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"\n📊 Status Code: {response.status_code}")
        print(f"📄 Headers: {dict(response.headers)}")
        print(f"📝 Response Text: {response.text}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_response = response.json()
                print(f"🔧 JSON Response: {json.dumps(json_response, indent=2)}")
            except Exception as e:
                print(f"❌ JSON decode error: {e}")
        
    except Exception as e:
        print(f"❌ Request error: {e}")

if __name__ == "__main__":
    test_diagnosis_direct()