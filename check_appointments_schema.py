"""
Check the actual appointments table schema in Supabase
"""

from backend.db.supabase_client import SupabaseClient

supabase = SupabaseClient()

print("Checking appointments table schema...")
print("=" * 60)

try:
    # Try to get all columns by querying with select *
    result = supabase.client.table("appointments").select("*").limit(0).execute()
    print("✅ Appointments table exists and is accessible")
    print("\nNote: To see actual columns, we need to check via SQL or insert a test row")
    
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Attempting to query table structure via information_schema...")
print("=" * 60)

# We need to run this SQL in Supabase dashboard:
sql_to_check = """
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'appointments'
ORDER BY ordinal_position;
"""

print("\nPlease run this SQL in Supabase SQL Editor:")
print("-" * 60)
print(sql_to_check)
print("-" * 60)
print("\nThis will show all columns in the appointments table.")
