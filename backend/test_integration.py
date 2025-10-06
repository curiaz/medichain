#!/usr/bin/env python3
"""
Complete integration test for MediChain backend AI system
"""

import requests
import json
import time

def test_ai_backend():
    """Test the complete AI backend system"""
    
    print("🧪 COMPREHENSIVE MEDICHAIN AI BACKEND TEST")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Check if server is running
    print("\n1️⃣ Testing server health...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test 2: Test AI diagnosis endpoint 
    print("\n2️⃣ Testing AI diagnosis endpoint...")
    test_cases = [
        {
            "name": "COVID-like symptoms",
            "data": {
                "text": "I have fever, bad cough, and can't taste anything",
                "age": 30,
                "gender": "male"
            }
        },
        {
            "name": "Flu-like symptoms", 
            "data": {
                "text": "I feel tired, have body aches and headache",
                "age": 45,
                "gender": "female"
            }
        },
        {
            "name": "Respiratory issues",
            "data": {
                "text": "difficulty breathing, chest pain, wheezing",
                "age": 60,
                "gender": "male"
            }
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test {i}: {test_case['name']}")
        try:
            response = requests.post(
                f"{base_url}/api/ai/diagnose",
                json=test_case["data"],
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Success: {result.get('primary_diagnosis', 'N/A')}")
                print(f"      Confidence: {result.get('confidence_percent', 'N/A')}")
                print(f"      Severity: {result.get('severity', 'N/A')}")
                print(f"      Medications: {len(result.get('medications', []))}")
            else:
                print(f"   ❌ Failed: {response.status_code}")
                print(f"      Response: {response.text}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            all_passed = False
    
    # Test 3: Test error handling
    print("\n3️⃣ Testing error handling...")
    try:
        response = requests.post(
            f"{base_url}/api/ai/diagnose",
            json={},  # Empty data
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 400:
            print("   ✅ Proper error handling for empty data")
        else:
            print(f"   ❌ Unexpected response for empty data: {response.status_code}")
            all_passed = False
            
    except Exception as e:
        print(f"   ❌ Error testing error handling: {e}")
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! AI Backend is working perfectly!")
        print("🏥 MediChain AI system ready for production!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return all_passed

if __name__ == "__main__":
    test_ai_backend()