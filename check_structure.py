#!/usr/bin/env python3
"""
Check Table Structure
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def check_table_structure():
    """Check the structure of existing tables"""
    print("Checking Table Structure...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # Check user_profiles structure
        print("\n1. user_profiles table:")
        try:
            response = supabase.service_client.table('user_profiles').select('*').limit(1).execute()
            if response.data:
                user = response.data[0]
                print("Columns:", list(user.keys()))
            else:
                print("No data found")
        except Exception as e:
            print(f"Error: {e}")
        
        # Check medical_records structure
        print("\n2. medical_records table:")
        try:
            response = supabase.service_client.table('medical_records').select('*').limit(1).execute()
            if response.data:
                record = response.data[0]
                print("Columns:", list(record.keys()))
            else:
                print("No data found")
        except Exception as e:
            print(f"Error: {e}")
        
        # Check appointments structure
        print("\n3. appointments table:")
        try:
            response = supabase.service_client.table('appointments').select('*').limit(1).execute()
            if response.data:
                appointment = response.data[0]
                print("Columns:", list(appointment.keys()))
            else:
                print("No data found")
        except Exception as e:
            print(f"Error: {e}")
        
        # Check prescriptions structure
        print("\n4. prescriptions table:")
        try:
            response = supabase.service_client.table('prescriptions').select('*').limit(1).execute()
            if response.data:
                prescription = response.data[0]
                print("Columns:", list(prescription.keys()))
            else:
                print("No data found")
        except Exception as e:
            print(f"Error: {e}")
            
    except Exception as e:
        print(f"ERROR: {e}")

def main():
    """Main function"""
    print("Checking Table Structure")
    print("=" * 25)
    
    check_table_structure()
    print("\nDone!")

if __name__ == "__main__":
    main()

