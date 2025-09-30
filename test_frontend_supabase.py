#!/usr/bin/env python3
"""
Test Frontend Supabase Access
"""

import requests
import json

def test_frontend_supabase_access():
    """Test if we can access user profiles like the frontend does"""
    print("Testing Frontend Supabase Access")
    print("=" * 35)
    
    # Same configuration as frontend
    supabase_url = "https://royvcmfbcghamnbnxdgb.supabase.co"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveXZjbWZiY2doYW1uYm54ZGdiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI4MDQwOTksImV4cCI6MjA2ODM4MDA5OX0.By2hJPp_2vn141HOPUDE-svm1m1sKtqhfHNSYTuf658"
    
    firebase_uid = "XFsbgVlSBzcXdtq33J2Y6QZT2VB2"
    
    print(f"Testing access for Firebase UID: {firebase_uid}")
    
    # Test different query approaches
    test_queries = [
        {
            'name': 'Direct firebase_uid filter',
            'params': {'firebase_uid': f'eq.{firebase_uid}'}
        },
        {
            'name': 'Simple select all',
            'params': {}
        },
        {
            'name': 'Select with limit',
            'params': {'limit': '1'}
        }
    ]
    
    for test in test_queries:
        print(f"\n{test['name']}:")
        test_query(supabase_url, anon_key, test['params'])

def test_query(supabase_url, anon_key, params):
    """Test a specific query"""
    url = f"{supabase_url}/rest/v1/user_profiles"
    headers = {
        'apikey': anon_key,
        'Authorization': f'Bearer {anon_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Results: {len(data)} records")
            if data:
                print(f"   First record: {data[0].get('first_name', 'N/A')} {data[0].get('last_name', 'N/A')}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   Exception: {e}")

def main():
    """Main function"""
    print("Frontend Supabase Access Test")
    print("=" * 30)
    
    test_frontend_supabase_access()
    
    print("\nIf all queries return empty results, RLS is blocking all access.")
    print("If some queries work, we can adjust the frontend query.")

if __name__ == "__main__":
    main()

