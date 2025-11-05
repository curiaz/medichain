"""
Debug script to check system state and authentication flow
"""
import os
from dotenv import load_dotenv
load_dotenv('backend/.env')

from supabase import create_client

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')

client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

print("\n" + "="*70)
print("  SYSTEM STATE CHECK FOR NAVIGATION ISSUE")
print("="*70 + "\n")

# Check patient accounts
print("1. Checking patient accounts...")
patients = client.table('user_profiles').select('firebase_uid, email, role, first_name, last_name').eq('role', 'patient').execute()

if patients.data:
    print(f"✅ Found {len(patients.data)} patient accounts:")
    for p in patients.data[:3]:
        print(f"   - {p.get('email')} ({p.get('role')})")
else:
    print("❌ No patient accounts found!")

# Check approved doctors
print("\n2. Checking approved doctors...")
doctors = client.table('doctor_profiles').select('firebase_uid, specialization, verification_status').eq('verification_status', 'approved').execute()

if doctors.data:
    print(f"✅ Found {len(doctors.data)} approved doctors")
    for d in doctors.data:
        print(f"   - {d.get('firebase_uid')} - {d.get('specialization')}")
else:
    print("❌ No approved doctors found!")

print("\n" + "="*70)
print("  NAVIGATION DEBUG INFO")
print("="*70 + "\n")

print("Expected flow:")
print("1. User clicks 'General Practitioner' on /book-appointment")
print("2. Should navigate to /select-gp with state: { appointmentType: 'general-practitioner' }")
print("3. SelectGP component should fetch approved doctors")
print("4. Display list of doctors")
print("\nPotential issues:")
print("- Authentication token expired or invalid")
print("- User role is not 'patient'")
print("- API endpoint returning 401/403")
print("- React Router state not preserved")
print("- ProtectedRoute redirecting to dashboard")

print("\n" + "="*70)
print("  RECOMMENDATIONS")
print("="*70 + "\n")

print("1. Check browser console for errors")
print("2. Verify user is logged in as 'patient' role")
print("3. Check Network tab for /api/appointments/doctors/approved call")
print("4. Look for any React Router redirects in console")
print("5. Verify Firebase auth token is valid")

print("\n" + "="*70 + "\n")
