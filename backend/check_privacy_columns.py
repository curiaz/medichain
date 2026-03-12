"""
Check if privacy columns exist in user_profiles table
"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_key:
    print("❌ Error: Missing Supabase credentials in .env file")
    sys.exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

def check_columns():
    """Check if privacy columns exist"""
    print("🔍 Checking user_profiles table columns...")
    
    try:
        # Try to select with all privacy columns
        result = supabase.table('user_profiles').select(
            'firebase_uid, profile_visibility, show_email, show_phone, '
            'medical_info_visible_to_doctors, allow_ai_analysis, share_data_for_research'
        ).limit(1).execute()
        
        print("✅ All privacy columns exist and are accessible!")
        print(f"   Found {len(result.data)} records")
        if result.data:
            print(f"   Sample data: {result.data[0]}")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Error accessing columns: {error_msg}")
        
        # Check which specific column is missing
        if 'PGRST204' in error_msg or 'schema cache' in error_msg.lower():
            print("\n⚠️  Schema cache issue detected!")
            print("   Solutions:")
            print("   1. Wait 1-2 minutes for automatic cache refresh")
            print("   2. Restart your Supabase project from the dashboard")
            print("   3. Run this SQL in Supabase SQL Editor:")
            print("      NOTIFY pgrst, 'reload schema';")
        
        # Try to identify missing column
        if "'allow_ai_analysis'" in error_msg:
            print("\n❌ Missing column: allow_ai_analysis")
        elif "'share_data_for_research'" in error_msg:
            print("\n❌ Missing column: share_data_for_research")
        elif "'medical_info_visible_to_doctors'" in error_msg:
            print("\n❌ Missing column: medical_info_visible_to_doctors")
        elif "'profile_visibility'" in error_msg:
            print("\n❌ Missing column: profile_visibility")
        elif "'show_email'" in error_msg:
            print("\n❌ Missing column: show_email")
        elif "'show_phone'" in error_msg:
            print("\n❌ Missing column: show_phone")
        
        return False

def test_basic_select():
    """Test basic select without privacy columns"""
    print("\n🔍 Testing basic select on user_profiles...")
    
    try:
        result = supabase.table('user_profiles').select('firebase_uid, email, first_name, last_name').limit(1).execute()
        print(f"✅ Basic select works! Found {len(result.data)} records")
        return True
    except Exception as e:
        print(f"❌ Basic select failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("CHECKING PRIVACY COLUMNS IN USER_PROFILES")
    print("=" * 60)
    print()
    
    # First check basic connectivity
    if not test_basic_select():
        print("\n❌ Cannot connect to Supabase. Check your credentials.")
        sys.exit(1)
    
    # Then check privacy columns
    if check_columns():
        print("\n✅ All columns are ready to use!")
        sys.exit(0)
    else:
        print("\n❌ Privacy columns are not accessible yet.")
        print("\nPlease run the SQL migration in Supabase SQL Editor:")
        print("   File: database/add_privacy_columns.sql")
        sys.exit(1)
