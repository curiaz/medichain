#!/usr/bin/env python3
"""
Test Frontend-Backend Connection
"""

import requests
import json

def test_cors():
    """Test CORS headers"""
    print("Testing CORS Headers...")
    
    try:
        # Test preflight request
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Authorization'
        }
        
        response = requests.options('http://localhost:5000/api/profile/patient', headers=headers)
        print(f"CORS Preflight Status: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
        return True
        
    except Exception as e:
        print(f"CORS Error: {e}")
        return False

def test_direct_call():
    """Test direct API call from frontend perspective"""
    print("\nTesting Direct API Call...")
    
    try:
        headers = {
            'Authorization': 'Bearer test_token_123',
            'Content-Type': 'application/json',
            'Origin': 'http://localhost:3000'
        }
        
        response = requests.get('http://localhost:5000/api/profile/patient', headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: API call works!")
            print(f"Patient: {data['data']['user_profile']['first_name']} {data['data']['user_profile']['last_name']}")
            return True
        else:
            print(f"ERROR: {response.text}")
            return False
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return False

def main():
    """Main function"""
    print("Testing Frontend-Backend Connection")
    print("=" * 35)
    
    cors_ok = test_cors()
    api_ok = test_direct_call()
    
    print(f"\nResults:")
    print(f"  CORS: {'OK' if cors_ok else 'FAILED'}")
    print(f"  API: {'OK' if api_ok else 'FAILED'}")
    
    if cors_ok and api_ok:
        print("\nBackend is working correctly!")
        print("The issue might be in the frontend code.")
    else:
        print("\nBackend has issues that need to be fixed.")

if __name__ == "__main__":
    main()

