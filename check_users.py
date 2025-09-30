#!/usr/bin/env python3
"""
Check What Users Exist in Database
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def check_existing_users():
    """Check what users exist in the database"""
    print("Checking Existing Users in Database...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # Get all users
        response = supabase.service_client.table('user_profiles').select('*').execute()
        
        if response.data:
            print(f"SUCCESS: Found {len(response.data)} users in database!")
            for i, user in enumerate(response.data):
                print(f"  User {i+1}:")
                print(f"    ID: {user['id']}")
                print(f"    Firebase UID: {user.get('firebase_uid', 'N/A')}")
                print(f"    Name: {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')}")
                print(f"    Email: {user.get('email', 'N/A')}")
                print(f"    Role: {user.get('role', 'N/A')}")
                print()
            return True
        else:
            print("ERROR: No users found in database")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def create_new_test_patient():
    """Create a new test patient with different UID"""
    print("\nCreating New Test Patient...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        client = supabase.service_client
        
        # New test patient data
        patient_data = {
            'firebase_uid': 'test_patient_456',
            'email': 'test.patient2@example.com',
            'first_name': 'Test',
            'last_name': 'Patient2',
            'phone': '+1 (555) 123-4567',
            'role': 'patient'
        }
        
        print("Inserting new test patient...")
        response = client.table('user_profiles').insert(patient_data).execute()
        
        if response.data:
            print("SUCCESS: New test patient created!")
            print(f"  Patient ID: {response.data[0]['id']}")
            print(f"  Firebase UID: {response.data[0]['firebase_uid']}")
            return True
        else:
            print("ERROR: Failed to create new test patient")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main function"""
    print("Checking Database Users")
    print("=" * 25)
    
    # Check existing users
    check_existing_users()
    
    # Create new test patient
    create_new_test_patient()
    
    print("\nDone!")

if __name__ == "__main__":
    main()

