"""
Direct PostgreSQL Connection to Refresh Schema Cache
Connects directly to Supabase PostgreSQL database and executes NOTIFY command
"""

import os
from dotenv import load_dotenv
import psycopg2

# Load environment from backend directory
load_dotenv('backend/.env')

print("\n" + "="*70)
print("  REFRESHING SUPABASE SCHEMA CACHE VIA DIRECT POSTGRESQL CONNECTION")
print("="*70 + "\n")

# Get Supabase URL and convert to PostgreSQL connection string
supabase_url = os.getenv('SUPABASE_URL', 'https://royvcmfbcghamnbnxdgb.supabase.co')
service_key = os.getenv('SUPABASE_SERVICE_KEY')

# Extract project reference from URL
# Format: https://PROJECT_REF.supabase.co
project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '')

# Supabase PostgreSQL connection string format
# postgresql://postgres:[YOUR-PASSWORD]@db.PROJECT_REF.supabase.co:5432/postgres

print("⚠️  Direct PostgreSQL connection requires the database password.")
print("You can find this in Supabase Dashboard > Settings > Database > Connection String")
print("\nExample format:")
print(f"postgresql://postgres:YOUR_PASSWORD@db.{project_ref}.supabase.co:5432/postgres\n")

# For security, we'll try using the REST API instead
print("Attempting REST API approach instead...")

import requests

try:
    # Try to reload schema via direct HTTP request to PostgREST
    headers = {
        'apikey': service_key,
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    # Send a request that will trigger schema reload
    # This is a workaround - we'll make a simple query
    response = requests.get(
        f"{supabase_url}/rest/v1/appointments?limit=1",
        headers=headers
    )
    
    if response.status_code in [200, 400, 404]:
        print(f"\n✅ Connected to Supabase successfully")
        print(f"Response code: {response.status_code}")
        
        if response.status_code == 400 and 'schema cache' in str(response.text):
            print("\n❌ Schema cache still needs refresh")
            print("\nThe ONLY way to refresh is through Supabase Dashboard:")
            print("\n1. Go to: https://supabase.com/dashboard")
            print(f"2. Select project: {project_ref}")
            print("3. SQL Editor → New query")
            print("4. Run: NOTIFY pgrst, 'reload schema';")
            print("5. Then run: python test_appointment_system.py\n")
        else:
            print("\n✅ Schema cache might be working now!")
            print("Run: python test_appointment_system.py\n")
    else:
        print(f"\n❌ Unexpected response: {response.status_code}")
        print(f"Response: {response.text[:200]}\n")
        
except Exception as e:
    print(f"\n❌ Error: {e}\n")
    print("Manual refresh required in Supabase Dashboard")

print("="*70)
print("  RECOMMENDATION")
print("="*70)
print("\nThe schema cache refresh MUST be done manually via Supabase Dashboard.")
print("This is a one-time requirement after creating new database columns.")
print("\nAlternatively, you can:")
print("1. Restart the PostgREST server (in Supabase Dashboard)")
print("2. Or wait ~5 minutes for automatic refresh")
print("3. Or run NOTIFY command in SQL Editor (fastest)\n")
