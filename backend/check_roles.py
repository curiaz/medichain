#!/usr/bin/env python3
"""
Check user roles in the database
"""

from db.supabase_client import SupabaseClient

def check_user_roles():
    supabase = SupabaseClient()

    try:
        response = supabase.service_client.table('user_profiles').select('*').execute()

        print(f'Total user profiles: {len(response.data)}')
        if response.data:
            for user in response.data:
                email = user.get('email', 'No email')
                role = user.get('role', 'No role')
                print(f'  Email: {email}, Role: {role}')
        else:
            print('No user profiles found')

    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    check_user_roles()
