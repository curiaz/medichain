#!/usr/bin/env python3
"""
Check and delete users from Firebase and Database
"""

import os
import sys
from dotenv import load_dotenv

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

load_dotenv()

from db.supabase_client import SupabaseClient
from auth.firebase_auth import FirebaseAuthService
from firebase_admin import auth as firebase_auth

def check_and_delete():
    """Check for users and delete them"""
    emails = ['bosx1negamer25@gmail.com', 'bruh.telev@gmail.com']
    
    # Initialize services
    try:
        supabase = SupabaseClient()
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"❌ Error initializing Supabase: {e}")
        return
    
    try:
        firebase_service = FirebaseAuthService()
        print("✅ Firebase Admin initialized")
    except Exception as e:
        print(f"⚠️  Warning: Firebase Admin not initialized: {e}")
        firebase_service = None
    
    for email in emails:
        print(f"\n{'='*60}")
        print(f"Checking: {email}")
        print(f"{'='*60}")
        
        # Check database (case-insensitive)
        try:
            # Try exact match first
            user_response = supabase.service_client.table("user_profiles").select("id, firebase_uid, email").ilike("email", email).execute()
            
            if user_response.data:
                for user in user_response.data:
                    print(f"📋 Found in database:")
                    print(f"   - ID: {user.get('id')}")
                    print(f"   - Firebase UID: {user.get('firebase_uid')}")
                    print(f"   - Email: {user.get('email')}")
                    
                    user_id = user.get("id")
                    firebase_uid = user.get("firebase_uid")
                    
                    # Delete from database
                    print(f"\n🗑️  Deleting from database...")
                    
                    # Get doctor_id if exists
                    doctor_response = supabase.service_client.table("doctor_profiles").select("id").eq("user_id", user_id).execute()
                    doctor_id = doctor_response.data[0].get("id") if doctor_response.data else None
                    
                    # Delete doctor documents
                    if doctor_id:
                        supabase.service_client.table("doctor_documents").delete().eq("doctor_id", doctor_id).execute()
                    if firebase_uid:
                        supabase.service_client.table("doctor_documents").delete().eq("firebase_uid", firebase_uid).execute()
                    
                    # Delete doctor profile
                    if doctor_id:
                        supabase.service_client.table("doctor_profiles").delete().eq("id", doctor_id).execute()
                    
                    # Delete appointments
                    if firebase_uid:
                        supabase.service_client.table("appointments").delete().or_(f"patient_firebase_uid.eq.{firebase_uid},doctor_firebase_uid.eq.{firebase_uid}").execute()
                    
                    # Delete notifications
                    if firebase_uid:
                        supabase.service_client.table("notifications").delete().eq("user_id", firebase_uid).execute()
                    
                    # Delete OTPs
                    supabase.service_client.table("temporary_otp_storage").delete().eq("email", user.get('email')).execute()
                    try:
                        supabase.service_client.table("email_verification_otps").delete().eq("email", user.get('email')).execute()
                    except:
                        pass
                    
                    # Delete user profile
                    supabase.service_client.table("user_profiles").delete().eq("id", user_id).execute()
                    print(f"   ✅ Deleted from database")
            else:
                print(f"⚠️  Not found in database")
        except Exception as e:
            print(f"❌ Error checking database: {e}")
        
        # Check and delete from Firebase
        if firebase_service:
            try:
                # List all users and find by email
                print(f"\n🔍 Checking Firebase Authentication...")
                page = firebase_auth.list_users()
                found_in_firebase = False
                
                while page:
                    for user in page.users:
                        if user.email and user.email.lower() == email.lower():
                            print(f"📋 Found in Firebase:")
                            print(f"   - UID: {user.uid}")
                            print(f"   - Email: {user.email}")
                            
                            try:
                                firebase_auth.delete_user(user.uid)
                                print(f"   ✅ Deleted from Firebase Authentication")
                                found_in_firebase = True
                            except Exception as firebase_error:
                                error_str = str(firebase_error)
                                if "USER_NOT_FOUND" in error_str:
                                    print(f"   ⚠️  User not found in Firebase (may have been deleted)")
                                else:
                                    print(f"   ⚠️  Error: {firebase_error}")
                    
                    page = page.get_next_page() if hasattr(page, 'get_next_page') else None
                
                if not found_in_firebase:
                    print(f"⚠️  Not found in Firebase Authentication")
                    
            except Exception as e:
                print(f"❌ Error checking Firebase: {e}")
                import traceback
                traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("Process completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    check_and_delete()

