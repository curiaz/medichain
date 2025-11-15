"""
Check Database Status and Users
"""

import os
import sys
from dotenv import load_dotenv

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment
load_dotenv('backend/.env')

from supabase import create_client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\n" + "="*70)
print("  DATABASE STATUS CHECK")
print("="*70 + "\n")

# Check user_profiles
try:
    users = supabase.table("user_profiles").select("firebase_uid, email, name, role").limit(10).execute()
    print(f"✅ User Profiles: {len(users.data)} users found")
    for user in users.data[:5]:
        print(f"   - {user.get('name', 'N/A')} ({user.get('email', 'N/A')}) - {user.get('role', 'N/A')}")
except Exception as e:
    print(f"❌ Error fetching user_profiles: {e}")

print()

# Check doctor_profiles  
try:
    doctors = supabase.table("doctor_profiles").select("firebase_uid, email, verification_status").limit(10).execute()
    print(f"✅ Doctor Profiles: {len(doctors.data)} doctors found")
    for doctor in doctors.data[:5]:
        print(f"   - {doctor.get('email', 'N/A')} - Status: {doctor.get('verification_status', 'N/A')}")
except Exception as e:
    print(f"❌ Error fetching doctor_profiles: {e}")

print()

# Check appointments table structure
try:
    # Get first row or empty result to see structure
    appointments = supabase.table("appointments").select("*").limit(1).execute()
    print(f"✅ Appointments Table: Accessible ({len(appointments.data)} records)")
    if appointments.data:
        print(f"   Columns: {', '.join(appointments.data[0].keys())}")
except Exception as e:
    print(f"❌ Error accessing appointments: {e}")

print()

# Check approved doctors
try:
    approved = supabase.table("doctor_profiles").select("firebase_uid, email").eq("verification_status", "approved").execute()
    print(f"✅ Approved Doctors: {len(approved.data)} doctors")
    for doctor in approved.data[:3]:
        print(f"   - {doctor.get('email', 'N/A')}")
except Exception as e:
    print(f"❌ Error fetching approved doctors: {e}")

print("\n" + "="*70 + "\n")
