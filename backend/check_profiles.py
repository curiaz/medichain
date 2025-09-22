#!/usr/bin/env python3
"""
Check user profiles in database
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from db.supabase_client import SupabaseClient

def main():
    supabase = SupabaseClient()
    try:
        response = supabase.service_client.table('user_profiles').select('firebase_uid, email, first_name, last_name, role').execute()

        print("📊 All user profiles in database:")
        print(f"Found {len(response.data)} profiles")
        print()

        for i, profile in enumerate(response.data, 1):
            print(f"Profile {i}:")
            print(f"  UID: {profile['firebase_uid']}")
            print(f"  Email: {profile['email']}")
            print(f"  Name: {profile['first_name']} {profile['last_name']}")
            print(f"  Role: {profile['role']}")
            print()

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
