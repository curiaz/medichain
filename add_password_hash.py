"""
Add password_hash column to user_profiles table
Run this if signup is failing with database errors
"""
import sys
sys.path.append('./backend')

from db.supabase_client import SupabaseClient

print("\n" + "="*60)
print("🔧 Adding password_hash column to user_profiles")
print("="*60)

try:
    supabase = SupabaseClient()
    print("✅ Connected to Supabase")
    
    # Read the SQL migration
    with open('./database/add_password_hash_column.sql', 'r') as f:
        sql = f.read()
    
    print("\n📝 SQL to execute:")
    print(sql)
    
    # Execute via RPC or direct SQL if available
    print("\n⚠️  Please run this SQL manually in Supabase Dashboard:")
    print("   1. Go to Supabase Dashboard → SQL Editor")
    print("   2. Copy and paste the SQL above")
    print("   3. Click 'Run'")
    print("\nOR use the Supabase CLI:")
    print("   supabase db execute --file database/add_password_hash_column.sql")
    
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60 + "\n")
