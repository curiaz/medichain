#!/usr/bin/env python3
"""
Script to fix UID mismatches in appointments table
This script helps identify and fix appointments where the doctor_firebase_uid
doesn't match the logged-in user's Firebase UID.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.supabase_client import SupabaseClient

def fix_appointment_uids():
    """Fix UID mismatches in appointments table"""
    try:
        print("=" * 60)
        print("🔧 Appointment UID Fixer")
        print("=" * 60)
        
        # Initialize Supabase client
        supabase = SupabaseClient()
        
        if not supabase or not supabase.service_client:
            print("❌ ERROR: Supabase service_client not initialized")
            print("💡 Make sure SUPABASE_SERVICE_KEY is set in .env file")
            return
        
        # Step 1: Get all appointments
        print("\n📋 Step 1: Fetching all appointments...")
        appointments_response = supabase.service_client.table("appointments").select("*").execute()
        
        if not appointments_response.data:
            print("ℹ️  No appointments found in database")
            return
        
        appointments = appointments_response.data
        print(f"✅ Found {len(appointments)} appointments")
        
        # Step 2: Get all unique doctor UIDs from appointments
        doctor_uids = set()
        for apt in appointments:
            doctor_uid = apt.get("doctor_firebase_uid")
            if doctor_uid:
                doctor_uids.add(doctor_uid)
        
        print(f"\n👨‍⚕️ Step 2: Found {len(doctor_uids)} unique doctor UIDs in appointments:")
        for uid in doctor_uids:
            print(f"   - {uid}")
        
        # Step 3: Get all user profiles with doctor role
        print(f"\n👤 Step 3: Fetching doctor user profiles...")
        doctors_response = supabase.service_client.table("user_profiles").select("firebase_uid, email, first_name, last_name").eq("role", "doctor").execute()
        
        if not doctors_response.data:
            print("⚠️  No doctor profiles found")
            return
        
        doctors = doctors_response.data
        print(f"✅ Found {len(doctors)} doctor profiles")
        
        # Step 4: Check for UID mismatches
        print(f"\n🔍 Step 4: Checking for UID mismatches...")
        doctor_profile_uids = {d["firebase_uid"] for d in doctors}
        
        mismatches = []
        for uid in doctor_uids:
            if uid not in doctor_profile_uids:
                # Count appointments with this UID
                count = sum(1 for apt in appointments if apt.get("doctor_firebase_uid") == uid)
                mismatches.append({
                    "uid": uid,
                    "appointment_count": count,
                    "issue": "UID exists in appointments but not in user_profiles"
                })
                print(f"⚠️  UID {uid} has {count} appointments but no matching user profile")
        
        # Step 5: Show mapping suggestions
        print(f"\n💡 Step 5: UID Mapping Suggestions")
        print("=" * 60)
        
        if mismatches:
            print("⚠️  Found UID mismatches:")
            for mismatch in mismatches:
                print(f"\n   UID: {mismatch['uid']}")
                print(f"   Appointments: {mismatch['appointment_count']}")
                print(f"   Issue: {mismatch['issue']}")
                print(f"\n   💡 To fix:")
                print(f"   1. Find the correct doctor Firebase UID")
                print(f"   2. Run this SQL in Supabase:")
                print(f"      UPDATE appointments")
                print(f"      SET doctor_firebase_uid = 'CORRECT_UID'")
                print(f"      WHERE doctor_firebase_uid = '{mismatch['uid']}';")
        else:
            print("✅ No UID mismatches found!")
            print("\n📊 Summary:")
            print(f"   - Total appointments: {len(appointments)}")
            print(f"   - Unique doctor UIDs: {len(doctor_uids)}")
            print(f"   - Doctor profiles: {len(doctors)}")
            print(f"   - All UIDs match: ✅")
        
        # Step 6: Show current appointments summary
        print(f"\n📊 Step 6: Current Appointments Summary")
        print("=" * 60)
        for uid in doctor_uids:
            count = sum(1 for apt in appointments if apt.get("doctor_firebase_uid") == uid)
            doctor_profile = next((d for d in doctors if d["firebase_uid"] == uid), None)
            if doctor_profile:
                name = f"{doctor_profile.get('first_name', '')} {doctor_profile.get('last_name', '')}".strip()
                email = doctor_profile.get("email", "N/A")
                print(f"   ✅ {uid}: {count} appointments - Dr. {name} ({email})")
            else:
                print(f"   ⚠️  {uid}: {count} appointments - NO PROFILE FOUND")
        
        print("\n" + "=" * 60)
        print("✅ Diagnostic complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    load_dotenv()
    fix_appointment_uids()

"""
Script to fix UID mismatches in appointments table
This script helps identify and fix appointments where the doctor_firebase_uid
doesn't match the logged-in user's Firebase UID.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.supabase_client import SupabaseClient

def fix_appointment_uids():
    """Fix UID mismatches in appointments table"""
    try:
        print("=" * 60)
        print("🔧 Appointment UID Fixer")
        print("=" * 60)
        
        # Initialize Supabase client
        supabase = SupabaseClient()
        
        if not supabase or not supabase.service_client:
            print("❌ ERROR: Supabase service_client not initialized")
            print("💡 Make sure SUPABASE_SERVICE_KEY is set in .env file")
            return
        
        # Step 1: Get all appointments
        print("\n📋 Step 1: Fetching all appointments...")
        appointments_response = supabase.service_client.table("appointments").select("*").execute()
        
        if not appointments_response.data:
            print("ℹ️  No appointments found in database")
            return
        
        appointments = appointments_response.data
        print(f"✅ Found {len(appointments)} appointments")
        
        # Step 2: Get all unique doctor UIDs from appointments
        doctor_uids = set()
        for apt in appointments:
            doctor_uid = apt.get("doctor_firebase_uid")
            if doctor_uid:
                doctor_uids.add(doctor_uid)
        
        print(f"\n👨‍⚕️ Step 2: Found {len(doctor_uids)} unique doctor UIDs in appointments:")
        for uid in doctor_uids:
            print(f"   - {uid}")
        
        # Step 3: Get all user profiles with doctor role
        print(f"\n👤 Step 3: Fetching doctor user profiles...")
        doctors_response = supabase.service_client.table("user_profiles").select("firebase_uid, email, first_name, last_name").eq("role", "doctor").execute()
        
        if not doctors_response.data:
            print("⚠️  No doctor profiles found")
            return
        
        doctors = doctors_response.data
        print(f"✅ Found {len(doctors)} doctor profiles")
        
        # Step 4: Check for UID mismatches
        print(f"\n🔍 Step 4: Checking for UID mismatches...")
        doctor_profile_uids = {d["firebase_uid"] for d in doctors}
        
        mismatches = []
        for uid in doctor_uids:
            if uid not in doctor_profile_uids:
                # Count appointments with this UID
                count = sum(1 for apt in appointments if apt.get("doctor_firebase_uid") == uid)
                mismatches.append({
                    "uid": uid,
                    "appointment_count": count,
                    "issue": "UID exists in appointments but not in user_profiles"
                })
                print(f"⚠️  UID {uid} has {count} appointments but no matching user profile")
        
        # Step 5: Show mapping suggestions
        print(f"\n💡 Step 5: UID Mapping Suggestions")
        print("=" * 60)
        
        if mismatches:
            print("⚠️  Found UID mismatches:")
            for mismatch in mismatches:
                print(f"\n   UID: {mismatch['uid']}")
                print(f"   Appointments: {mismatch['appointment_count']}")
                print(f"   Issue: {mismatch['issue']}")
                print(f"\n   💡 To fix:")
                print(f"   1. Find the correct doctor Firebase UID")
                print(f"   2. Run this SQL in Supabase:")
                print(f"      UPDATE appointments")
                print(f"      SET doctor_firebase_uid = 'CORRECT_UID'")
                print(f"      WHERE doctor_firebase_uid = '{mismatch['uid']}';")
        else:
            print("✅ No UID mismatches found!")
            print("\n📊 Summary:")
            print(f"   - Total appointments: {len(appointments)}")
            print(f"   - Unique doctor UIDs: {len(doctor_uids)}")
            print(f"   - Doctor profiles: {len(doctors)}")
            print(f"   - All UIDs match: ✅")
        
        # Step 6: Show current appointments summary
        print(f"\n📊 Step 6: Current Appointments Summary")
        print("=" * 60)
        for uid in doctor_uids:
            count = sum(1 for apt in appointments if apt.get("doctor_firebase_uid") == uid)
            doctor_profile = next((d for d in doctors if d["firebase_uid"] == uid), None)
            if doctor_profile:
                name = f"{doctor_profile.get('first_name', '')} {doctor_profile.get('last_name', '')}".strip()
                email = doctor_profile.get("email", "N/A")
                print(f"   ✅ {uid}: {count} appointments - Dr. {name} ({email})")
            else:
                print(f"   ⚠️  {uid}: {count} appointments - NO PROFILE FOUND")
        
        print("\n" + "=" * 60)
        print("✅ Diagnostic complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    load_dotenv()
    fix_appointment_uids()

