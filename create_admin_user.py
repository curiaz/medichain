#!/usr/bin/env python3
"""
Utility script to create an admin user or promote an existing user to admin
Run this script to set up your first admin user or promote existing users
"""

import sys
import os
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

load_dotenv()

from db.supabase_client import SupabaseClient
from auth.firebase_auth import FirebaseAuthService
import getpass

def create_admin_user():
    """Create a new admin user or promote existing user"""
    print("=" * 60)
    print("Admin User Setup Utility")
    print("=" * 60)
    print()
    
    # Initialize services
    try:
        supabase = SupabaseClient()
        firebase_auth = FirebaseAuthService()
        print("✅ Connected to database and Firebase")
    except Exception as e:
        print(f"❌ Error connecting to services: {e}")
        return
    
    print()
    print("Choose an option:")
    print("1. Create a new admin user (with Firebase account)")
    print("2. Promote an existing user to admin")
    print("3. List all admin users")
    print("4. Exit")
    print()
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == "1":
        create_new_admin(supabase, firebase_auth)
    elif choice == "2":
        promote_existing_user(supabase)
    elif choice == "3":
        list_admin_users(supabase)
    elif choice == "4":
        print("Exiting...")
        return
    else:
        print("❌ Invalid choice")
        return


def create_new_admin(supabase, firebase_auth):
    """Create a new admin user"""
    print()
    print("-" * 60)
    print("Create New Admin User")
    print("-" * 60)
    print()
    
    email = input("Enter email: ").strip().lower()
    if not email:
        print("❌ Email is required")
        return
    
    # Check if user already exists
    existing = supabase.service_client.table("user_profiles").select("*").eq("email", email).execute()
    if existing.data:
        print(f"❌ User with email {email} already exists")
        promote = input("Would you like to promote this user to admin? (y/n): ").strip().lower()
        if promote == 'y':
            promote_user_to_admin(supabase, existing.data[0])
        return
    
    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name: ").strip()
    phone = input("Enter phone (optional): ").strip() or None
    
    print()
    print("Creating Firebase account...")
    print("You'll need to create a password for Firebase authentication.")
    password = getpass.getpass("Enter password (min 6 characters): ")
    
    if len(password) < 6:
        print("❌ Password must be at least 6 characters")
        return
    
    try:
        # Create Firebase user
        firebase_user = firebase_auth.create_user_with_email_password(email, password)
        
        if not firebase_user.get("success"):
            print(f"❌ Failed to create Firebase user: {firebase_user.get('error')}")
            return
        
        firebase_uid = firebase_user["user"]["uid"]
        print(f"✅ Firebase user created: {firebase_uid}")
        
        # Create user profile in Supabase
        user_data = {
            "firebase_uid": firebase_uid,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "role": "admin",
            "is_active": True,
            "is_verified": True
        }
        
        response = supabase.service_client.table("user_profiles").insert(user_data).execute()
        
        if response.data:
            print()
            print("✅ Admin user created successfully!")
            print(f"   Email: {email}")
            print(f"   Name: {first_name} {last_name}")
            print(f"   Firebase UID: {firebase_uid}")
            print()
            print("You can now log in with this account to access the admin dashboard.")
        else:
            print("❌ Failed to create user profile in database")
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")


def promote_existing_user(supabase):
    """Promote an existing user to admin"""
    print()
    print("-" * 60)
    print("Promote Existing User to Admin")
    print("-" * 60)
    print()
    
    email = input("Enter user email to promote: ").strip().lower()
    if not email:
        print("❌ Email is required")
        return
    
    # Find user
    response = supabase.service_client.table("user_profiles").select("*").eq("email", email).execute()
    
    if not response.data:
        print(f"❌ User with email {email} not found")
        return
    
    user = response.data[0]
    
    if user.get("role") == "admin":
        print(f"✅ User {email} is already an admin")
        return
    
    print()
    print(f"Found user: {user.get('first_name')} {user.get('last_name')} ({email})")
    print(f"Current role: {user.get('role')}")
    print()
    
    confirm = input("Promote this user to admin? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled")
        return
    
    promote_user_to_admin(supabase, user)


def promote_user_to_admin(supabase, user):
    """Promote a user to admin role"""
    try:
        firebase_uid = user["firebase_uid"]
        response = supabase.service_client.table("user_profiles").update({
            "role": "admin"
        }).eq("firebase_uid", firebase_uid).execute()
        
        if response.data:
            print()
            print("✅ User promoted to admin successfully!")
            print(f"   Email: {user.get('email')}")
            print(f"   Name: {user.get('first_name')} {user.get('last_name')}")
            print()
            print("User can now log in to access the admin dashboard.")
        else:
            print("❌ Failed to update user role")
    except Exception as e:
        print(f"❌ Error promoting user: {e}")


def list_admin_users(supabase):
    """List all admin users"""
    print()
    print("-" * 60)
    print("Admin Users")
    print("-" * 60)
    print()
    
    try:
        response = supabase.service_client.table("user_profiles").select("*").eq("role", "admin").execute()
        
        if not response.data:
            print("No admin users found")
            return
        
        print(f"Found {len(response.data)} admin user(s):\n")
        for i, user in enumerate(response.data, 1):
            print(f"{i}. {user.get('first_name')} {user.get('last_name')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Status: {'Active' if user.get('is_active') else 'Inactive'}")
            print(f"   Verified: {'Yes' if user.get('is_verified') else 'No'}")
            print()
    except Exception as e:
        print(f"❌ Error listing admin users: {e}")


if __name__ == "__main__":
    try:
        create_admin_user()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

