#!/usr/bin/env python3
"""
Create Test Patient Data
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def create_test_patient():
    """Create a test patient with correct schema"""
    print("Creating Test Patient...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # First, let's see what columns exist
        print("Checking user_profiles table structure...")
        try:
            response = supabase.client.table('user_profiles').select('*').limit(1).execute()
            if response.data:
                print("Table structure:", list(response.data[0].keys()))
        except Exception as e:
            print(f"Error checking table: {e}")
        
        # Test patient data with basic fields only
        patient_data = {
            'firebase_uid': 'test_patient_123',
            'email': 'test.patient@example.com',
            'first_name': 'Test',
            'last_name': 'Patient',
            'phone': '+1 (555) 123-4567',
            'role': 'patient'
        }
        
        print("Inserting test patient...")
        response = supabase.client.table('user_profiles').insert(patient_data).execute()
        
        if response.data:
            print("SUCCESS: Test patient created!")
            print(f"  Patient ID: {response.data[0]['id']}")
            print(f"  Firebase UID: {response.data[0]['firebase_uid']}")
            print(f"  Email: {response.data[0]['email']}")
            return True
        else:
            print("ERROR: Failed to create test patient")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_patient_profile():
    """Test getting patient profile"""
    print("\nTesting Patient Profile Retrieval...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # Test the get_patient_profile method
        profile = supabase.get_patient_profile('test_patient_123')
        
        if profile:
            print("SUCCESS: Patient profile retrieved!")
            print(f"  Name: {profile['user_profile']['first_name']} {profile['user_profile']['last_name']}")
            print(f"  Email: {profile['user_profile']['email']}")
            print(f"  Role: {profile['user_profile']['role']}")
            return True
        else:
            print("ERROR: Could not retrieve patient profile")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main function"""
    print("Creating Test Patient Data")
    print("=" * 30)
    
    # Create test patient
    success = create_test_patient()
    
    if success:
        # Test profile retrieval
        test_patient_profile()
    
    print("\nDone!")

if __name__ == "__main__":
    main()

