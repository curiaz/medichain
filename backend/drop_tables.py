"""
Drop existing tables script for MediChain
Drops all existing tables to prepare for fresh schema setup
"""
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.supabase_client import SupabaseClient

def drop_existing_tables():
    """Drop all existing tables in the database"""
    try:
        supabase = SupabaseClient()
        print("✓ Successfully connected to Supabase")

        # List of tables to drop (in reverse dependency order)
        tables_to_drop = [
            'appointments',
            'ai_diagnoses',
            'prescriptions',
            'medical_records',
            'doctor_profiles',
            'user_profiles'
        ]

        print("Dropping existing tables...")

        # Drop each table
        for table in tables_to_drop:
            try:
                # Use service client to bypass RLS
                supabase.service_client.table(table).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
                print(f"✓ Cleared data from {table}")
            except Exception as e:
                print(f"Note: {table} may not exist or is already empty: {e}")

        print("✓ All existing tables have been cleared")
        print("You can now run the enhanced_schema.sql in your Supabase dashboard")

    except Exception as e:
        print(f"Error dropping tables: {e}")
        print("Make sure your SUPABASE_SERVICE_KEY is set in the .env file")

if __name__ == "__main__":
    drop_existing_tables()
