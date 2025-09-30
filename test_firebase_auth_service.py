#!/usr/bin/env python3
"""
Test Firebase Auth Service Directly
"""

import sys
import os
sys.path.append('backend')

def test_firebase_auth_service():
    """Test Firebase auth service directly"""
    print("Testing Firebase Auth Service")
    print("=" * 30)
    
    try:
        from auth.firebase_auth import firebase_auth_service
        print("✅ Firebase auth service imported successfully")
        
        # Test with a fake token to see what error we get
        result = firebase_auth_service.verify_token("fake_token_123")
        print(f"Fake token test result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing Firebase auth service: {e}")
        return False

def main():
    """Main function"""
    print("Firebase Auth Service Test")
    print("=" * 25)
    
    success = test_firebase_auth_service()
    
    if success:
        print("\n✅ Firebase auth service is working!")
    else:
        print("\n❌ Firebase auth service has issues")

if __name__ == "__main__":
    main()

