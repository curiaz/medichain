"""
Migration Script: Add Deactivation Columns
Date: 2025-11-11
Purpose: Add deactivated_at, reactivated_at, and related columns for account deactivation feature
"""

import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from db.supabase_client import SupabaseClient

def run_migration():
    """Run the migration to add deactivation columns"""
    print("🚀 Starting migration: Add Deactivation Columns")
    print("-" * 60)
    
    supabase = SupabaseClient()
    
    # Migration SQL
    migration_sql = """
    -- Add deactivated_at column to track when account was deactivated
    ALTER TABLE user_profiles 
    ADD COLUMN IF NOT EXISTS deactivated_at TIMESTAMP WITH TIME ZONE;

    -- Add reactivated_at column to track when account was reactivated
    ALTER TABLE user_profiles 
    ADD COLUMN IF NOT EXISTS reactivated_at TIMESTAMP WITH TIME ZONE;

    -- Add is_active column if it doesn't exist
    ALTER TABLE user_profiles 
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

    -- Add account_status column to doctor_profiles if it doesn't exist
    ALTER TABLE doctor_profiles 
    ADD COLUMN IF NOT EXISTS account_status VARCHAR(50) DEFAULT 'active';

    -- Create index on is_active for faster queries
    CREATE INDEX IF NOT EXISTS idx_user_profiles_is_active ON user_profiles(is_active);

    -- Create index on account_status for faster queries
    CREATE INDEX IF NOT EXISTS idx_doctor_profiles_account_status ON doctor_profiles(account_status);
    """
    
    try:
        # Execute migration
        print("📝 Executing migration SQL...")
        result = supabase.service_client.rpc('exec_sql', {'sql': migration_sql}).execute()
        
        print("✅ Migration executed successfully!")
        
        # Update existing records
        print("\n🔄 Updating existing records...")
        
        # Ensure all user_profiles have is_active set
        update_users = supabase.service_client.table('user_profiles').update({
            'is_active': True
        }).is_('is_active', 'null').execute()
        
        print(f"✅ Updated {len(update_users.data) if update_users.data else 0} user profiles")
        
        # Ensure all doctor_profiles have account_status set
        update_doctors = supabase.service_client.table('doctor_profiles').update({
            'account_status': 'active'
        }).is_('account_status', 'null').execute()
        
        print(f"✅ Updated {len(update_doctors.data) if update_doctors.data else 0} doctor profiles")
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        
        # Verify columns exist
        print("\n🔍 Verifying migration...")
        verify_query = supabase.service_client.table('user_profiles').select('is_active, deactivated_at, reactivated_at').limit(1).execute()
        
        if verify_query.data:
            print("✅ All columns verified successfully!")
            print(f"   Sample record: {verify_query.data[0]}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed!")
        print(f"Error: {str(e)}")
        print("\n📝 Manual migration required:")
        print("Please run the following SQL in your Supabase SQL Editor:\n")
        print(migration_sql)
        return False

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("MEDICHAIN DATABASE MIGRATION")
    print("Adding Deactivation/Reactivation Support")
    print("=" * 60 + "\n")
    
    success = run_migration()
    
    if success:
        print("\n✨ You can now use the account deactivation feature!")
    else:
        print("\n⚠️  Please run the migration manually via Supabase dashboard")
    
    sys.exit(0 if success else 1)
