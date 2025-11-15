"""
Direct Supabase Schema Cache Refresh
Uses Supabase REST API to refresh the schema cache
"""

import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

print("\n" + "="*70)
print("  REFRESHING SUPABASE SCHEMA CACHE VIA REST API")
print("="*70 + "\n")

# Method 1: Try to execute SQL directly via REST API
sql_query = "NOTIFY pgrst, 'reload schema';"

try:
    # Execute via SQL endpoint
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/exec",
        headers={
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        },
        json={'query': sql_query}
    )
    
    if response.status_code == 200:
        print("✅ Schema cache refreshed successfully!")
        print("\nNow run: python test_appointment_system.py")
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Response: {response.text}")
        print("\n⚠️  Manual action required in Supabase Dashboard")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print("\n⚠️  Manual action required in Supabase Dashboard")

print("\n" + "="*70)
print("  ALTERNATIVE: Manual Refresh in Supabase Dashboard")
print("="*70)
print("\n1. Open: https://supabase.com/dashboard")
print("2. Select your project")
print("3. Go to SQL Editor")
print("4. Run: NOTIFY pgrst, 'reload schema';")
print("5. Then run: python test_appointment_system.py\n")
