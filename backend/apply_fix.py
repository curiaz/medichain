#!/usr/bin/env python3
"""
Apply the fix for foreign key constraint issue
"""

from db.supabase_client import SupabaseClient
import os

def apply_fix():
    supabase = SupabaseClient()

    # Read the fix SQL file
    fix_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'fix_foreign_key_constraint.sql')

    with open(fix_file, 'r') as f:
        fix_sql = f.read()

    print('🔧 Applying fix for foreign key constraint issue...')
    print('SQL to execute:')
    print('=' * 50)
    print(fix_sql)
    print('=' * 50)

    try:
        # Test database connection
        result = supabase.service_client.table('user_profiles').select('count').limit(1).execute()
        print('✅ Database connection successful')

        print('\n📋 Please copy and run the above SQL in your Supabase dashboard:')
        print('1. Go to your Supabase project dashboard')
        print('2. Navigate to SQL Editor')
        print('3. Paste and run the SQL above')
        print('4. This will:')
        print('   - Remove the foreign key constraint on doctor_profiles.firebase_uid')
        print('   - Keep the triggers to maintain data consistency')
        print('   - Allow the login update to work properly')

    except Exception as e:
        print(f'❌ Error: {e}')
        print('Please run the SQL manually in Supabase dashboard SQL Editor')

if __name__ == '__main__':
    apply_fix()
