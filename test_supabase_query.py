#!/usr/bin/env python3
"""
Test Supabase Query Directly
"""

import requests
import json

def test_supabase_query():
    """Test Supabase query directly"""
    print("Testing Supabase Query")
    print("=" * 25)
    
    # Your Firebase UID from the database
    firebase_uid = "XFsbgVlSBzcXdtq33J2Y6QZT2VB2"
    
    print(f"Testing query for Firebase UID: {firebase_uid}")
    
    # Supabase URL and key
    supabase_url = "https://royvcmfbcghamnbnxdgb.supabase.co"
    supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveXZjbWZiY2doYW1uYm54ZGdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI4MDQwOTksImV4cCI6MjA2ODM4MDA5OX0.By2hJPp_2vn141HOPUDE-svm1m1sKtqhfHNSYTuf658"
    
    # Test query
    url = f"{supabase_url}/rest/v1/user_profiles"
    headers = {
        'apikey': supabase_key,
        'Authorization': f'Bearer {supabase_key}',
        'Content-Type': 'application/json'
    }
    
    params = {
        'firebase_uid': f'eq.{firebase_uid}',
        'select': '*'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data:
                print("SUCCESS: User profile found!")
                print(f"Name: {data[0].get('first_name', 'N/A')} {data[0].get('last_name', 'N/A')}")
                print(f"Email: {data[0].get('email', 'N/A')}")
                return True
            else:
                print("ERROR: No user profile found")
                return False
        else:
            print(f"ERROR: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function"""
    print("Supabase Query Test")
    print("=" * 20)
    
    success = test_supabase_query()
    
    if success:
        print("\n✅ Supabase query works!")
        print("The issue might be in the frontend SupabaseService.")
    else:
        print("\n❌ Supabase query failed.")
        print("Check Supabase configuration or RLS policies.")

if __name__ == "__main__":
    main()

