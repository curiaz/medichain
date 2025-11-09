#!/usr/bin/env python3
"""
Simple script to make a user an admin or list admin users
Usage: python make_admin.py [email]
"""

import sys
import os
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

load_dotenv()

try:
    from db.supabase_client import SupabaseClient
    supabase = SupabaseClient()
except Exception as e:
    print(f"❌ Error connecting to Supabase: {e}")
    print("\nMake sure your .env file has SUPABASE_URL and SUPABASE_SERVICE_KEY set")
    sys.exit(1)

def list_admins():
    """List all admin users"""
    try:
        response = supabase.service_client.table("user_profiles").select("*").eq("role", "admin").execute()
        
        if not response.data:
            print("No admin users found.")
            return
        
        print(f"\n✅ Found {len(response.data)} admin user(s):\n")
        for i, user in enumerate(response.data, 1):
            status = "✅ Active" if user.get("is_active") else "❌ Inactive"
            verified = "✓" if user.get("is_verified") else "✗"
            print(f"{i}. {user.get('first_name')} {user.get('last_name')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Status: {status} | Verified: {verified}")
            print(f"   Firebase UID: {user.get('firebase_uid')}")
            print()
    except Exception as e:
        print(f"❌ Error: {e}")

def make_admin(email):
    """Make a user an admin by email"""
    email = email.strip().lower()
    
    try:
        # Find user
        response = supabase.service_client.table("user_profiles").select("*").eq("email", email).execute()
        
        if not response.data:
            print(f"❌ User with email '{email}' not found.")
            print("\n💡 Tip: Make sure the user has signed up first.")
            return
        
        user = response.data[0]
        
        if user.get("role") == "admin":
            print(f"✅ User '{email}' is already an admin.")
            return
        
        # Update role
        update_response = supabase.service_client.table("user_profiles").update({
            "role": "admin"
        }).eq("firebase_uid", user["firebase_uid"]).execute()
        
        if update_response.data:
            print(f"✅ Successfully promoted '{email}' to admin!")
            print(f"   Name: {user.get('first_name')} {user.get('last_name')}")
            print(f"   User can now log in to access the admin dashboard.")
        else:
            print("❌ Failed to update user role.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Make user admin
        email = sys.argv[1]
        make_admin(email)
    else:
        # List all admins
        print("=" * 60)
        print("Admin Users")
        print("=" * 60)
        list_admins()
        print("\n💡 To make a user admin, run:")
        print("   python make_admin.py user@example.com")

