"""
Test script to verify login flow and Supabase integration
"""

import requests
import json
import pytest

# Configuration
BASE_URL = "http://localhost:5000/api"

@pytest.mark.skip(reason="This is an HTTP smoke script, not a pytest unit test")
def test_health_check():
    """Test if backend is running"""
    print("\n" + "="*60)
    print("1️⃣  Testing Backend Health Check")
    print("="*60)
    
    try:
        response = requests.get("http://localhost:5000/health")
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

@pytest.mark.skip(reason="External HTTP flow helper, skip in unit test suite")
def test_signup(email, password, name, role="patient"):
    """Test user registration"""
    print("\n" + "="*60)
    print(f"2️⃣  Testing User Registration - {email}")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": password,
                "name": name,
                "role": role
            }
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [201, 409]:  # 409 = already exists
            return True, response.json()
        return False, response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

@pytest.mark.skip(reason="External HTTP flow helper, skip in unit test suite")
def test_login(email, password):
    """Test user login"""
    print("\n" + "="*60)
    print(f"3️⃣  Testing User Login - {email}")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            },
            headers={
                "Content-Type": "application/json"
            }
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

@pytest.mark.skip(reason="External HTTP flow helper, skip in unit test suite")
def test_get_user(token):
    """Test get current user endpoint"""
    print("\n" + "="*60)
    print("4️⃣  Testing Get Current User")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

@pytest.mark.skip(reason="External HTTP flow helper, skip in unit test suite")
def test_resend_verification(email):
    """Test resend verification endpoint"""
    print("\n" + "="*60)
    print("5️⃣  Testing Resend Verification")
    print("="*60)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/resend-verification",
            json={
                "email": email
            }
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            return True, response.json()
        return False, response.json()
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 MediChain Login Flow Test Suite")
    print("="*60)
    
    # Test credentials
    test_email = "test_patient@medichain.com"
    test_password = "Test123456"
    test_name = "Test Patient"
    
    results = {
        "health_check": False,
        "signup": False,
        "login": False,
        "get_user": False,
        "resend_verification": False
    }
    
    # Test 1: Health check
    results["health_check"] = test_health_check()
    
    # Test 2: Signup (may already exist)
    signup_success, signup_data = test_signup(test_email, test_password, test_name)
    results["signup"] = signup_success
    
    # Test 3: Login
    login_success, login_data = test_login(test_email, test_password)
    results["login"] = login_success
    
    # Test 4: Get current user (if login successful)
    if login_success and login_data and "data" in login_data:
        token = login_data["data"]["token"]
        get_user_success, _ = test_get_user(token)
        results["get_user"] = get_user_success
    
    # Test 5: Resend verification
    resend_success, _ = test_resend_verification(test_email)
    results["resend_verification"] = resend_success
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print("\n" + "="*60)
    print(f"Total: {passed_tests}/{total_tests} tests passed")
    print("="*60)
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main()
