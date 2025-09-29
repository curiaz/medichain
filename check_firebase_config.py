#!/usr/bin/env python3
"""
Test Firebase Configuration
"""

import os
from dotenv import load_dotenv

def check_firebase_config():
    """Check Firebase configuration"""
    print("Checking Firebase Configuration...")
    print("=" * 35)
    
    # Load .env from backend directory
    load_dotenv('backend/.env')
    
    required_vars = [
        'FIREBASE_PROJECT_ID',
        'FIREBASE_PRIVATE_KEY_ID', 
        'FIREBASE_PRIVATE_KEY',
        'FIREBASE_CLIENT_EMAIL',
        'FIREBASE_CLIENT_ID',
        'FIREBASE_CLIENT_CERT_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"X {var}: Missing")
        else:
            print(f"OK {var}: Set")
    
    if missing_vars:
        print(f"\nX Missing Firebase environment variables: {missing_vars}")
        print("This is likely why Firebase token verification is failing.")
        return False
    else:
        print("\nOK All Firebase environment variables are set!")
        return True

def main():
    """Main function"""
    print("Firebase Configuration Check")
    print("=" * 30)
    
    config_ok = check_firebase_config()
    
    if not config_ok:
        print("\n🔧 To fix this:")
        print("1. Check your .env file in the backend directory")
        print("2. Make sure all Firebase environment variables are set")
        print("3. Restart the backend server after updating .env")

if __name__ == "__main__":
    main()
