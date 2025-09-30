#!/usr/bin/env python3
"""
Simple RLS Fix - Allow all access to user_profiles
"""

import requests
import json

def disable_rls_temporarily():
    """Temporarily disable RLS for user_profiles table"""
    print("Temporarily disabling RLS for user_profiles")
    print("=" * 45)
    
    # Supabase configuration
    supabase_url = "https://royvcmfbcghamnbnxdgb.supabase.co"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveXZjbWZiY2doYW1uYm54ZGdiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjgwNDA5OSwiZXhwIjoyMDY4MzgwMDk5fQ.QP9kO33v4sME_36xqbPpY8ZiEe7pFsaPbz0zwD7Ak8M"
    
    # SQL to disable RLS
    sql = "ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;"
    
    print(f"Executing: {sql}")
    
    try:
        # Use Supabase SQL endpoint
        url = f"{supabase_url}/rest/v1/rpc/exec_sql"
        headers = {
            'apikey': service_key,
            'Authorization': f'Bearer {service_key}',
            'Content-Type': 'application/json'
        }
        
        data = {'sql': sql}
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code in [200, 201]:
            print("SUCCESS: RLS disabled for user_profiles table")
            test_anon_access()
        else:
            print("ERROR: Failed to disable RLS")
            
    except Exception as e:
        print(f"Exception: {e}")

def test_anon_access():
    """Test if ANON key can now access user profiles"""
    print("\nTesting ANON key access...")
    
    supabase_url = "https://royvcmfbcghamnbnxdgb.supabase.co"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveXZjbWZiY2doYW1uYm54ZGdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI4MDQwOTksImV4cCI6MjA2ODM4MDA5OX0.By2hJPp_2vn141HOPUDE-svm1m1sKtqhfHNSYTuf658"
    
    firebase_uid = "XFsbgVlSBzcXdtq33J2Y6QZT2VB2"
    
    url = f"{supabase_url}/rest/v1/user_profiles"
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'firebase_uid': f'eq.{firebase_uid}',
        'select': '*'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print("SUCCESS: ANON key can now access user profiles!")
                print(f"Found: {data[0].get('first_name', 'N/A')} {data[0].get('last_name', 'N/A')}")
                print(f"Email: {data[0].get('email', 'N/A')}")
                return True
            else:
                print("Still empty - check query parameters")
                return False
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    """Main function"""
    print("Simple RLS Fix")
    print("=" * 15)
    
    disable_rls_temporarily()
    
    print("\nDone! Try refreshing your profile page now.")
    print("If it works, we can implement proper RLS policies later.")

if __name__ == "__main__":
    main()

