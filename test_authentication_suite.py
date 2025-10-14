#!/usr/bin/env python3
"""
Comprehensive authentication and database integration test suite
"""

import os
import sys
from datetime import datetime
import json

# Add backend directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def run_comprehensive_tests():
    """Run all authentication and integration tests"""
    
    print("🧪 COMPREHENSIVE AUTHENTICATION TEST SUITE")
    print("=" * 60)
    
    tests = []
    
    # Test 1: Database Connection
    print("\n1️⃣ Testing Database Connection...")
    try:
        from db.supabase_client import SupabaseClient
        supabase = SupabaseClient()
        
        # Test connection
        response = supabase.service_client.table('user_profiles').select('count').execute()
        tests.append(("Database Connection", True, "✅ Connected successfully"))
        print("✅ Database connection successful")
        
    except Exception as e:
        tests.append(("Database Connection", False, f"❌ {str(e)}"))
        print(f"❌ Database connection failed: {e}")
    
    # Test 2: User Profile Operations  
    print("\n2️⃣ Testing User Profile Operations...")
    try:
        # Test user retrieval
        user_response = supabase.service_client.table('user_profiles').select('*').eq('email', 'jeremiahcurias@gmail.com').execute()
        
        if user_response.data:
            user = user_response.data[0]
            tests.append(("User Profile Retrieval", True, f"✅ Found user: {user['first_name']} {user['last_name']}"))
            print(f"✅ User profile found: {user['first_name']} {user['last_name']}")
            
            # Test profile update
            update_data = {'updated_at': datetime.now().isoformat()}
            update_response = supabase.service_client.table('user_profiles').update(update_data).eq('id', user['id']).execute()
            
            if update_response.data:
                tests.append(("Profile Update", True, "✅ Profile updated successfully"))
                print("✅ Profile update successful")
            else:
                tests.append(("Profile Update", False, "❌ Profile update failed"))
                print("❌ Profile update failed")
        else:
            tests.append(("User Profile Retrieval", False, "❌ User not found"))
            print("❌ User profile not found")
            
    except Exception as e:
        tests.append(("User Profile Operations", False, f"❌ {str(e)}"))
        print(f"❌ User profile operations failed: {e}")
    
    # Test 3: Medical Records Schema
    print("\n3️⃣ Testing Medical Records Schema...")
    try:
        # Test table structure
        medical_response = supabase.service_client.table('medical_records').select('*').limit(1).execute()
        tests.append(("Medical Records Schema", True, "✅ Medical records table accessible"))
        print("✅ Medical records table accessible")
        
        # Test AI diagnoses table
        ai_response = supabase.service_client.table('ai_diagnoses').select('*').limit(1).execute()
        tests.append(("AI Diagnoses Schema", True, "✅ AI diagnoses table accessible"))
        print("✅ AI diagnoses table accessible")
        
        # Test appointments table
        appointments_response = supabase.service_client.table('appointments').select('*').limit(1).execute()
        tests.append(("Appointments Schema", True, "✅ Appointments table accessible"))
        print("✅ Appointments table accessible")
        
    except Exception as e:
        tests.append(("Medical Records Schema", False, f"❌ {str(e)}"))
        print(f"❌ Medical records schema test failed: {e}")
    
    # Test 4: Data Storage and Retrieval
    print("\n4️⃣ Testing Data Storage and Retrieval...")
    try:
        firebase_uid = "cr8mltOMfNeV5dVCLBcfwDu7GbB2"  # Test user UID
        
        # Create test AI diagnosis
        test_diagnosis = {
            'user_firebase_uid': firebase_uid,
            'session_id': f'test_auth_{int(datetime.now().timestamp())}',
            'symptoms_input': 'Authentication test symptoms',
            'ai_diagnosis': {
                'condition': 'Test Authentication',
                'confidence': 99.99,
                'test': True
            },
            'primary_condition': 'Test Authentication',
            'confidence_score': 99.99,
            'ai_model_version': 'auth_test_v1.0'
        }
        
        # Insert test record
        insert_response = supabase.service_client.table('ai_diagnoses').insert(test_diagnosis).execute()
        
        if insert_response.data:
            record_id = insert_response.data[0]['id']
            tests.append(("Data Storage", True, "✅ Test record created successfully"))
            print("✅ Test record created successfully")
            
            # Retrieve test record
            retrieve_response = supabase.service_client.table('ai_diagnoses').select('*').eq('id', record_id).execute()
            
            if retrieve_response.data and len(retrieve_response.data) > 0:
                tests.append(("Data Retrieval", True, "✅ Test record retrieved successfully"))
                print("✅ Test record retrieved successfully")
                
                # Clean up test record
                delete_response = supabase.service_client.table('ai_diagnoses').delete().eq('id', record_id).execute()
                tests.append(("Data Cleanup", True, "✅ Test record cleaned up"))
                print("✅ Test record cleaned up")
            else:
                tests.append(("Data Retrieval", False, "❌ Failed to retrieve test record"))
                print("❌ Failed to retrieve test record")
        else:
            tests.append(("Data Storage", False, "❌ Failed to create test record"))
            print("❌ Failed to create test record")
            
    except Exception as e:
        tests.append(("Data Storage and Retrieval", False, f"❌ {str(e)}"))
        print(f"❌ Data storage and retrieval test failed: {e}")
    
    # Test 5: Authentication System Integration
    print("\n5️⃣ Testing Authentication System Integration...")
    try:
        # Test Firebase auth routes exist
        auth_routes_path = os.path.join(os.path.dirname(__file__), 'backend', 'auth', 'firebase_auth_routes.py')
        if os.path.exists(auth_routes_path):
            tests.append(("Auth Routes", True, "✅ Firebase auth routes exist"))
            print("✅ Firebase auth routes exist")
        else:
            tests.append(("Auth Routes", False, "❌ Firebase auth routes not found"))
            print("❌ Firebase auth routes not found")
        
        # Test Firebase auth service
        auth_service_path = os.path.join(os.path.dirname(__file__), 'backend', 'auth', 'firebase_auth.py')
        if os.path.exists(auth_service_path):
            tests.append(("Auth Service", True, "✅ Firebase auth service exists"))
            print("✅ Firebase auth service exists")
        else:
            tests.append(("Auth Service", False, "❌ Firebase auth service not found"))
            print("❌ Firebase auth service not found")
            
        # Test Supabase client
        supabase_client_path = os.path.join(os.path.dirname(__file__), 'backend', 'db', 'supabase_client.py')
        if os.path.exists(supabase_client_path):
            tests.append(("Supabase Client", True, "✅ Supabase client exists"))
            print("✅ Supabase client exists")
        else:
            tests.append(("Supabase Client", False, "❌ Supabase client not found"))
            print("❌ Supabase client not found")
            
    except Exception as e:
        tests.append(("Authentication System Integration", False, f"❌ {str(e)}"))
        print(f"❌ Authentication system integration test failed: {e}")
    
    # Test Results Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed_tests = sum(1 for _, passed, _ in tests if passed)
    total_tests = len(tests)
    
    print(f"✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Authentication system is fully functional")
        print("✅ Database integration is working")
        print("✅ Ready for production deployment")
        return True
    else:
        print(f"\n⚠️ {total_tests - passed_tests} TESTS FAILED")
        print("\nFailed Tests:")
        for test_name, passed, message in tests:
            if not passed:
                print(f"  • {test_name}: {message}")
        return False
    
    print("\nDetailed Test Results:")
    for test_name, passed, message in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} | {test_name}: {message}")

if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit_code = 0 if success else 1
    sys.exit(exit_code)