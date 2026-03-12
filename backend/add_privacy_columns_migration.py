"""
Add privacy columns to user_profiles table
Adds: profile_visibility, show_email, show_phone, medical_info_visible_to_doctors, 
      allow_ai_analysis, share_data_for_research
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def add_privacy_columns():
    """Add privacy columns to user_profiles table"""
    
    print("🔧 Adding privacy columns to user_profiles table...")
    
    # SQL to add privacy columns
    sql = """
    ALTER TABLE user_profiles
    ADD COLUMN IF NOT EXISTS profile_visibility VARCHAR(20) DEFAULT 'private',
    ADD COLUMN IF NOT EXISTS show_email BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS show_phone BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS medical_info_visible_to_doctors BOOLEAN DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS allow_ai_analysis BOOLEAN DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS share_data_for_research BOOLEAN DEFAULT FALSE;
    """
    
    try:
        # Execute the SQL using Supabase RPC or direct query
        result = supabase.rpc('exec_sql', {'sql': sql}).execute()
        print("✅ Privacy columns added successfully!")
        return True
    except Exception as e:
        print(f"❌ Error adding columns: {e}")
        print("\n⚠️  Please run this SQL manually in Supabase SQL Editor:")
        print(sql)
        return False

def verify_columns():
    """Verify that the columns were added"""
    print("\n🔍 Verifying columns...")
    
    try:
        # Try to select with the new columns
        result = supabase.table('user_profiles').select(
            'firebase_uid, profile_visibility, show_email, show_phone, '
            'medical_info_visible_to_doctors, allow_ai_analysis, share_data_for_research'
        ).limit(1).execute()
        
        print("✅ All privacy columns exist and are accessible!")
        return True
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("ADDING PRIVACY COLUMNS TO USER_PROFILES")
    print("=" * 60)
    
    # Note: Supabase may not support direct SQL execution via Python client
    # You may need to run this SQL manually in the Supabase SQL Editor
    
    print("\n📝 SQL to run in Supabase SQL Editor:")
    print("-" * 60)
    
    sql_to_run = """
-- Add privacy columns to user_profiles table
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS profile_visibility VARCHAR(20) DEFAULT 'private' CHECK (profile_visibility IN ('private', 'doctors_only', 'public')),
ADD COLUMN IF NOT EXISTS show_email BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS show_phone BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS medical_info_visible_to_doctors BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS allow_ai_analysis BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS share_data_for_research BOOLEAN DEFAULT FALSE;

-- Refresh the schema cache
NOTIFY pgrst, 'reload schema';
"""
    
    print(sql_to_run)
    print("-" * 60)
    
    print("\n📋 Instructions:")
    print("1. Go to your Supabase Dashboard")
    print("2. Open the SQL Editor")
    print("3. Copy and paste the SQL above")
    print("4. Click 'Run' to execute")
    print("\n5. After running, press Enter here to verify...")
    
    input()
    
    # Verify the columns
    if verify_columns():
        print("\n✅ Migration completed successfully!")
    else:
        print("\n❌ Migration verification failed. Please check Supabase dashboard.")
