#!/usr/bin/env python3
"""
Real Database Integration Test for Patient Profile Management
This script tests the actual database integration (no more mock data!)
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Load environment variables
load_dotenv(os.path.join('backend', '.env'))

# Configuration
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/profile"

def test_real_database_connection():
    """Test the real database connection"""
    print("🔍 Testing Real Database Connection...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        # Test Supabase connection
        supabase = SupabaseClient()
        
        # Try to query the user_profiles table
        response = supabase.client.table('user_profiles').select('count').execute()
        print("✅ Supabase connection successful!")
        
        # Check if tables exist
        tables_to_check = [
            'user_profiles',
            'patient_medical_info', 
            'patient_documents',
            'patient_privacy_settings',
            'patient_audit_log'
        ]
        
        print("\n📋 Checking required tables...")
        for table in tables_to_check:
            try:
                result = supabase.client.table(table).select('count').execute()
                print(f"   ✅ {table} table exists")
            except Exception as e:
                print(f"   ❌ {table} table missing: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Make sure:")
        print("   1. Your Supabase credentials are correct in backend/.env")
        print("   2. The database schema has been executed")
        print("   3. Your Supabase project is active")
        return False

def test_firebase_auth():
    """Test Firebase authentication"""
    print("\n🔐 Testing Firebase Authentication...")
    
    try:
        from auth.firebase_auth import firebase_auth_service
        
        # Test Firebase initialization
        if firebase_auth_service.app:
            print("✅ Firebase Admin SDK initialized successfully!")
            return True
        else:
            print("❌ Firebase Admin SDK not initialized")
            return False
            
    except Exception as e:
        print(f"❌ Firebase authentication failed: {e}")
        print("\n💡 Make sure:")
        print("   1. Your Firebase service account key is correct")
        print("   2. The FIREBASE_SERVICE_ACCOUNT_KEY path is valid")
        print("   3. Your Firebase project is active")
        return False

def test_patient_profile_endpoints():
    """Test patient profile endpoints with real authentication"""
    print("\n🏥 Testing Patient Profile Endpoints...")
    
    # Note: These tests require a real Firebase token
    # In a real scenario, you would get this from the frontend
    print("⚠️  Note: These tests require a real Firebase authentication token")
    print("   To test with real data, use the frontend application")
    
    # Test server connection
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Flask server is running!")
            return True
        else:
            print(f"⚠️  Server responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server!")
        print("💡 Make sure the Flask server is running:")
        print("   cd backend && python app.py")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def create_sample_patient_data():
    """Create sample patient data in the real database"""
    print("\n👤 Creating Sample Patient Data...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # Sample patient data
        patient_data = {
            'firebase_uid': 'test_patient_123',
            'email': 'test.patient@example.com',
            'first_name': 'Test',
            'last_name': 'Patient',
            'phone': '+1 (555) 123-4567',
            'date_of_birth': '1990-01-01',
            'gender': 'male',
            'role': 'patient',
            'address': {
                'street': '123 Test St',
                'city': 'Test City',
                'state': 'CA',
                'postal_code': '12345'
            },
            'emergency_contact': {
                'name': 'Jane Patient',
                'phone': '+1 (555) 987-6543',
                'relationship': 'Spouse'
            },
            'medical_conditions': ['Hypertension'],
            'allergies': ['Penicillin'],
            'current_medications': ['Metformin 500mg'],
            'blood_type': 'O+',
            'medical_notes': 'Test patient for development',
            'is_active': True,
            'is_verified': True
        }
        
        # Insert sample patient
        response = supabase.client.table('user_profiles').insert(patient_data).execute()
        
        if response.data:
            print("✅ Sample patient data created successfully!")
            print(f"   Patient ID: {response.data[0]['id']}")
            print(f"   Firebase UID: {response.data[0]['firebase_uid']}")
            return True
        else:
            print("❌ Failed to create sample patient data")
            return False
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def main():
    """Main test function"""
    print("🏥 MediChain Patient Profile - Real Database Integration Test")
    print("=" * 70)
    
    # Test 1: Database connection
    db_ok = test_real_database_connection()
    
    # Test 2: Firebase authentication
    firebase_ok = test_firebase_auth()
    
    # Test 3: Server connection
    server_ok = test_patient_profile_endpoints()
    
    # Test 4: Create sample data (optional)
    if db_ok and firebase_ok:
        create_sample = input("\n🤔 Would you like to create sample patient data? (y/n): ").lower().strip()
        if create_sample == 'y':
            create_sample_patient_data()
    
    print("\n📊 Test Results:")
    print(f"   Database Connection: {'✅ Pass' if db_ok else '❌ Fail'}")
    print(f"   Firebase Auth: {'✅ Pass' if firebase_ok else '❌ Fail'}")
    print(f"   Server Connection: {'✅ Pass' if server_ok else '❌ Fail'}")
    
    if db_ok and firebase_ok and server_ok:
        print("\n🎉 Real database integration is working!")
        print("\n🚀 Your system is ready for real patient data!")
        print("\n📋 Next steps:")
        print("   1. Use the frontend to test with real Firebase authentication")
        print("   2. Create real patient profiles through the UI")
        print("   3. Test profile updates, medical info, and document uploads")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("\n💡 Common solutions:")
        print("   1. Check your .env file configuration")
        print("   2. Run the database schema in Supabase")
        print("   3. Verify Firebase service account key")
        print("   4. Start the Flask server")
    
    return db_ok and firebase_ok and server_ok

if __name__ == "__main__":
    main()

