"""Check doctor profile data in database"""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Missing Supabase credentials in .env file")
    sys.exit(1)

# Create Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Get firebase_uid from command line or use test value
firebase_uid = sys.argv[1] if len(sys.argv) > 1 else None

if not firebase_uid:
    print("Usage: python check_doctor_data.py <firebase_uid>")
    print("\nListing all doctors in database:")
    
    # List all user profiles with role=doctor
    users_response = supabase.table('user_profiles').select('firebase_uid, email, first_name, last_name, role').eq('role', 'doctor').execute()
    
    if users_response.data:
        print(f"\n✅ Found {len(users_response.data)} doctors:")
        for user in users_response.data:
            print(f"  - {user['email']} ({user.get('first_name')} {user.get('last_name')}) - UID: {user['firebase_uid']}")
    else:
        print("\n❌ No doctors found in database")
    sys.exit(0)

print(f"🔍 Checking data for Firebase UID: {firebase_uid}\n")

# Check user_profiles
print("1️⃣ Checking user_profiles table:")
user_response = supabase.table('user_profiles').select('*').eq('firebase_uid', firebase_uid).execute()

if user_response.data:
    user = user_response.data[0]
    print(f"✅ Found user profile:")
    print(f"   - Email: {user['email']}")
    print(f"   - Name: {user.get('first_name')} {user.get('last_name')}")
    print(f"   - Role: {user.get('role')}")
    print(f"   - Phone: {user.get('phone')}")
    print(f"   - Address: {user.get('address')}")
    print(f"   - City: {user.get('city')}")
    print(f"   - State: {user.get('state')}")
    print(f"   - Zip: {user.get('zip_code')}")
else:
    print(f"❌ No user profile found for Firebase UID: {firebase_uid}")
    sys.exit(1)

# Check doctor_profiles
print("\n2️⃣ Checking doctor_profiles table:")
doctor_response = supabase.table('doctor_profiles').select('*').eq('firebase_uid', firebase_uid).execute()

if doctor_response.data:
    doctor = doctor_response.data[0]
    print(f"✅ Found doctor profile:")
    print(f"   - Specialization: {doctor.get('specialization')}")
    print(f"   - License Number: {doctor.get('license_number')}")
    print(f"   - Years of Experience: {doctor.get('years_of_experience')}")
    print(f"   - Hospital Affiliation: {doctor.get('hospital_affiliation')}")
    print(f"   - Profile Visibility: {doctor.get('profile_visibility')}")
    print(f"   - Show Email: {doctor.get('show_email')}")
    print(f"   - Show Phone: {doctor.get('show_phone')}")
    print(f"   - Allow Messages: {doctor.get('allow_patient_messages')}")
    print(f"   - Data Sharing: {doctor.get('data_sharing')}")
else:
    print(f"⚠️  No doctor profile found for Firebase UID: {firebase_uid}")
    print("   This will be created on first save.")

print("\n✅ Database check complete!")
