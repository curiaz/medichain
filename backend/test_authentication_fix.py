#!/usr/bin/env python3
"""
Test script to verify authentication fixes
Tests both Firebase token and email/password authentication
"""

import requests
import json

API_URL = "http://localhost:5000/api"

def test_health_check():
    """Test 1: Server health check"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_ai_health():
    """Test 2: AI system health check"""
    print("\n" + "="*60)
    print("TEST 2: AI Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL}/ai/health")
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return response.status_code in [200, 503]  # 503 if AI not initialized
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_email_login_invalid():
    """Test 3: Email/password login with invalid credentials"""
    print("\n" + "="*60)
    print("TEST 3: Email/Password Login (Invalid)")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "WrongPassword123"
            },
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        # Should return 401 Unauthorized
        return response.status_code == 401 and not response.json().get("success", True)
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_missing_credentials():
    """Test 4: Login with missing credentials"""
    print("\n" + "="*60)
    print("TEST 4: Login with Missing Credentials")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={},
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        # Should return 400 Bad Request
        return response.status_code == 400
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_invalid_json():
    """Test 5: Login with invalid JSON"""
    print("\n" + "="*60)
    print("TEST 5: Invalid JSON Body")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        # Should return 400 Bad Request
        return response.status_code == 400
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_cors_preflight():
    """Test 6: CORS preflight request"""
    print("\n" + "="*60)
    print("TEST 6: CORS Preflight")
    print("="*60)
    
    try:
        response = requests.options(
            f"{API_URL}/auth/login",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type,Authorization"
            }
        )
        print(f"✅ Status: {response.status_code}")
        print(f"✅ CORS Headers:")
        cors_headers = {
            k: v for k, v in response.headers.items() 
            if k.startswith("Access-Control")
        }
        for header, value in cors_headers.items():
            print(f"   {header}: {value}")
        
        # Should have CORS headers
        return "Access-Control-Allow-Origin" in response.headers
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_firebase_token_invalid():
    """Test 7: Firebase token login with invalid token"""
    print("\n" + "="*60)
    print("TEST 7: Firebase Token Login (Invalid Token)")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={
                "id_token": "invalid_firebase_token_12345"
            },
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        # Should return 401 or 500 (Firebase verification fails)
        return response.status_code in [401, 500]
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def test_signup_validation():
    """Test 8: Signup with missing required fields"""
    print("\n" + "="*60)
    print("TEST 8: Signup Validation")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/auth/signup",
            json={
                "email": "test@example.com"
                # Missing password, name, role
            },
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ Status: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        # Should return 400 Bad Request
        return response.status_code == 400
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*70)
    print("🧪 AUTHENTICATION FIX - TEST SUITE")
    print("="*70)
    print("\nTesting backend at: http://localhost:5000")
    print("Make sure the backend server is running!\n")
    
    tests = [
        ("Health Check", test_health_check),
        ("AI Health Check", test_ai_health),
        ("Email Login (Invalid)", test_email_login_invalid),
        ("Missing Credentials", test_missing_credentials),
        ("Invalid JSON", test_invalid_json),
        ("CORS Preflight", test_cors_preflight),
        ("Firebase Token (Invalid)", test_firebase_token_invalid),
        ("Signup Validation", test_signup_validation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Test '{name}' crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST RESULTS SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("="*70)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed! Authentication fix is working correctly!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

