#!/usr/bin/env python3
"""
Test script to directly test appointment fetching from database
This bypasses the API and tests the database connection directly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.supabase_client import SupabaseClient

def test_appointments_fetch():
    """Test fetching appointments directly from database"""
    print("=" * 60)
    print("🧪 Testing Appointments Fetch")
    print("=" * 60)
    
    try:
        # Initialize Supabase client
        print("\n1. Initializing Supabase client...")
        supabase = SupabaseClient()
        
        if not supabase:
            print("❌ ERROR: Could not initialize SupabaseClient")
            return
        
        if not supabase.service_client:
            print("❌ ERROR: service_client is not available")
            print("💡 Check SUPABASE_SERVICE_KEY in .env file")
            return
        
        print("✅ Supabase client initialized")
        print(f"   - client available: {supabase.client is not None}")
        print(f"   - service_client available: {supabase.service_client is not None}")
        
        # Test 1: Query all appointments
        print("\n2. Testing: Fetch ALL appointments from database...")
        try:
            all_appointments = supabase.service_client.table("appointments").select("*").execute()
            print(f"✅ Query executed successfully")
            print(f"   - Response type: {type(all_appointments)}")
            print(f"   - Has data attribute: {hasattr(all_appointments, 'data')}")
            
            if hasattr(all_appointments, 'data'):
                appointments = all_appointments.data
                print(f"   - Appointments found: {len(appointments) if appointments else 0}")
                
                if appointments:
                    print(f"\n📋 Appointments in database:")
                    for i, apt in enumerate(appointments, 1):
                        print(f"\n   Appointment {i}:")
                        print(f"      ID: {apt.get('id')}")
                        print(f"      Doctor UID: {apt.get('doctor_firebase_uid')}")
                        print(f"      Patient UID: {apt.get('patient_firebase_uid')}")
                        print(f"      Date: {apt.get('appointment_date')}")
                        print(f"      Time: {apt.get('appointment_time')}")
                        print(f"      Status: {apt.get('status')}")
                    
                    # Get unique doctor UIDs
                    doctor_uids = set(apt.get('doctor_firebase_uid') for apt in appointments if apt.get('doctor_firebase_uid'))
                    patient_uids = set(apt.get('patient_firebase_uid') for apt in appointments if apt.get('patient_firebase_uid'))
                    
                    print(f"\n📊 Summary:")
                    print(f"   - Total appointments: {len(appointments)}")
                    print(f"   - Unique doctor UIDs: {list(doctor_uids)}")
                    print(f"   - Unique patient UIDs: {list(patient_uids)}")
                else:
                    print("⚠️  No appointments found in database")
            else:
                print("❌ Response does not have 'data' attribute")
                print(f"   - Response: {all_appointments}")
        except Exception as e:
            print(f"❌ ERROR fetching appointments: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 2: Query with specific doctor UID (from screenshot)
        print("\n3. Testing: Fetch appointments for specific doctor UID...")
        test_doctor_uid = "fLmNDKoCp1e0vQrOAs7bSYLSB8y1"  # From screenshot
        try:
            doctor_appointments = supabase.service_client.table("appointments").select("*").eq("doctor_firebase_uid", test_doctor_uid).execute()
            print(f"✅ Query executed for doctor UID: {test_doctor_uid}")
            
            if hasattr(doctor_appointments, 'data'):
                apts = doctor_appointments.data
                print(f"   - Appointments found: {len(apts) if apts else 0}")
                
                if apts:
                    print(f"   ✅ Successfully fetched {len(apts)} appointments for this doctor")
                else:
                    print(f"   ⚠️  No appointments found for this doctor UID")
            else:
                print(f"   ❌ Response does not have 'data' attribute")
        except Exception as e:
            print(f"❌ ERROR querying by doctor UID: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Check user_profiles
        print("\n4. Testing: Check user_profiles table...")
        try:
            all_users = supabase.service_client.table("user_profiles").select("firebase_uid, email, role").limit(10).execute()
            if hasattr(all_users, 'data') and all_users.data:
                print(f"✅ Found {len(all_users.data)} user profiles")
                print(f"\n📋 User Profiles:")
                for user in all_users.data:
                    role = user.get('role', 'N/A')
                    uid = user.get('firebase_uid', 'N/A')
                    email = user.get('email', 'N/A')
                    print(f"   - {role}: {uid} ({email})")
            else:
                print("⚠️  No user profiles found")
        except Exception as e:
            print(f"❌ ERROR querying user_profiles: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 4: Check if doctor UID from appointments exists in user_profiles
        print("\n5. Testing: Check if doctor UID exists in user_profiles...")
        if appointments:
            doctor_uids = set(apt.get('doctor_firebase_uid') for apt in appointments if apt.get('doctor_firebase_uid'))
            for doctor_uid in doctor_uids:
                try:
                    user_check = supabase.service_client.table("user_profiles").select("*").eq("firebase_uid", doctor_uid).execute()
                    if hasattr(user_check, 'data') and user_check.data:
                        user = user_check.data[0]
                        print(f"   ✅ Doctor UID {doctor_uid} exists in user_profiles")
                        print(f"      - Email: {user.get('email')}")
                        print(f"      - Role: {user.get('role')}")
                        print(f"      - Name: {user.get('first_name')} {user.get('last_name')}")
                    else:
                        print(f"   ⚠️  Doctor UID {doctor_uid} NOT found in user_profiles")
                        print(f"      💡 This is the problem! The UID in appointments doesn't match any user profile")
                except Exception as e:
                    print(f"   ❌ Error checking UID {doctor_uid}: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Test complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_appointments_fetch()

"""
Test script to directly test appointment fetching from database
This bypasses the API and tests the database connection directly
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.supabase_client import SupabaseClient

def test_appointments_fetch():
    """Test fetching appointments directly from database"""
    print("=" * 60)
    print("🧪 Testing Appointments Fetch")
    print("=" * 60)
    
    try:
        # Initialize Supabase client
        print("\n1. Initializing Supabase client...")
        supabase = SupabaseClient()
        
        if not supabase:
            print("❌ ERROR: Could not initialize SupabaseClient")
            return
        
        if not supabase.service_client:
            print("❌ ERROR: service_client is not available")
            print("💡 Check SUPABASE_SERVICE_KEY in .env file")
            return
        
        print("✅ Supabase client initialized")
        print(f"   - client available: {supabase.client is not None}")
        print(f"   - service_client available: {supabase.service_client is not None}")
        
        # Test 1: Query all appointments
        print("\n2. Testing: Fetch ALL appointments from database...")
        try:
            all_appointments = supabase.service_client.table("appointments").select("*").execute()
            print(f"✅ Query executed successfully")
            print(f"   - Response type: {type(all_appointments)}")
            print(f"   - Has data attribute: {hasattr(all_appointments, 'data')}")
            
            if hasattr(all_appointments, 'data'):
                appointments = all_appointments.data
                print(f"   - Appointments found: {len(appointments) if appointments else 0}")
                
                if appointments:
                    print(f"\n📋 Appointments in database:")
                    for i, apt in enumerate(appointments, 1):
                        print(f"\n   Appointment {i}:")
                        print(f"      ID: {apt.get('id')}")
                        print(f"      Doctor UID: {apt.get('doctor_firebase_uid')}")
                        print(f"      Patient UID: {apt.get('patient_firebase_uid')}")
                        print(f"      Date: {apt.get('appointment_date')}")
                        print(f"      Time: {apt.get('appointment_time')}")
                        print(f"      Status: {apt.get('status')}")
                    
                    # Get unique doctor UIDs
                    doctor_uids = set(apt.get('doctor_firebase_uid') for apt in appointments if apt.get('doctor_firebase_uid'))
                    patient_uids = set(apt.get('patient_firebase_uid') for apt in appointments if apt.get('patient_firebase_uid'))
                    
                    print(f"\n📊 Summary:")
                    print(f"   - Total appointments: {len(appointments)}")
                    print(f"   - Unique doctor UIDs: {list(doctor_uids)}")
                    print(f"   - Unique patient UIDs: {list(patient_uids)}")
                else:
                    print("⚠️  No appointments found in database")
            else:
                print("❌ Response does not have 'data' attribute")
                print(f"   - Response: {all_appointments}")
        except Exception as e:
            print(f"❌ ERROR fetching appointments: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Test 2: Query with specific doctor UID (from screenshot)
        print("\n3. Testing: Fetch appointments for specific doctor UID...")
        test_doctor_uid = "fLmNDKoCp1e0vQrOAs7bSYLSB8y1"  # From screenshot
        try:
            doctor_appointments = supabase.service_client.table("appointments").select("*").eq("doctor_firebase_uid", test_doctor_uid).execute()
            print(f"✅ Query executed for doctor UID: {test_doctor_uid}")
            
            if hasattr(doctor_appointments, 'data'):
                apts = doctor_appointments.data
                print(f"   - Appointments found: {len(apts) if apts else 0}")
                
                if apts:
                    print(f"   ✅ Successfully fetched {len(apts)} appointments for this doctor")
                else:
                    print(f"   ⚠️  No appointments found for this doctor UID")
            else:
                print(f"   ❌ Response does not have 'data' attribute")
        except Exception as e:
            print(f"❌ ERROR querying by doctor UID: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 3: Check user_profiles
        print("\n4. Testing: Check user_profiles table...")
        try:
            all_users = supabase.service_client.table("user_profiles").select("firebase_uid, email, role").limit(10).execute()
            if hasattr(all_users, 'data') and all_users.data:
                print(f"✅ Found {len(all_users.data)} user profiles")
                print(f"\n📋 User Profiles:")
                for user in all_users.data:
                    role = user.get('role', 'N/A')
                    uid = user.get('firebase_uid', 'N/A')
                    email = user.get('email', 'N/A')
                    print(f"   - {role}: {uid} ({email})")
            else:
                print("⚠️  No user profiles found")
        except Exception as e:
            print(f"❌ ERROR querying user_profiles: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 4: Check if doctor UID from appointments exists in user_profiles
        print("\n5. Testing: Check if doctor UID exists in user_profiles...")
        if appointments:
            doctor_uids = set(apt.get('doctor_firebase_uid') for apt in appointments if apt.get('doctor_firebase_uid'))
            for doctor_uid in doctor_uids:
                try:
                    user_check = supabase.service_client.table("user_profiles").select("*").eq("firebase_uid", doctor_uid).execute()
                    if hasattr(user_check, 'data') and user_check.data:
                        user = user_check.data[0]
                        print(f"   ✅ Doctor UID {doctor_uid} exists in user_profiles")
                        print(f"      - Email: {user.get('email')}")
                        print(f"      - Role: {user.get('role')}")
                        print(f"      - Name: {user.get('first_name')} {user.get('last_name')}")
                    else:
                        print(f"   ⚠️  Doctor UID {doctor_uid} NOT found in user_profiles")
                        print(f"      💡 This is the problem! The UID in appointments doesn't match any user profile")
                except Exception as e:
                    print(f"   ❌ Error checking UID {doctor_uid}: {e}")
        
        print("\n" + "=" * 60)
        print("✅ Test complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_appointments_fetch()

