#!/usr/bin/env python3
"""
Test Frontend-Backend Connection with Real Auth
"""

import requests
import json

def test_api_without_auth():
    """Test API without authentication"""
    print("Testing API without authentication...")
    
    try:
        response = requests.get('http://localhost:5000/api/profile/patient')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 401  # Should require auth
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_api_with_fake_token():
    """Test API with fake token"""
    print("\nTesting API with fake token...")
    
    try:
        headers = {
            'Authorization': 'Bearer fake_token_123',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('http://localhost:5000/api/profile/patient', headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 401  # Should reject fake token
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_backend_logs():
    """Check if backend is running and logging errors"""
    print("\nBackend Status Check:")
    print("1. Is the backend server running on port 5000?")
    print("2. Check backend terminal for any error messages")
    print("3. Look for Firebase initialization errors")
    print("4. Check for token verification errors")

def main():
    """Main function"""
    print("Frontend-Backend Connection Debug")
    print("=" * 35)
    
    auth_ok = test_api_without_auth()
    fake_token_ok = test_api_with_fake_token()
    
    print(f"\nResults:")
    print(f"  No Auth (should be 401): {'OK' if auth_ok else 'FAILED'}")
    print(f"  Fake Token (should be 401): {'OK' if fake_token_ok else 'FAILED'}")
    
    if auth_ok and fake_token_ok:
        print("\n✅ Backend is responding correctly!")
        print("The issue is likely with Firebase token verification.")
        test_backend_logs()
    else:
        print("\n❌ Backend has issues.")

if __name__ == "__main__":
    main()

