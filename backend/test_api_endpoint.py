#!/usr/bin/env python3
"""
Test the running API endpoint
"""

import requests
import json

def test_api():
    """Test the diagnosis API"""
    
    print("=" * 60)
    print("🧪 Testing AI Diagnosis API")
    print("=" * 60)
    
    # Test health endpoint
    print("\n1️⃣  Testing health endpoint...")
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test AI health endpoint
    print("\n2️⃣  Testing AI health endpoint...")
    try:
        response = requests.get("http://localhost:5000/api/ai/health")
        print(f"   Status: {response.status_code}")
        data = response.json()
        print(f"   AI System: {data.get('ai_system')}")
        print(f"   Conditions: {data.get('conditions_loaded')}")
        print(f"   Symptoms: {data.get('symptoms_tracked')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test diagnosis endpoint
    print("\n3️⃣  Testing diagnosis endpoint...")
    try:
        test_data = {
            "symptoms": "fever, cough, sore throat, fatigue"
        }
        
        response = requests.post(
            "http://localhost:5000/api/diagnose",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                data = result['data']
                print(f"   ✅ Diagnosis successful!")
                print(f"   Primary Condition: {data['primary_condition']}")
                print(f"   Confidence: {data['primary_confidence']}")
                print(f"   Detected Symptoms: {len(data['detected_symptoms'])}")
                
                print(f"\n   📋 Top 3 Diagnoses:")
                for i, detail in enumerate(data['detailed_results'][:3], 1):
                    print(f"   {i}. {detail['condition']} - {detail['confidence']}")
                    print(f"      Medication: {detail['medication'][:50]}...")
            else:
                print(f"   ❌ Diagnosis failed: {result.get('message')}")
                return False
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test another diagnosis
    print("\n4️⃣  Testing with different symptoms...")
    try:
        test_data2 = {
            "symptoms": "headache, nausea, dizziness"
        }
        
        response = requests.post(
            "http://localhost:5000/api/diagnose",
            json=test_data2,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                data = result['data']
                print(f"   ✅ Diagnosis: {data['primary_condition']} ({data['primary_confidence']})")
            else:
                print(f"   ❌ Failed: {result.get('message')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ API tests completed successfully!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    import sys
    success = test_api()
    sys.exit(0 if success else 1)
