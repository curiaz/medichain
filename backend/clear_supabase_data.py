#!/usr/bin/env python3
"""
Supabase Database Cleanup Script
Clears all user data from Supabase tables for fresh start
"""

import os
import sys

from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()


def initialize_supabase():
    """Initialize Supabase client"""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin operations

        if not url or not key:
            print("❌ Supabase credentials not found in environment")
            return None

        supabase = create_client(url, key)
        print("✅ Supabase client initialized")
        return supabase

    except Exception as e:
        print(f"❌ Error initializing Supabase: {e}")
        return None


def count_records(supabase, table_name):
    """Count records in a table"""
    try:
        result = supabase.table(table_name).select("*", count="exact").execute()
        return result.count if hasattr(result, "count") else len(result.data)
    except Exception as e:
        print(f"❌ Error counting {table_name}: {e}")
        return 0


def clear_table(supabase, table_name):
    """Clear all records from a table"""
    try:
        # First count records
        count = count_records(supabase, table_name)
        if count == 0:
            print(f"ℹ️ {table_name}: No records to delete")
            return True

        print(f"🧹 {table_name}: Deleting {count} records...")

        # Delete all records (Supabase requires a condition, so we use neq with impossible value)
        result = supabase.table(table_name).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()

        if result.data is not None:
            deleted_count = len(result.data) if isinstance(result.data, list) else 1
            print(f"✅ {table_name}: Deleted {deleted_count} records")
            return True
        else:
            print(f"✅ {table_name}: Cleared successfully")
            return True

    except Exception as e:
        print(f"❌ Error clearing {table_name}: {e}")
        return False


def show_database_stats(supabase):
    """Show current database statistics"""
    tables = [
        "user_profiles",
        "medical_records",
        "ai_diagnoses",
        "appointments",
        "doctor_reviews",
        "patient_vitals",
    ]

    print("\n📊 Current Database Statistics:")
    print("-" * 40)

    total_records = 0
    for table in tables:
        count = count_records(supabase, table)
        total_records += count
        print(f"{table:20} : {count:6} records")

    print("-" * 40)
    print(f"{'TOTAL':20} : {total_records:6} records")

    return total_records


def clear_all_user_data(supabase):
    """Clear all user data from all tables"""
    tables_to_clear = [
        "doctor_reviews",  # Clear dependent tables first
        "patient_vitals",
        "ai_diagnoses",
        "appointments",
        "medical_records",
        "user_profiles",  # Clear main profiles last
    ]

    print("🧹 Starting database cleanup...")
    print("=" * 50)

    success_count = 0
    total_tables = len(tables_to_clear)

    for table in tables_to_clear:
        if clear_table(supabase, table):
            success_count += 1
        else:
            print(f"⚠️ Warning: Failed to clear {table}")

    print("=" * 50)
    print("📊 Cleanup Summary:")
    print(f"  ✅ Successfully cleared: {success_count}/{total_tables} tables")

    if success_count == total_tables:
        print("✅ Database cleanup completed successfully!")
        print("📝 You can now create new user accounts")
        return True
    else:
        print("⚠️ Some tables could not be cleared completely")
        return False


def main():
    """Main function"""
    print("🗄️ Supabase Database Cleanup Tool")
    print("=" * 50)

    # Initialize Supabase
    supabase = initialize_supabase()
    if not supabase:
        print("❌ Failed to initialize Supabase. Exiting.")
        sys.exit(1)

    # Show menu
    while True:
        print("\nOptions:")
        print("1. Show database statistics")
        print("2. Clear all user data")
        print("3. Clear specific table")
        print("4. Exit")

        choice = input("\nSelect option (1-4): ").strip()

        if choice == "1":
            total = show_database_stats(supabase)
            if total == 0:
                print("\n✨ Database is already clean!")

        elif choice == "2":
            total = show_database_stats(supabase)
            if total == 0:
                print("\n✨ Database is already clean!")
                continue

            confirm = input("\n⚠️ Are you sure you want to delete ALL user data? (yes/no): ")
            if confirm.lower() != "yes":
                print("❌ Operation cancelled")
                continue

            success = clear_all_user_data(supabase)
            if success:
                print("\n🎉 Database cleared successfully!")
            else:
                print("\n⚠️ Database clearing completed with warnings")

        elif choice == "3":
            tables = [
                "user_profiles",
                "medical_records",
                "ai_diagnoses",
                "appointments",
                "doctor_reviews",
                "patient_vitals",
            ]
            print("\nAvailable tables:")
            for i, table in enumerate(tables, 1):
                count = count_records(supabase, table)
                print(f"{i}. {table} ({count} records)")

            try:
                table_choice = int(input("\nSelect table number: ")) - 1
                if 0 <= table_choice < len(tables):
                    table_name = tables[table_choice]
                    count = count_records(supabase, table_name)
                    if count == 0:
                        print(f"ℹ️ {table_name} is already empty")
                        continue

                    confirm = input(f"⚠️ Delete all {count} records from {table_name}? (yes/no): ")
                    if confirm.lower() == "yes":
                        if clear_table(supabase, table_name):
                            print(f"✅ {table_name} cleared successfully!")
                        else:
                            print(f"❌ Failed to clear {table_name}")
                else:
                    print("❌ Invalid table number")
            except ValueError:
                print("❌ Invalid input")

        elif choice == "4":
            print("👋 Goodbye!")
            break

        else:
            print("❌ Invalid option. Please try again.")


if __name__ == "__main__":
    main()
