#!/usr/bin/env python3
"""
Simple Database Connection Test
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_database_connection():
    """Test the database connection"""
    print("Testing Database Connection...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        # Test Supabase connection
        supabase = SupabaseClient()
        
        # Try to query the user_profiles table
        response = supabase.client.table('user_profiles').select('count').execute()
        print("SUCCESS: Supabase connection working!")
        
        # Check if we have any users
        users = supabase.client.table('user_profiles').select('*').limit(5).execute()
        if users.data:
            print(f"Found {len(users.data)} users in database")
            for user in users.data:
                print(f"  - {user.get('first_name', 'N/A')} {user.get('last_name', 'N/A')} ({user.get('email', 'N/A')})")
        else:
            print("No users found in database")
        
        return True
        
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return False

def test_firebase_auth():
    """Test Firebase authentication"""
    print("\nTesting Firebase Authentication...")
    
    try:
        from auth.firebase_auth import firebase_auth_service
        
        # Test Firebase initialization
        if firebase_auth_service.app:
            print("SUCCESS: Firebase Admin SDK initialized!")
            return True
        else:
            print("ERROR: Firebase Admin SDK not initialized")
            return False
            
    except Exception as e:
        print(f"ERROR: Firebase authentication failed: {e}")
        return False

def create_test_patient():
    """Create a test patient"""
    print("\nCreating Test Patient...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # Test patient data
        patient_data = {
            'firebase_uid': 'test_patient_123',
            'email': 'test.patient@example.com',
            'first_name': 'Test',
            'last_name': 'Patient',
            'phone': '+1 (555) 123-4567',
            'role': 'patient',
            'is_active': True,
            'is_verified': True
        }
        
        # Insert test patient
        response = supabase.client.table('user_profiles').insert(patient_data).execute()
        
        if response.data:
            print("SUCCESS: Test patient created!")
            print(f"  Patient ID: {response.data[0]['id']}")
            return True
        else:
            print("ERROR: Failed to create test patient")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main test function"""
    print("MediChain Database Test")
    print("=" * 30)
    
    # Test database connection
    db_ok = test_database_connection()
    
    # Test Firebase
    firebase_ok = test_firebase_auth()
    
    # Create test patient if database is working
    if db_ok:
        create_test_patient()
    
    print("\nResults:")
    print(f"  Database: {'OK' if db_ok else 'FAILED'}")
    print(f"  Firebase: {'OK' if firebase_ok else 'FAILED'}")
    
    if db_ok and firebase_ok:
        print("\nSUCCESS: Everything is working!")
    else:
        print("\nISSUES FOUND: Check your configuration")

if __name__ == "__main__":
    main()

