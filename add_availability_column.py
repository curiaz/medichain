from backend.db.supabase_client import SupabaseClient

supabase = SupabaseClient()

# Add availability column using raw SQL
sql = """
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'doctor_profiles' 
        AND column_name = 'availability'
    ) THEN
        ALTER TABLE doctor_profiles
        ADD COLUMN availability JSONB DEFAULT '[]'::jsonb;
    END IF;
END $$;
"""

try:
    # Execute the SQL
    result = supabase.client.rpc('exec_sql', {'query': sql}).execute()
    print("✅ Availability column added successfully")
except Exception as e:
    print(f"Note: {e}")
    print("Trying direct table update instead...")
    
# Verify the column exists by checking schema
try:
    # Try to query with availability to see if column exists
    test = supabase.client.table('doctor_profiles').select('availability').limit(1).execute()
    print(f"✅ Availability column exists and is queryable")
    print(f"Sample data: {test.data}")
except Exception as e:
    print(f"❌ Column verification failed: {e}")
