"""
Deep dive into the appointments table schema
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

from supabase import create_client
import requests

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\n" + "="*70)
print("  DEEP SCHEMA INVESTIGATION")
print("="*70 + "\n")

# 1. Check what the REST API thinks the schema is
print("1. Checking PostgREST schema endpoint...")
try:
    headers = {
        'apikey': SUPABASE_SERVICE_KEY,
        'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}'
    }
    
    # Get the OpenAPI spec which shows available columns
    response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers)
    print(f"   PostgREST responding: {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

# 2. Check actual database schema using SQL
print("\n2. Checking actual database schema...")
try:
    # Query information_schema to see actual columns
    result = client.rpc('exec', {
        'sql': """
        SELECT column_name, data_type, is_nullable 
        FROM information_schema.columns 
        WHERE table_name = 'appointments' 
        ORDER BY ordinal_position;
        """
    }).execute()
    
    if result.data:
        print("   Actual columns in appointments table:")
        for col in result.data:
            print(f"     - {col}")
    else:
        print("   Could not fetch via RPC, trying direct query...")
except Exception as e:
    print(f"   RPC method failed: {e}")

# 3. Try using raw SQL query
print("\n3. Trying direct SQL to describe appointments table...")
try:
    # Use PostgreSQL's \d equivalent
    sql = """
    SELECT 
        a.attname as column_name,
        pg_catalog.format_type(a.atttypid, a.atttypmod) as data_type,
        a.attnotnull as not_null
    FROM 
        pg_catalog.pg_attribute a
    WHERE 
        a.attrelid = (SELECT c.oid FROM pg_catalog.pg_class c WHERE c.relname = 'appointments')
        AND a.attnum > 0 
        AND NOT a.attisdropped
    ORDER BY a.attnum;
    """
    
    # Try to execute via different method
    from supabase import create_client
    # Create a new client instance
    test_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    
    print("   Attempting SQL query execution...")
    
except Exception as e:
    print(f"   Failed: {e}")

# 4. Try to read the appointments table structure by selecting
print("\n4. Checking table by selecting with specific columns...")
try:
    # Try selecting all columns explicitly
    result = client.table('appointments').select('*').limit(0).execute()
    print(f"   ✅ Can select from appointments table")
    print(f"   Response structure: {type(result)}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Try inserting with minimal fields
print("\n5. Testing minimal insert (to see which fields are required)...")
try:
    from datetime import date, timedelta
    
    minimal_data = {
        'patient_firebase_uid': 'test_patient',
        'doctor_firebase_uid': 'test_doctor',
        'date': (date.today() + timedelta(days=1)).isoformat(),
        'time': '10:00:00',
        'status': 'scheduled'
    }
    
    result = client.table('appointments').insert(minimal_data).execute()
    
    if result.data:
        print(f"   ✅ Minimal insert worked!")
        print(f"   Used columns: {list(minimal_data.keys())}")
        # Cleanup
        client.table('appointments').delete().eq('id', result.data[0]['id']).execute()
    
except Exception as e:
    error_str = str(e)
    print(f"   ❌ Minimal insert failed: {e}")
    
    if 'Could not find' in error_str and 'column' in error_str:
        print("\n   🔍 FOUND THE PROBLEM!")
        print("   The column names in the code don't match the database!")
        
        # Extract what column is missing
        import re
        match = re.search(r"Could not find the '(\w+)' column", error_str)
        if match:
            wrong_column = match.group(1)
            print(f"   Code is using: '{wrong_column}'")
            print(f"   But database might have different column name!")

# 6. Check the SUPABASE_SCHEMA.sql file
print("\n6. Checking SUPABASE_SCHEMA.sql file...")
try:
    with open('SUPABASE_SCHEMA.sql', 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find the appointments table definition
    import re
    table_match = re.search(r'CREATE TABLE.*?appointments.*?\((.*?)\);', content, re.DOTALL | re.IGNORECASE)
    
    if table_match:
        print("   Found appointments table definition:")
        columns_text = table_match.group(1)
        # Parse column definitions
        for line in columns_text.split('\n'):
            line = line.strip()
            if line and not line.startswith('--') and not line.startswith('CONSTRAINT'):
                print(f"     {line}")
    else:
        print("   Could not find appointments table in schema file")
        
except Exception as e:
    print(f"   Error reading schema file: {e}")

print("\n" + "="*70)
print("  ANALYSIS COMPLETE")
print("="*70 + "\n")
