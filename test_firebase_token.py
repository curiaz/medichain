#!/usr/bin/env python3
"""
Test Firebase Token Verification
"""

import requests
import json

def test_firebase_token_verification():
    """Test Firebase token verification with a real token"""
    print("Testing Firebase Token Verification")
    print("=" * 40)
    
    print("To get your Firebase token:")
    print("1. Open browser console (F12)")
    print("2. Go to Console tab")
    print("3. Run this command:")
    print("   firebase.auth().currentUser.getIdToken().then(token => console.log('Token:', token))")
    print("4. Copy the token and replace 'YOUR_TOKEN_HERE' below")
    print()
    
    # This would be your actual Firebase token
    token = "YOUR_TOKEN_HERE"
    
    if token == "YOUR_TOKEN_HERE":
        print("❌ Please replace 'YOUR_TOKEN_HERE' with your actual Firebase token")
        print("   You can get it from the browser console as shown above")
        return False
    
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        print(f"Testing with token: {token[:20]}...")
        response = requests.get('http://localhost:5000/api/profile/patient', headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Firebase token verification works!")
            user_profile = data['data']['user_profile']
            print(f"Patient: {user_profile['first_name']} {user_profile['last_name']}")
            print(f"Email: {user_profile['email']}")
            return True
        else:
            print("FAILED: Firebase token verification failed")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    print("Firebase Token Verification Test")
    print("=" * 35)
    
    success = test_firebase_token_verification()
    
    if success:
        print("\n✅ Firebase authentication is working!")
    else:
        print("\n❌ Firebase authentication needs debugging")

if __name__ == "__main__":
    main()

