"""
Test Supabase connection from backend
"""
import sys
sys.path.append('./backend')

print("\n" + "="*60)
print("🔍 Testing Supabase Connection")
print("="*60)

try:
    from db.supabase_client import SupabaseClient
    
    print("\n✅ SupabaseClient imported successfully")
    
    supabase = SupabaseClient()
    print("✅ SupabaseClient initialized")
    
    # Try to query user_profiles table
    print("\n📊 Testing database query...")
    result = supabase.client.table("user_profiles").select("id, email, role").limit(1).execute()
    
    print(f"✅ Query successful!")
    print(f"   Found {len(result.data)} records")
    if result.data:
        print(f"   Sample: {result.data[0]}")
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60 + "\n")
