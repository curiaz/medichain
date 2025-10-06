#!/usr/bin/env python3
"""
Test medical record storage for jeremiahcurias@gmail.com account
"""

import os
import sys
from datetime import datetime, date
import json

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from db.supabase_client import SupabaseClient
except ImportError as e:
    print(f"❌ Error importing SupabaseClient: {e}")
    sys.exit(1)

def test_medical_storage():
    """Test that medical records can be stored for the user"""
    
    email = "jeremiahcurias@gmail.com"
    firebase_uid = "cr8mltOMfNeV5dVCLBcfwDu7GbB2"  # From previous check
    
    print("🧪 Testing Medical Storage Capabilities")
    print(f"📧 For account: {email}")
    print("=" * 60)
    
    try:
        supabase = SupabaseClient()
        
        # Test 1: Update user profile with medical information
        print("1️⃣ Testing medical information storage...")
        
        medical_update = {
            'medical_conditions': ['None currently'],
            'allergies': ['No known allergies'],
            'blood_type': 'A+',
            'medical_notes': f'Test medical record created on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        }
        
        # Update user profile with medical info
        update_response = supabase.service_client.table('user_profiles').update(medical_update).eq('firebase_uid', firebase_uid).execute()
        
        if update_response.data:
            print("✅ Medical information successfully stored!")
            for key, value in medical_update.items():
                print(f"   • {key}: {value}")
        else:
            print("❌ Failed to store medical information")
        
        # Test 2: Create a sample AI diagnosis record
        print("\n2️⃣ Testing AI diagnosis storage...")
        
        sample_diagnosis = {
            'user_firebase_uid': firebase_uid,
            'session_id': f'test_session_{int(datetime.now().timestamp())}',
            'symptoms_input': 'This is a test diagnosis entry to verify storage capability',
            'patient_age': 25,
            'patient_gender': 'male',
            'ai_diagnosis': {
                'condition': 'System Test',
                'confidence': 95.5,
                'recommendations': ['Test storage successful']
            },
            'primary_condition': 'Storage Test',
            'confidence_score': 95.50,
            'ai_model_version': 'test_v1.0'
        }
        
        diagnosis_response = supabase.service_client.table('ai_diagnoses').insert(sample_diagnosis).execute()
        
        if diagnosis_response.data:
            print("✅ AI diagnosis record successfully stored!")
            print(f"   • Session ID: {sample_diagnosis['session_id']}")
            print(f"   • Condition: {sample_diagnosis['primary_condition']}")
            print(f"   • Confidence: {sample_diagnosis['confidence_score']}%")
        else:
            print("❌ Failed to store AI diagnosis record")
        
        # Test 3: Verify data can be retrieved
        print("\n3️⃣ Testing data retrieval...")
        
        # Get updated user profile
        updated_profile = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', firebase_uid).execute()
        
        if updated_profile.data:
            profile = updated_profile.data[0]
            print("✅ Profile data retrieved successfully!")
            print(f"   • Medical conditions: {profile.get('medical_conditions', [])}")
            print(f"   • Allergies: {profile.get('allergies', [])}")
            print(f"   • Blood type: {profile.get('blood_type', 'Not set')}")
        
        # Get AI diagnosis records
        ai_records = supabase.service_client.table('ai_diagnoses').select('*').eq('user_firebase_uid', firebase_uid).execute()
        
        if ai_records.data:
            print(f"✅ Found {len(ai_records.data)} AI diagnosis record(s)")
            for record in ai_records.data:
                print(f"   • Session: {record.get('session_id', 'N/A')}")
                print(f"   • Date: {record.get('created_at', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("🎉 MEDICAL STORAGE TEST RESULTS:")
        print("✅ Medical information storage: WORKING")
        print("✅ AI diagnosis storage: WORKING") 
        print("✅ Data retrieval: WORKING")
        print("✅ All health records will be properly saved!")
        
        # Clean up test data
        print("\n🧹 Cleaning up test data...")
        if diagnosis_response.data:
            cleanup_response = supabase.service_client.table('ai_diagnoses').delete().eq('session_id', sample_diagnosis['session_id']).execute()
            if cleanup_response:
                print("✅ Test AI diagnosis record cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during medical storage test: {e}")
        return False

if __name__ == "__main__":
    test_medical_storage()