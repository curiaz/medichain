"""
Quick Database Migration Runner
Adds deactivation columns to user_profiles and doctor_profiles tables
"""
import os
import sys

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

try:
    from db.supabase_client import SupabaseClient
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False

def run_migration():
    """Run the deactivation columns migration"""
    print("\n" + "="*70)
    print("MEDICHAIN - Database Migration")
    print("Adding Account Deactivation Support")
    print("="*70 + "\n")
    
    try:
        if HAS_SUPABASE:
            supabase = SupabaseClient()
            print("✅ Connected to Supabase\n")
        else:
            print("⚠️  Supabase client not available\n")
        
        # Step 1: Add columns to user_profiles
        print("📝 Step 1: Adding columns to user_profiles table...")
        
        # Note: Supabase Python client doesn't support ALTER TABLE directly
        # We need to use raw SQL through PostgreSQL or Supabase REST API
        
        print("⚠️  Important: Supabase Python client cannot execute ALTER TABLE commands.")
        print("You need to run the SQL manually in Supabase Dashboard.\n")
        
        print("=" * 70)
        print("PLEASE RUN THIS SQL IN YOUR SUPABASE SQL EDITOR:")
        print("=" * 70)
        print("""
-- Add columns to user_profiles
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS deactivated_at TIMESTAMP WITH TIME ZONE;

ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS reactivated_at TIMESTAMP WITH TIME ZONE;

-- Add column to doctor_profiles  
ALTER TABLE doctor_profiles 
ADD COLUMN IF NOT EXISTS account_status VARCHAR(50) DEFAULT 'active';

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_profiles_is_active 
ON user_profiles(is_active);

CREATE INDEX IF NOT EXISTS idx_doctor_profiles_account_status 
ON doctor_profiles(account_status);

-- Update existing records
UPDATE user_profiles SET is_active = TRUE WHERE is_active IS NULL;
UPDATE doctor_profiles SET account_status = 'active' WHERE account_status IS NULL;
""")
        print("=" * 70)
        print("\n📋 How to run this:")
        print("1. Go to https://app.supabase.com")
        print("2. Select your project")
        print("3. Click 'SQL Editor' in the left sidebar")
        print("4. Click 'New Query'")
        print("5. Copy and paste the SQL above")
        print("6. Click 'Run' button")
        print("\n✨ After running the SQL, your account deactivation feature will work!\n")
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {str(e)}\n")
        return False

if __name__ == "__main__":
    run_migration()
    print("\nPress Enter to exit...")
    input()
