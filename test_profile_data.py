#!/usr/bin/env python3
"""
Test Patient Profile Retrieval
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_profile_retrieval():
    """Test getting patient profile directly"""
    print("Testing Patient Profile Retrieval...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # Test the get_patient_profile method directly
        print("Getting profile for firebase_uid: test_patient_123")
        profile = supabase.get_patient_profile('test_patient_123')
        
        if profile:
            print("SUCCESS: Patient profile retrieved!")
            print(f"  Name: {profile['user_profile']['first_name']} {profile['user_profile']['last_name']}")
            print(f"  Email: {profile['user_profile']['email']}")
            print(f"  Role: {profile['user_profile']['role']}")
            print(f"  Phone: {profile['user_profile'].get('phone', 'N/A')}")
            return True
        else:
            print("ERROR: Could not retrieve patient profile")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_database_query():
    """Test direct database query"""
    print("\nTesting Direct Database Query...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # Test direct query
        response = supabase.client.table('user_profiles').select('*').eq('firebase_uid', 'test_patient_123').execute()
        
        if response.data:
            print("SUCCESS: Found user in database!")
            user = response.data[0]
            print(f"  ID: {user['id']}")
            print(f"  Firebase UID: {user['firebase_uid']}")
            print(f"  Name: {user['first_name']} {user['last_name']}")
            print(f"  Email: {user['email']}")
            print(f"  Role: {user['role']}")
            return True
        else:
            print("ERROR: No user found with firebase_uid: test_patient_123")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main function"""
    print("Testing Patient Profile Data Retrieval")
    print("=" * 40)
    
    # Test direct database query
    db_ok = test_database_query()
    
    if db_ok:
        # Test profile retrieval method
        test_profile_retrieval()
    
    print("\nDone!")

if __name__ == "__main__":
    main()

