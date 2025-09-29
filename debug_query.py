#!/usr/bin/env python3
"""
Debug Database Query
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def debug_query():
    """Debug the database query"""
    print("Debugging Database Query...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # Test the exact query from get_patient_profile
        real_patient_uid = 'xeA5Dv1708a2YVyxO4I1HBpHnBv2'
        
        print(f"Querying user_profiles table for firebase_uid: {real_patient_uid}")
        
        # Use the same client as get_patient_profile (not service client)
        response = supabase.client.table('user_profiles').select('*').eq('firebase_uid', real_patient_uid).execute()
        
        print(f"Query result: {response}")
        print(f"Data: {response.data}")
        
        if response.data:
            print("SUCCESS: Found user!")
            user = response.data[0]
            print(f"  ID: {user['id']}")
            print(f"  Firebase UID: {user['firebase_uid']}")
            print(f"  Name: {user['first_name']} {user['last_name']}")
            print(f"  Email: {user['email']}")
            print(f"  Role: {user['role']}")
        else:
            print("ERROR: No user found")
            
            # Let's try with service client
            print("\nTrying with service client...")
            service_response = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', real_patient_uid).execute()
            print(f"Service client result: {service_response.data}")
            
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    """Main function"""
    print("Debugging Database Query")
    print("=" * 25)
    
    debug_query()
    print("\nDone!")

if __name__ == "__main__":
    main()

