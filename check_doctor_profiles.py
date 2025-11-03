"""
Quick check of doctor profiles
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

from supabase import create_client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\nChecking doctor_profiles table...")
profiles = client.table('doctor_profiles').select('*').execute()
print(f'Total doctor profiles: {len(profiles.data) if profiles.data else 0}\n')

if profiles.data:
    for p in profiles.data:
        print(f"UID: {p.get('firebase_uid')}")
        print(f"  Verification: {p.get('verification_status')}")
        print(f"  Specialization: {p.get('specialization')}")
        print(f"  Availability: {p.get('availability')}")
        print()
else:
    print("No doctor profiles found!\n")
    print("Checking user_profiles for doctors...")
    users = client.table('user_profiles').select('firebase_uid, email, verification_status').eq('role', 'doctor').execute()
    print(f"Found {len(users.data) if users.data else 0} doctor users\n")
    if users.data:
        for u in users.data:
            print(f"  {u.get('email')} - {u.get('verification_status')}")
