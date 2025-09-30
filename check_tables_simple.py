#!/usr/bin/env python3
"""
Check Database Tables (Simple)
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def check_tables():
    """Check what tables exist in the database"""
    print("Checking Database Tables...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # Try to query different tables to see what exists
        tables_to_check = [
            'user_profiles',
            'patient_medical_info',
            'patient_documents', 
            'patient_privacy_settings',
            'patient_audit_log',
            'medical_records',
            'health_records',
            'appointments',
            'prescriptions'
        ]
        
        existing_tables = []
        
        for table in tables_to_check:
            try:
                response = supabase.service_client.table(table).select('count').execute()
                print(f"OK: {table} - EXISTS")
                existing_tables.append(table)
            except Exception as e:
                print(f"NO: {table} - NOT FOUND")
        
        print(f"\nFound {len(existing_tables)} existing tables:")
        for table in existing_tables:
            print(f"  - {table}")
            
        return existing_tables
            
    except Exception as e:
        print(f"ERROR: {e}")
        return []

def main():
    """Main function"""
    print("Checking Database Tables")
    print("=" * 25)
    
    check_tables()
    print("\nDone!")

if __name__ == "__main__":
    main()

