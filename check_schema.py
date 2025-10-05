#!/usr/bin/env python3
"""
Check actual database schema and available columns
"""

import os
import sys

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from db.supabase_client import SupabaseClient
except ImportError as e:
    print(f"❌ Error importing SupabaseClient: {e}")
    sys.exit(1)

def check_schema():
    """Check the actual database schema"""
    
    print("🔍 Checking Database Schema")
    print("=" * 50)
    
    try:
        supabase = SupabaseClient()
        
        # Get a sample user record to see available columns
        sample_response = supabase.service_client.table('user_profiles').select('*').limit(1).execute()
        
        if sample_response.data:
            user = sample_response.data[0]
            print("📋 Available columns in user_profiles table:")
            for key, value in user.items():
                print(f"   • {key}: {type(value).__name__}")
            
            print(f"\n👤 Sample user data:")
            for key, value in user.items():
                if key not in ['firebase_uid', 'email']:  # Don't show sensitive data
                    print(f"   • {key}: {value}")
        else:
            print("❌ No user data found")
        
        # Check if medical records table exists and its structure
        print(f"\n🏥 Checking medical_records table...")
        try:
            medical_response = supabase.service_client.table('medical_records').select('*').limit(1).execute()
            if medical_response.data:
                print("✅ medical_records table exists")
                record = medical_response.data[0]
                print("📋 Available columns in medical_records table:")
                for key in record.keys():
                    print(f"   • {key}")
            else:
                print("ℹ️ medical_records table exists but is empty")
        except Exception as e:
            print(f"❌ medical_records table error: {e}")
        
        # Check AI diagnoses table
        print(f"\n🤖 Checking ai_diagnoses table...")
        try:
            ai_response = supabase.service_client.table('ai_diagnoses').select('*').limit(1).execute()
            if ai_response.data:
                print("✅ ai_diagnoses table exists and has data")
                record = ai_response.data[0]
                print("📋 Available columns in ai_diagnoses table:")
                for key in record.keys():
                    print(f"   • {key}")
            else:
                print("ℹ️ ai_diagnoses table exists but is empty")
        except Exception as e:
            print(f"❌ ai_diagnoses table error: {e}")
            
    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    check_schema()