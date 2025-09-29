#!/usr/bin/env python3
"""
Quick Fix: Create Test Patient with Service Client
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def create_test_patient():
    """Create a test patient using service client"""
    print("Creating Test Patient with Service Client...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # Use service client to bypass RLS
        client = supabase.service_client
        
        # Test patient data
        patient_data = {
            'firebase_uid': 'test_patient_123',
            'email': 'test.patient@example.com',
            'first_name': 'Test',
            'last_name': 'Patient',
            'phone': '+1 (555) 123-4567',
            'role': 'patient'
        }
        
        print("Inserting test patient with service client...")
        response = client.table('user_profiles').insert(patient_data).execute()
        
        if response.data:
            print("SUCCESS: Test patient created!")
            print(f"  Patient ID: {response.data[0]['id']}")
            print(f"  Firebase UID: {response.data[0]['firebase_uid']}")
            return True
        else:
            print("ERROR: Failed to create test patient")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main function"""
    print("Creating Test Patient (Service Client)")
    print("=" * 40)
    
    create_test_patient()
    print("\nDone!")

if __name__ == "__main__":
    main()

