#!/usr/bin/env python3
"""
Delete users from both database and Firebase Authentication
Deletes: bosx1negamer25@gmail.com and bruh.telev@gmail.com
"""

import os
import sys
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

load_dotenv()

from db.supabase_client import SupabaseClient
from auth.firebase_auth import FirebaseAuthService

def delete_users():
    """Delete users from both database and Firebase"""
    emails = ['bosx1negamer25@gmail.com', 'bruh.telev@gmail.com']
    
    # Initialize services
    try:
        supabase = SupabaseClient()
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"❌ Error initializing Supabase: {e}")
        return
    
    try:
        firebase_auth = FirebaseAuthService()
        print("✅ Firebase Admin initialized")
    except Exception as e:
        print(f"⚠️  Warning: Firebase Admin not initialized: {e}")
        print("   Will only delete from database")
        firebase_auth = None
    
    for email in emails:
        print(f"\n{'='*60}")
        print(f"Processing: {email}")
        print(f"{'='*60}")
        
        try:
            # Get user from database
            user_response = supabase.service_client.table("user_profiles").select("id, firebase_uid").eq("email", email).execute()
            
            if not user_response.data:
                print(f"⚠️  User not found in database: {email}")
                continue
            
            user = user_response.data[0]
            user_id = user.get("id")
            firebase_uid = user.get("firebase_uid")
            
            print(f"📋 Found user in database:")
            print(f"   - ID: {user_id}")
            print(f"   - Firebase UID: {firebase_uid}")
            
            # Get doctor_id if exists
            doctor_response = supabase.service_client.table("doctor_profiles").select("id").eq("user_id", user_id).execute()
            doctor_id = doctor_response.data[0].get("id") if doctor_response.data else None
            
            # Delete from database (in order of dependencies)
            print(f"\n🗑️  Deleting from database...")
            
            # Delete doctor documents
            if doctor_id:
                docs_response = supabase.service_client.table("doctor_documents").delete().eq("doctor_id", doctor_id).execute()
                print(f"   ✅ Deleted doctor documents")
            
            if firebase_uid:
                docs_response = supabase.service_client.table("doctor_documents").delete().eq("firebase_uid", firebase_uid).execute()
                if docs_response.data:
                    print(f"   ✅ Deleted additional doctor documents by firebase_uid")
            
            # Delete doctor profile
            if doctor_id:
                supabase.service_client.table("doctor_profiles").delete().eq("id", doctor_id).execute()
                print(f"   ✅ Deleted doctor profile")
            
            # Delete appointments
            if firebase_uid:
                appointments_response = supabase.service_client.table("appointments").delete().or_(f"patient_firebase_uid.eq.{firebase_uid},doctor_firebase_uid.eq.{firebase_uid}").execute()
                print(f"   ✅ Deleted appointments")
            
            # Delete notifications
            if firebase_uid:
                notifications_response = supabase.service_client.table("notifications").delete().eq("user_id", firebase_uid).execute()
                print(f"   ✅ Deleted notifications")
            
            # Delete OTPs
            supabase.service_client.table("temporary_otp_storage").delete().eq("email", email).execute()
            print(f"   ✅ Deleted temporary OTPs")
            
            # Try to delete from email_verification_otps if table exists
            try:
                supabase.service_client.table("email_verification_otps").delete().eq("email", email).execute()
                print(f"   ✅ Deleted email verification OTPs")
            except:
                pass  # Table might not exist
            
            # Delete user profile (this should cascade to other related data)
            supabase.service_client.table("user_profiles").delete().eq("id", user_id).execute()
            print(f"   ✅ Deleted user profile from database")
            
            # Delete from Firebase Authentication
            if firebase_auth and firebase_uid:
                try:
                    from firebase_admin import auth
                    auth.delete_user(firebase_uid)
                    print(f"   ✅ Deleted user from Firebase Authentication")
                except Exception as firebase_error:
                    error_str = str(firebase_error)
                    if "USER_NOT_FOUND" in error_str or "not found" in error_str.lower():
                        print(f"   ⚠️  User not found in Firebase (may have been deleted already)")
                    else:
                        print(f"   ⚠️  Error deleting from Firebase: {firebase_error}")
            elif not firebase_uid:
                print(f"   ⚠️  No Firebase UID found, skipping Firebase deletion")
            
            print(f"\n✅ Successfully deleted: {email}")
            
        except Exception as e:
            print(f"❌ Error deleting {email}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*60}")
    print("Deletion process completed!")
    print(f"{'='*60}")

if __name__ == "__main__":
    import sys
    import io
    # Fix encoding for Windows console
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("WARNING: This will permanently delete users from both database and Firebase!")
    print("Users to delete:")
    print("  - bosx1negamer25@gmail.com")
    print("  - bruh.telev@gmail.com")
    print()
    confirm = input("Type 'DELETE' to confirm: ")
    
    if confirm == "DELETE":
        delete_users()
    else:
        print("Deletion cancelled")

