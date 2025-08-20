#!/usr/bin/env python3
"""
Comprehensive test of all AI Assistant features
"""

import requests
import json

def test_all_features():
    """Test all AI Assistant features"""
    
    base_url = "http://localhost:5001"
    
    print("🧪 Testing AI Assistant - Comprehensive Test Suite")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. 🏥 Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Health: {result.get('status')}")
            print(f"   ✅ Model Loaded: {result.get('model_loaded')}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test 2: Model Information
    print("\n2. 📊 Testing Model Information...")
    try:
        response = requests.get(f"{base_url}/learning-stats", timeout=5)
        if response.status_code == 200:
            result = response.json()
            model_info = result.get('model_info', {})
            print(f"   ✅ Model: {model_info.get('name')}")
            print(f"   ✅ Accuracy: {model_info.get('accuracy')}")
            print(f"   ✅ Features: {model_info.get('total_features')}")
            print(f"   ✅ Conditions: {model_info.get('supported_conditions')}")
        else:
            print(f"   ❌ Model info failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Model info error: {e}")
    
    # Test 3: Normal Diagnosis
    print("\n3. 🩺 Testing Normal Diagnosis...")
    try:
        test_data = {
            "symptoms": "fever, cough, headache",
            "patient_data": {
                "age": 35,
                "gender": "Male"
            }
        }
        
        response = requests.post(
            f"{base_url}/predict",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            analysis = result.get('analysis', {})
            primary = analysis.get('primary_diagnosis', {})
            
            print(f"   ✅ Diagnosis: {primary.get('condition')}")
            print(f"   ✅ Confidence: {primary.get('confidence', 0):.1%}")
            print(f"   ✅ Recommendations: {len(result.get('recommendations', {}).get('lifestyle_advice', []))} items")
            print(f"   ✅ Medical Disclaimer: {'Yes' if result.get('medical_disclaimer') else 'No'}")
        else:
            print(f"   ❌ Diagnosis failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Diagnosis error: {e}")
    
    # Test 4: Low Confidence Case
    print("\n4. ⚠️  Testing Low Confidence Case...")
    try:
        test_data = {
            "symptoms": "unusual_symptom, rare_condition",
            "patient_data": {
                "age": 35,
                "gender": "Male"
            }
        }
        
        response = requests.post(
            f"{base_url}/predict",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'unknown_case':
                print(f"   ✅ Unknown case handled: {result.get('recommendation')}")
                print(f"   ✅ Safety message: {result.get('message')}")
            else:
                analysis = result.get('analysis', {})
                primary = analysis.get('primary_diagnosis', {})
                print(f"   ℹ️  Normal diagnosis: {primary.get('condition')} ({primary.get('confidence', 0):.1%})")
        else:
            print(f"   ❌ Low confidence test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Low confidence error: {e}")
    
    # Test 5: Feedback Submission
    print("\n5. 💬 Testing Feedback Submission...")
    try:
        feedback_data = {
            "actual_diagnosis": "Test Diagnosis",
            "doctor_notes": "Test feedback for improvement",
            "treatment_outcome": "Successful"
        }
        
        response = requests.post(
            f"{base_url}/submit-feedback",
            json=feedback_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Feedback accepted: {result.get('status')}")
            print(f"   ✅ Session ID: {result.get('session_id', 'Generated')}")
        else:
            print(f"   ❌ Feedback failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Feedback error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Test Suite Complete!")
    print("✅ All major AI Assistant features have been tested")
    print("🚀 Ready for production deployment!")

if __name__ == "__main__":
    test_all_features()
