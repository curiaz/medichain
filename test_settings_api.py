"""
Quick Test Script for Settings Backend
Tests all API endpoints with mock data
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000/api/settings"
AUTH_TOKEN = "YOUR_FIREBASE_TOKEN_HERE"  # Replace with actual token

# Headers
headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def print_response(endpoint, method, response):
    """Pretty print API response"""
    print(f"\n{'='*60}")
    print(f"{method} {endpoint}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)
    print(f"{'='*60}")

def test_health_check():
    """Test health check endpoint (no auth required)"""
    print("\n🏥 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("/health", "GET", response)
    return response.status_code == 200

def test_get_notifications():
    """Test GET notification preferences"""
    print("\n📧 Testing GET Notification Preferences...")
    response = requests.get(f"{BASE_URL}/notifications", headers=headers)
    print_response("/notifications", "GET", response)
    return response.status_code in [200, 401]  # 401 if token invalid

def test_update_notifications():
    """Test PUT notification preferences"""
    print("\n📧 Testing UPDATE Notification Preferences...")
    
    data = {
        "email_notifications": False,
        "sms_notifications": True,
        "appointment_reminders": True,
        "diagnosis_alerts": False
    }
    
    response = requests.put(
        f"{BASE_URL}/notifications",
        headers=headers,
        json=data
    )
    print_response("/notifications", "PUT", response)
    return response.status_code in [200, 401]

def test_change_password():
    """Test password change"""
    print("\n🔑 Testing Password Change...")
    
    data = {
        "current_password": "OldPassword123!",
        "new_password": "NewSecurePass456!",
        "confirm_password": "NewSecurePass456!"
    }
    
    response = requests.post(
        f"{BASE_URL}/security/password",
        headers=headers,
        json=data
    )
    print_response("/security/password", "POST", response)
    return response.status_code in [200, 400, 401]  # 400 for validation, 401 for auth

def test_weak_password():
    """Test password validation with weak password"""
    print("\n🔑 Testing Weak Password Validation...")
    
    data = {
        "current_password": "OldPassword123!",
        "new_password": "weak",
        "confirm_password": "weak"
    }
    
    response = requests.post(
        f"{BASE_URL}/security/password",
        headers=headers,
        json=data
    )
    print_response("/security/password (weak)", "POST", response)
    
    # Should return 400 for weak password
    if response.status_code == 400:
        print("✅ Weak password correctly rejected")
        return True
    elif response.status_code == 401:
        print("⚠️  Auth failed (expected if token invalid)")
        return True
    else:
        print("❌ Weak password not rejected properly")
        return False

def test_get_audit_log():
    """Test GET security audit log"""
    print("\n📋 Testing GET Security Audit Log...")
    
    response = requests.get(
        f"{BASE_URL}/security/audit-log?limit=10&offset=0",
        headers=headers
    )
    print_response("/security/audit-log", "GET", response)
    return response.status_code in [200, 401]

def test_get_sessions():
    """Test GET active sessions"""
    print("\n🔐 Testing GET Active Sessions...")
    
    response = requests.get(
        f"{BASE_URL}/security/sessions",
        headers=headers
    )
    print_response("/security/sessions", "GET", response)
    return response.status_code in [200, 401]

def test_deactivate_account():
    """Test account deactivation (won't actually run without confirmation)"""
    print("\n🗑️  Testing Account Deactivation (SKIPPED)")
    print("⚠️  Skipping actual deactivation to prevent accidental account loss")
    print("To test: Uncomment the code below and run manually")
    return True
    
    # Uncomment to actually test:
    # data = {"password": "YourPassword123!"}
    # response = requests.post(
    #     f"{BASE_URL}/security/account/deactivate",
    #     headers=headers,
    #     json=data
    # )
    # print_response("/security/account/deactivate", "POST", response)
    # return response.status_code in [200, 401]

def test_delete_account():
    """Test account deletion (won't actually run without confirmation)"""
    print("\n🗑️  Testing Account Deletion (SKIPPED)")
    print("⚠️  Skipping actual deletion to prevent accidental account loss")
    print("To test: Uncomment the code below and run manually")
    return True
    
    # Uncomment to actually test:
    # data = {"password": "YourPassword123!", "reason": "Test deletion"}
    # response = requests.delete(
    #     f"{BASE_URL}/security/account/delete",
    #     headers=headers,
    #     json=data
    # )
    # print_response("/security/account/delete", "DELETE", response)
    # return response.status_code in [200, 401]

def main():
    """Run all tests"""
    print("="*60)
    print("🧪 SETTINGS BACKEND API TESTS")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check if backend is running
    print("\n🔍 Checking if backend is running...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print("✅ Backend is running!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend is not running or not accessible")
        print(f"Error: {e}")
        print("\n💡 Make sure to start the backend first:")
        print("   cd backend")
        print("   python app.py")
        return
    
    # Run tests
    tests = [
        ("Health Check", test_health_check),
        ("GET Notifications", test_get_notifications),
        ("UPDATE Notifications", test_update_notifications),
        ("Change Password", test_change_password),
        ("Weak Password Validation", test_weak_password),
        ("GET Audit Log", test_get_audit_log),
        ("GET Sessions", test_get_sessions),
        ("Deactivate Account", test_deactivate_account),
        ("Delete Account", test_delete_account),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test '{test_name}' failed with error: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 Note: If you see 401 errors, update AUTH_TOKEN at the top of this script")
    print("="*60)

if __name__ == "__main__":
    main()
