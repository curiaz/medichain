#!/usr/bin/env python3
"""
Test Script for Delete Account Feature
Tests the delete account API endpoint
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:5000"
API_ENDPOINT = f"{BASE_URL}/api/profile/delete-account"

def test_delete_account_without_auth():
    """Test 1: Delete account without authentication (should fail)"""
    print("\n" + "="*60)
    print("TEST 1: Delete Account Without Authentication")
    print("="*60)
    
    try:
        response = requests.delete(API_ENDPOINT)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("✅ PASSED: Correctly rejected unauthenticated request")
        else:
            print("❌ FAILED: Should have returned 401")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_delete_account_with_invalid_token():
    """Test 2: Delete account with invalid token (should fail)"""
    print("\n" + "="*60)
    print("TEST 2: Delete Account With Invalid Token")
    print("="*60)
    
    headers = {
        "Authorization": "Bearer invalid_token_12345",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.delete(API_ENDPOINT, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 401:
            print("✅ PASSED: Correctly rejected invalid token")
        else:
            print("❌ FAILED: Should have returned 401")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_backend_health():
    """Test 0: Check if backend is running"""
    print("\n" + "="*60)
    print("TEST 0: Backend Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print("❌ Backend health check failed")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend. Make sure it's running!")
        print("   Run: cd backend && python app.py")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def test_endpoint_exists():
    """Test 3: Check if delete account endpoint exists"""
    print("\n" + "="*60)
    print("TEST 3: Check Delete Account Endpoint Exists")
    print("="*60)
    
    try:
        # Try with OPTIONS to check if endpoint exists
        response = requests.options(API_ENDPOINT)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 404:
            print("✅ PASSED: Delete account endpoint exists")
        else:
            print("❌ FAILED: Endpoint not found (404)")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def print_usage_instructions():
    """Print instructions for manual testing"""
    print("\n" + "="*60)
    print("MANUAL TESTING INSTRUCTIONS")
    print("="*60)
    print("\n📝 To test the complete delete account flow:")
    print("\n1. Start the backend server:")
    print("   cd backend")
    print("   python app.py")
    print("\n2. Start the frontend:")
    print("   npm start")
    print("\n3. Login as a test patient user")
    print("\n4. Navigate to: Profile → Account Security tab")
    print("\n5. Scroll to the 'Danger Zone' section")
    print("\n6. Click 'Delete Account' button")
    print("\n7. Confirm in the first dialog")
    print("\n8. Type 'DELETE' in the second dialog")
    print("\n9. Verify:")
    print("   ✅ Account is deleted from database")
    print("   ✅ Account is deleted from Firebase")
    print("   ✅ User is redirected to home page")
    print("   ✅ Local storage is cleared")
    print("\n" + "="*60)

def main():
    """Run all tests"""
    print("\n🧪 DELETE ACCOUNT FEATURE - TEST SUITE")
    print("=" * 60)
    print("Testing the delete account API endpoint")
    
    # Check if backend is running
    if not test_backend_health():
        print("\n❌ Cannot proceed with tests. Please start the backend server.")
        return
    
    # Run automated tests
    test_delete_account_without_auth()
    test_delete_account_with_invalid_token()
    test_endpoint_exists()
    
    # Print manual testing instructions
    print_usage_instructions()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print("Automated tests completed.")
    print("Please perform manual testing to verify complete functionality.")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
