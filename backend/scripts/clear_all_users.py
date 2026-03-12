#!/usr/bin/env python3
"""
Script to clear all users from the database for fresh account creation
WARNING: This will permanently delete all user data including:
- User profiles
- Doctor profiles
- Appointments
- Medical records
- Prescriptions
- AI diagnoses
- Privacy settings
- User documents
- And all related data

Usage:
    python backend/scripts/clear_all_users.py [--confirm]
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv
from db.supabase_client import supabase

# Load environment variables
load_dotenv()


def clear_all_users(confirm=False):
    """
    Clear all users and related data from the database
    
    Args:
        confirm (bool): If True, skip confirmation prompt
    """
    if not confirm:
        print("=" * 60)
        print("⚠️  WARNING: This will delete ALL users and related data!")
        print("=" * 60)
        print("\nThis includes:")
        print("  - All user profiles")
        print("  - All doctor profiles")
        print("  - All appointments")
        print("  - All medical records")
        print("  - All prescriptions")
        print("  - All AI diagnoses")
        print("  - All privacy settings")
        print("  - All user documents")
        print("  - All blockchain transactions")
        print("  - All credential updates")
        print("\n⚠️  This action CANNOT be undone!")
        
        response = input("\nType 'DELETE ALL USERS' to confirm: ")
        if response != "DELETE ALL USERS":
            print("❌ Operation cancelled.")
            return False
    
    print("\n🧹 Starting database cleanup...")
    
    try:
        # Use service client to bypass RLS
        service_client = supabase.service_client
        
        if not service_client:
            print("❌ Error: Service client not available. Check SUPABASE_SERVICE_KEY in .env")
            return False
        
        deleted_counts = {}
        
        # 1. Delete related data first (in order of dependencies)
        print("\n📋 Step 1: Deleting related data...")
        
        # Delete appointments
        try:
            result = service_client.table("appointments").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            deleted_counts["appointments"] = len(result.data) if result.data else 0
            print(f"  ✅ Deleted {deleted_counts['appointments']} appointments")
        except Exception as e:
            print(f"  ⚠️  Error deleting appointments: {e}")
            deleted_counts["appointments"] = 0
        
        # Delete prescriptions
        try:
            result = service_client.table("prescriptions").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            deleted_counts["prescriptions"] = len(result.data) if result.data else 0
            print(f"  ✅ Deleted {deleted_counts['prescriptions']} prescriptions")
        except Exception as e:
            print(f"  ⚠️  Error deleting prescriptions: {e}")
            deleted_counts["prescriptions"] = 0
        
        # Delete AI diagnoses
        try:
            result = service_client.table("ai_diagnoses").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            deleted_counts["ai_diagnoses"] = len(result.data) if result.data else 0
            print(f"  ✅ Deleted {deleted_counts['ai_diagnoses']} AI diagnoses")
        except Exception as e:
            print(f"  ⚠️  Error deleting AI diagnoses: {e}")
            deleted_counts["ai_diagnoses"] = 0
        
        # Delete medical records
        try:
            result = service_client.table("medical_records").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            deleted_counts["medical_records"] = len(result.data) if result.data else 0
            print(f"  ✅ Deleted {deleted_counts['medical_records']} medical records")
        except Exception as e:
            print(f"  ⚠️  Error deleting medical records: {e}")
            deleted_counts["medical_records"] = 0
        
        # Delete blockchain transactions (if table exists)
        try:
            result = service_client.table("blockchain_transactions").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            deleted_counts["blockchain_transactions"] = len(result.data) if result.data else 0
            print(f"  ✅ Deleted {deleted_counts['blockchain_transactions']} blockchain transactions")
        except Exception as e:
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                print(f"  ⏭️  Skipped blockchain_transactions (table does not exist)")
            else:
                print(f"  ⚠️  Error deleting blockchain transactions: {e}")
            deleted_counts["blockchain_transactions"] = 0
        
        # Delete user documents (if table exists)
        try:
            result = service_client.table("user_documents").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            deleted_counts["user_documents"] = len(result.data) if result.data else 0
            print(f"  ✅ Deleted {deleted_counts['user_documents']} user documents")
        except Exception as e:
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                print(f"  ⏭️  Skipped user_documents (table does not exist)")
            else:
                print(f"  ⚠️  Error deleting user documents: {e}")
            deleted_counts["user_documents"] = 0
        
        # Delete privacy settings (if table exists)
        try:
            result = service_client.table("privacy_settings").delete().neq("user_firebase_uid", "").execute()
            deleted_counts["privacy_settings"] = len(result.data) if result.data else 0
            print(f"  ✅ Deleted {deleted_counts['privacy_settings']} privacy settings")
        except Exception as e:
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                print(f"  ⏭️  Skipped privacy_settings (table does not exist)")
            else:
                print(f"  ⚠️  Error deleting privacy settings: {e}")
            deleted_counts["privacy_settings"] = 0
        
        # Delete credential updates (if table exists)
        try:
            result = service_client.table("credential_updates").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            deleted_counts["credential_updates"] = len(result.data) if result.data else 0
            print(f"  ✅ Deleted {deleted_counts['credential_updates']} credential updates")
        except Exception as e:
            if "relation" in str(e).lower() and "does not exist" in str(e).lower():
                print(f"  ⏭️  Skipped credential_updates (table does not exist)")
            else:
                print(f"  ⚠️  Error deleting credential updates: {e}")
            deleted_counts["credential_updates"] = 0
        
        # 2. Delete doctor profiles
        print("\n👨‍⚕️ Step 2: Deleting doctor profiles...")
        try:
            result = service_client.table("doctor_profiles").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            deleted_counts["doctor_profiles"] = len(result.data) if result.data else 0
            print(f"  ✅ Deleted {deleted_counts['doctor_profiles']} doctor profiles")
        except Exception as e:
            print(f"  ⚠️  Error deleting doctor profiles: {e}")
            deleted_counts["doctor_profiles"] = 0
        
        # 3. Delete user profiles (this should cascade to related data)
        print("\n👤 Step 3: Deleting user profiles...")
        try:
            result = service_client.table("user_profiles").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            deleted_counts["user_profiles"] = len(result.data) if result.data else 0
            print(f"  ✅ Deleted {deleted_counts['user_profiles']} user profiles")
        except Exception as e:
            print(f"  ❌ Error deleting user profiles: {e}")
            deleted_counts["user_profiles"] = 0
            return False
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ Database cleanup completed!")
        print("=" * 60)
        print("\nDeleted records:")
        total = 0
        for table, count in deleted_counts.items():
            print(f"  - {table}: {count}")
            total += count
        print(f"\nTotal records deleted: {total}")
        print("\n⚠️  Note: Firebase Auth users are NOT deleted by this script.")
        print("   You may need to delete them manually from Firebase Console.")
        print("   Or use Firebase Admin SDK to delete them programmatically.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Clear all users from the database")
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Skip confirmation prompt (use with caution!)"
    )
    
    args = parser.parse_args()
    
    success = clear_all_users(confirm=args.confirm)
    sys.exit(0 if success else 1)

