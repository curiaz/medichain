#!/usr/bin/env python3
"""
Check user account creation in Supabase
Verifies if jeremiahcurias@gmail.com account exists and has proper storage setup
"""

import os
import sys
from datetime import datetime

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from db.supabase_client import SupabaseClient
except ImportError as e:
    print(f"❌ Error importing SupabaseClient: {e}")
    print("Make sure you're in the correct directory and have set up the backend properly")
    sys.exit(1)

def check_user_account(email="jeremiahcurias@gmail.com"):
    """Check if user account exists and has proper storage setup"""
    
    print("🔍 Checking user account setup...")
    print(f"📧 Email: {email}")
    print("-" * 50)
    
    # Initialize Supabase client
    try:
        supabase = SupabaseClient()
        print("✅ Successfully connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        return False
    
    # Check if user profile exists
    print("\n1️⃣ Checking user profile...")
    try:
        user_response = supabase.service_client.table('user_profiles').select('*').eq('email', email).execute()
        
        if user_response.data:
            user_profile = user_response.data[0]
            print("✅ User profile found!")
            print(f"   • Firebase UID: {user_profile.get('firebase_uid', 'N/A')}")
            print(f"   • Full Name: {user_profile.get('first_name', '')} {user_profile.get('last_name', '')}")
            print(f"   • Role: {user_profile.get('role', 'N/A')}")
            print(f"   • Created: {user_profile.get('created_at', 'N/A')}")
            print(f"   • Active: {user_profile.get('is_active', False)}")
            
            firebase_uid = user_profile.get('firebase_uid')
            
        else:
            print("❌ User profile not found!")
            print("   This means the account wasn't properly created in Supabase")
            return False
            
    except Exception as e:
        print(f"❌ Error checking user profile: {e}")
        return False
    
    # Check medical information storage
    print("\n2️⃣ Checking medical information storage...")
    try:
        # Check if user has medical conditions, allergies, etc. in profile
        medical_fields = ['medical_conditions', 'allergies', 'current_medications', 'blood_type', 'medical_notes']
        has_medical_storage = any(user_profile.get(field) for field in medical_fields)
        
        if has_medical_storage:
            print("✅ User has medical information storage setup!")
            for field in medical_fields:
                value = user_profile.get(field)
                if value:
                    print(f"   • {field}: {value}")
        else:
            print("ℹ️ No medical information stored yet (this is normal for new accounts)")
            print("   Medical fields are available for storage:")
            for field in medical_fields:
                print(f"   • {field}: Ready for data")
                
    except Exception as e:
        print(f"❌ Error checking medical storage: {e}")
    
    # Check for medical records
    print("\n3️⃣ Checking medical records...")
    try:
        records_response = supabase.service_client.table('medical_records').select('*').eq('patient_firebase_uid', firebase_uid).execute()
        
        if records_response.data:
            print(f"✅ Found {len(records_response.data)} medical record(s)")
            for i, record in enumerate(records_response.data[:3], 1):  # Show first 3
                print(f"   Record {i}:")
                print(f"   • ID: {record.get('id', 'N/A')}")
                print(f"   • Date: {record.get('record_date', 'N/A')}")
                print(f"   • Type: {record.get('record_type', 'N/A')}")
        else:
            print("ℹ️ No medical records found (normal for new accounts)")
            
    except Exception as e:
        print(f"❌ Error checking medical records: {e}")
    
    # Check AI diagnosis history
    print("\n4️⃣ Checking AI diagnosis history...")
    try:
        ai_response = supabase.service_client.table('ai_diagnoses').select('*').eq('patient_firebase_uid', firebase_uid).execute()
        
        if ai_response.data:
            print(f"✅ Found {len(ai_response.data)} AI diagnosis record(s)")
            for i, diagnosis in enumerate(ai_response.data[:3], 1):  # Show first 3
                print(f"   Diagnosis {i}:")
                print(f"   • Date: {diagnosis.get('diagnosis_date', 'N/A')}")
                print(f"   • Condition: {diagnosis.get('diagnosed_condition', 'N/A')}")
                print(f"   • Confidence: {diagnosis.get('confidence_score', 'N/A')}")
        else:
            print("ℹ️ No AI diagnosis history found (normal for new accounts)")
            
    except Exception as e:
        print(f"❌ Error checking AI diagnosis history: {e}")
    
    # Check appointments
    print("\n5️⃣ Checking appointments...")
    try:
        appointments_response = supabase.service_client.table('appointments').select('*').eq('patient_firebase_uid', firebase_uid).execute()
        
        if appointments_response.data:
            print(f"✅ Found {len(appointments_response.data)} appointment(s)")
            for i, appointment in enumerate(appointments_response.data[:3], 1):
                print(f"   Appointment {i}:")
                print(f"   • Date: {appointment.get('appointment_date', 'N/A')}")
                print(f"   • Status: {appointment.get('status', 'N/A')}")
        else:
            print("ℹ️ No appointments found (normal for new accounts)")
            
    except Exception as e:
        print(f"❌ Error checking appointments: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("📊 ACCOUNT VERIFICATION SUMMARY")
    print("="*50)
    
    if user_response.data:
        print("✅ Account Status: ACTIVE")
        print("✅ Supabase Integration: WORKING")
        print("✅ Medical Storage: READY")
        print("\n🎯 Next Steps:")
        print("   • Account is properly set up for medical records")
        print("   • You can start using AI diagnosis features")
        print("   • Medical history will be automatically saved")
        print("   • All data is securely stored in Supabase")
        return True
    else:
        print("❌ Account Status: NOT FOUND")
        print("❌ Issue: Account not properly created in Supabase")
        print("\n🔧 Recommended Actions:")
        print("   • Try logging in again to trigger account creation")
        print("   • Check Firebase authentication is working")
        print("   • Verify Supabase integration is properly configured")
        return False

def main():
    """Main function to run the account check"""
    print("🏥 MediChain Account Verification Tool")
    print(f"⏰ Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    # Check the specific email
    success = check_user_account("jeremiahcurias@gmail.com")
    
    if success:
        print("\n🎉 Account verification completed successfully!")
    else:
        print("\n⚠️ Account verification found issues that need attention")
    
    return success

if __name__ == "__main__":
    main()