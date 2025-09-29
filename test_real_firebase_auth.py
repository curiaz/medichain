#!/usr/bin/env python3
"""
Test Real Firebase Authentication
"""

import requests
import json

def test_real_firebase_auth():
    """Test with real Firebase token"""
    print("Testing Real Firebase Authentication")
    print("=" * 40)
    
    # This would be your actual Firebase token from the browser
    # You can get this from the browser console when logged in
    print("To test with your real Firebase token:")
    print("1. Open browser console (F12)")
    print("2. Go to Console tab")
    print("3. Run: firebase.auth().currentUser.getIdToken().then(token => console.log(token))")
    print("4. Copy the token and replace 'YOUR_FIREBASE_TOKEN' below")
    print()
    
    # Placeholder for real token
    real_token = "YOUR_FIREBASE_TOKEN"
    
    if real_token == "YOUR_FIREBASE_TOKEN":
        print("❌ Please replace 'YOUR_FIREBASE_TOKEN' with your actual token")
        return False
    
    try:
        headers = {
            'Authorization': f'Bearer {real_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get('http://localhost:5000/api/profile/patient', headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Real Firebase authentication works!")
            user_profile = data['data']['user_profile']
            print(f"Patient: {user_profile['first_name']} {user_profile['last_name']}")
            print(f"Email: {user_profile['email']}")
            print(f"Firebase UID: {user_profile['firebase_uid']}")
            return True
        else:
            print(f"ERROR: {response.text}")
            return False
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return False

def main():
    """Main function"""
    print("Real Firebase Authentication Test")
    print("=" * 35)
    
    success = test_real_firebase_auth()
    
    if success:
        print("\n✅ Real Firebase authentication is working!")
    else:
        print("\n❌ Real Firebase authentication needs to be tested with actual token")

if __name__ == "__main__":
    main()

