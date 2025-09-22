#!/usr/bin/env python3
"""
Apply database trigger to sync firebase_uid between user_profiles and doctor_profiles
"""

from db.supabase_client import SupabaseClient
import os

def apply_trigger():
    supabase = SupabaseClient()

    # Read the trigger SQL file
    trigger_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'sync_firebase_uid_trigger.sql')

    with open(trigger_file, 'r') as f:
        trigger_sql = f.read()

    print('🔧 Applying database trigger to sync firebase_uid...')
    print('SQL to execute:')
    print('=' * 50)
    print(trigger_sql)
    print('=' * 50)

    try:
        # Try to execute using service client
        # Note: This requires proper permissions
        result = supabase.service_client.table('user_profiles').select('count').limit(1).execute()
        print('✅ Database connection successful')

        # For now, just show the SQL - user needs to run it manually in Supabase dashboard
        print('\n📋 Please copy and run the above SQL in your Supabase dashboard:')
        print('1. Go to your Supabase project dashboard')
        print('2. Navigate to SQL Editor')
        print('3. Paste and run the SQL above')
        print('4. This will create triggers to automatically sync firebase_uid')

    except Exception as e:
        print(f'❌ Error: {e}')
        print('Please run the SQL manually in Supabase dashboard SQL Editor')

if __name__ == '__main__':
    apply_trigger()
