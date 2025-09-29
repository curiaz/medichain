#!/usr/bin/env python3
"""
Firebase Auth User Cleanup Script
Clears all Firebase Authentication users for fresh start
"""

import os
import sys

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import auth, credentials

# Load environment variables
load_dotenv()


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        # Check if Firebase is already initialized
        try:
            firebase_admin.get_app()
            print("✅ Firebase already initialized")
            return True
        except ValueError:
            pass

        # Initialize with environment variables
        if all(
            key in os.environ
            for key in [
                "FIREBASE_PROJECT_ID",
                "FIREBASE_PRIVATE_KEY",
                "FIREBASE_CLIENT_EMAIL",
            ]
        ):
            cred_dict = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace("\\n", "\n"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
            }

            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            print("✅ Firebase Admin initialized with environment variables")
            return True
        else:
            print("❌ Firebase environment variables not found")
            return False

    except Exception as e:
        print(f"❌ Error initializing Firebase: {e}")
        return False


def list_all_users():
    """List all Firebase Auth users"""
    try:
        users = []
        page = auth.list_users()

        while page:
            for user in page.users:
                users.append(
                    {
                        "uid": user.uid,
                        "email": user.email or "No email",
                        "display_name": user.display_name or "No name",
                        "created": user.user_metadata.creation_timestamp,
                    }
                )

            page = page.get_next_page()

        return users
    except Exception as e:
        print(f"❌ Error listing users: {e}")
        return []


def delete_all_users():
    """Delete all Firebase Auth users"""
    try:
        print("🔍 Fetching all users...")
        users = list_all_users()

        if not users:
            print("ℹ️ No users found to delete")
            return True

        print(f"📊 Found {len(users)} users:")
        for user in users[:5]:  # Show first 5 users
            print(f"  - {user['email']} ({user['uid'][:8]}...)")
        if len(users) > 5:
            print(f"  ... and {len(users) - 5} more")

        # Confirm deletion
        confirm = input(f"\n⚠️ Are you sure you want to delete all {len(users)} users? (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ Operation cancelled")
            return False

        print("🧹 Starting user deletion...")

        deleted_count = 0
        failed_count = 0

        for user in users:
            try:
                auth.delete_user(user["uid"])
                deleted_count += 1
                print(f"✅ Deleted user: {user['email']}")
            except Exception as e:
                failed_count += 1
                print(f"❌ Failed to delete {user['email']}: {e}")

        print("\n📊 Deletion Summary:")
        print(f"  ✅ Successfully deleted: {deleted_count}")
        print(f"  ❌ Failed to delete: {failed_count}")
        print(f"  📋 Total processed: {len(users)}")

        return failed_count == 0

    except Exception as e:
        print(f"❌ Error during bulk deletion: {e}")
        return False


def main():
    """Main function"""
    print("🔥 Firebase Auth User Cleanup Tool")
    print("=" * 50)

    # Initialize Firebase
    if not initialize_firebase():
        print("❌ Failed to initialize Firebase. Exiting.")
        sys.exit(1)

    # Show menu
    while True:
        print("\nOptions:")
        print("1. List all users")
        print("2. Delete all users")
        print("3. Exit")

        choice = input("\nSelect option (1-3): ").strip()

        if choice == "1":
            print("\n🔍 Listing all users...")
            users = list_all_users()
            if users:
                print(f"\n📊 Found {len(users)} users:")
                for i, user in enumerate(users, 1):
                    # Handle timestamp conversion
                    if user["created"]:
                        if hasattr(user["created"], "strftime"):
                            created = user["created"].strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            # Convert timestamp to datetime
                            from datetime import datetime

                            created = datetime.fromtimestamp(user["created"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        created = "Unknown"
                    print(f"{i:3d}. {user['email']} | {user['uid'][:8]}... | Created: {created}")
            else:
                print("ℹ️ No users found")

        elif choice == "2":
            success = delete_all_users()
            if success:
                print("\n✅ All users deleted successfully!")
                print("📝 You can now create new accounts")
            else:
                print("\n⚠️ Some users could not be deleted")

        elif choice == "3":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    main()
