#!/usr/bin/env python3
"""
Test Supabase RLS Policies
"""

import requests
import json

def test_rls_policies():
    """Test RLS policies"""
    print("Testing Supabase RLS Policies")
    print("=" * 30)
    
    # Supabase URL and keys
    supabase_url = "https://royvcmfbcghamnbnxdgb.supabase.co"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveXZjbWZiY2doYW1uYm54ZGdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI4MDQwOTksImV4cCI6MjA2ODM4MDA5OX0.By2hJPp_2vn141HOPUDE-svm1m1sKtqhfHNSYTuf658"
    service_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveXZjbWZiY2doYW1uYm54ZGdiIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MjgwNDA5OSwiZXhwIjoyMDY4MzgwMDk5fQ.QP9kO33v4sME_36xqbPpY8ZiEe7pFsaPbz0zwD7Ak8M"
    
    firebase_uid = "XFsbgVlSBzcXdtq33J2Y6QZT2VB2"
    
    print("1. Testing with ANON key (what frontend uses):")
    test_with_key(anon_key, "ANON", firebase_uid)
    
    print("\n2. Testing with SERVICE key (bypasses RLS):")
    test_with_key(service_key, "SERVICE", firebase_uid)

def test_with_key(key, key_type, firebase_uid):
    """Test query with specific key"""
    supabase_url = "https://royvcmfbcghamnbnxdgb.supabase.co"
    
    url = f"{supabase_url}/rest/v1/user_profiles"
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'firebase_uid': f'eq.{firebase_uid}',
        'select': '*'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print(f"   SUCCESS: Found user with {key_type} key")
                print(f"   Name: {data[0].get('first_name', 'N/A')} {data[0].get('last_name', 'N/A')}")
            else:
                print(f"   EMPTY: No data returned with {key_type} key")
        else:
            print(f"   ERROR: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"   Exception: {e}")

def main():
    """Main function"""
    print("Supabase RLS Policy Test")
    print("=" * 25)
    
    test_rls_policies()
    
    print("\nConclusion:")
    print("- If ANON key fails but SERVICE key works: RLS is blocking")
    print("- If both fail: User doesn't exist or other issue")
    print("- If both work: RLS is not the issue")

if __name__ == "__main__":
    main()

