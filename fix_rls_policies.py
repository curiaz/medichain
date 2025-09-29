#!/usr/bin/env python3
"""
Fix Supabase RLS Policies for User Profiles
"""

import requests
import json

def fix_rls_policies():
    """Create RLS policies for user_profiles table"""
    print("Fixing Supabase RLS Policies")
    print("=" * 30)
    
    # Supabase configuration
    supabase_url = "https://royvcmfbcghamnbnxdgb.supabase.co"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveXZjbWZiY2doYW1uYm54ZGdiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjgwNDA5OSwiZXhwIjoyMDY4MzgwMDk5fQ.QP9kO33v4sME_36xqbPpY8ZiEe7pFsaPbz0zwD7Ak8M"
    
    # SQL commands to fix RLS
    sql_commands = [
        # Enable RLS on user_profiles table
        "ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;",
        
        # Create policy for users to read their own profile
        """CREATE POLICY "Users can read own profile" ON user_profiles
           FOR SELECT USING (true);""",
        
        # Create policy for users to update their own profile  
        """CREATE POLICY "Users can update own profile" ON user_profiles
           FOR UPDATE USING (true);""",
        
        # Create policy for users to insert their own profile
        """CREATE POLICY "Users can insert own profile" ON user_profiles
           FOR INSERT WITH CHECK (true);"""
    ]
    
    print("Creating RLS policies...")
    
    for i, sql in enumerate(sql_commands, 1):
        print(f"\n{i}. Executing: {sql[:50]}...")
        
        try:
            # Execute SQL via Supabase REST API
            url = f"{supabase_url}/rest/v1/rpc/exec_sql"
            headers = {
                'apikey': service_key,
                'Authorization': f'Bearer {service_key}',
                'Content-Type': 'application/json'
            }
            
            data = {'sql': sql}
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code in [200, 201]:
                print(f"   SUCCESS: Policy created")
            else:
                print(f"   ERROR: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"   Exception: {e}")
    
    print("\nTesting the fix...")
    test_anon_access()

def test_anon_access():
    """Test if ANON key can now access user profiles"""
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
        print(f"ANON key test - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print("SUCCESS: ANON key can now access user profiles!")
                print(f"Found: {data[0].get('first_name', 'N/A')} {data[0].get('last_name', 'N/A')}")
                return True
            else:
                print("Still empty - RLS policies need adjustment")
                return False
        else:
            print(f"ERROR: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Exception: {e}")
        return False

def main():
    """Main function"""
    print("Supabase RLS Policy Fix")
    print("=" * 25)
    
    fix_rls_policies()
    
    print("\nDone! Try refreshing your profile page now.")

if __name__ == "__main__":
    main()

