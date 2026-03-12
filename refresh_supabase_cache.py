"""
Refresh Supabase Schema Cache using SQL
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
print("  REFRESHING SUPABASE SCHEMA CACHE")
print("="*70 + "\n")

try:
    # Method 1: Try using PostgREST admin endpoint
    print("Attempting to reload schema cache...")
    
    # Send NOTIFY command through SQL
    result = client.rpc('exec_sql', {
        'query': 'NOTIFY pgrst, \'reload schema\''
    }).execute()
    
    print("✅ Schema cache refresh initiated via SQL")
    
except Exception as e:
    print(f"⚠️  SQL method failed: {e}")
    print("\nTrying alternative method...")
    
    try:
        # Method 2: Direct REST API call to reload endpoint
        headers = {
            'apikey': SUPABASE_SERVICE_KEY,
            'Authorization': f'Bearer {SUPABASE_SERVICE_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Try the reload endpoint
        reload_url = f"{SUPABASE_URL}/rest/v1/"
        response = requests.post(reload_url, headers=headers)
        
        print(f"✅ Schema refresh attempted via REST API")
        
    except Exception as e2:
        print(f"⚠️  REST API method also failed: {e2}")
        print("\n" + "="*70)
        print("  MANUAL REFRESH REQUIRED")
        print("="*70)
        print("\nThe Supabase schema cache needs to be refreshed manually.")
        print("\nOption 1 - Via Supabase Dashboard:")
        print("  1. Go to: https://supabase.com/dashboard/project/royvcmfbcghamnbnxdgb")
        print("  2. Click on 'SQL Editor'")
        print("  3. Run this command:")
        print("     NOTIFY pgrst, 'reload schema';")
        print("\nOption 2 - Restart PostgREST (Supabase Dashboard):")
        print("  1. Go to: https://supabase.com/dashboard/project/royvcmfbcghamnbnxdgb")
        print("  2. Click on 'Settings' > 'API'")
        print("  3. Look for 'Restart PostgREST' or restart your project")

# Test if the schema is now working
print("\n" + "="*70)
print("  TESTING SCHEMA AFTER REFRESH")
print("="*70 + "\n")

try:
    from datetime import date, timedelta
    
    # Try to insert a test appointment
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    test_data = {
        'patient_firebase_uid': 'test_uid',
        'doctor_firebase_uid': 'test_uid',
        'appointment_date': tomorrow,
        'appointment_time': '10:00:00',
        'appointment_type': 'test',
        'status': 'scheduled',
        'notes': 'Schema test'
    }
    
    result = client.table('appointments').insert(test_data).execute()
    
    if result.data:
        # Delete the test appointment
        client.table('appointments').delete().eq('id', result.data[0]['id']).execute()
        print("✅ Schema is working! Appointment creation successful!")
        print("\n" + "="*70)
        print("  ✅ APPOINTMENT SYSTEM IS READY")
        print("="*70)
        print("\nYou can now:")
        print("  - Create appointments via API")
        print("  - Book appointments through frontend")
        print("  - Test with: python test_appointment_system.py")
    
except Exception as e:
    error_msg = str(e)
    if 'PGRST204' in error_msg or 'schema cache' in error_msg:
        print("❌ Schema cache still needs refresh")
        print("\nPlease manually refresh using Supabase Dashboard:")
        print("  1. Open: https://supabase.com/dashboard/project/royvcmfbcghamnbnxdgb")
        print("  2. Go to SQL Editor")
        print("  3. Run: NOTIFY pgrst, 'reload schema';")
        print("\nOr simply wait 5-10 minutes for automatic cache refresh.")
    else:
        print(f"❌ Schema test failed: {e}")
