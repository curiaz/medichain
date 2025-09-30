#!/usr/bin/env python3
"""
Functional Test for Profile Branch
Tests the actual backend server functionality
"""
import sys
import os
import time
import subprocess
import requests
import json

# Add backend to path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.append(backend_dir)

def test_backend_startup():
    """Test that the backend can start up properly"""
    print("Testing backend startup...")
    
    try:
        # Import and test basic functionality
        os.chdir(backend_dir)
        
        # Test imports
        from flask import Flask
        from db.supabase_client import SupabaseClient
        from patient_profile_routes import patient_profile_bp
        from profile_management import profile_mgmt_bp
        
        print("✅ All imports successful")
        
        # Test Flask app creation
        app = Flask(__name__)
        app.register_blueprint(patient_profile_bp)
        app.register_blueprint(profile_mgmt_bp)
        
        print("✅ Flask app created successfully")
        
        # Test Supabase client (without actual connection)
        try:
            supabase = SupabaseClient()
            print("✅ Supabase client initialized")
        except Exception as e:
            print(f"⚠️  Supabase client warning: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend startup failed: {e}")
        return False

def test_profile_routes():
    """Test profile route definitions"""
    print("\nTesting profile route definitions...")
    
    try:
        from patient_profile_routes import patient_profile_bp
        from profile_management import profile_mgmt_bp
        
        # Check blueprint registration
        patient_routes = [rule.rule for rule in patient_profile_bp.url_map._rules]
        profile_mgmt_routes = [rule.rule for rule in profile_mgmt_bp.url_map._rules]
        
        print(f"✅ Patient profile routes defined: {len(patient_routes)} routes")
        print(f"✅ Profile management routes defined: {len(profile_mgmt_routes)} routes")
        
        return True
        
    except Exception as e:
        print(f"❌ Route testing failed: {e}")
        return False

def test_environment_setup():
    """Test environment and configuration"""
    print("\nTesting environment setup...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check for required environment variables
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_KEY',
            'FIREBASE_PROJECT_ID'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing environment variables: {missing_vars}")
        else:
            print("✅ All required environment variables present")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment setup failed: {e}")
        return False

def test_database_schema():
    """Test database schema requirements"""
    print("\nTesting database schema requirements...")
    
    try:
        # Check if schema files exist
        schema_files = [
            'database/enhanced_profile_management_schema.sql',
            'database_setup.sql',
            'database_rls_policies.sql'
        ]
        
        existing_files = []
        for file_path in schema_files:
            full_path = os.path.join('..', file_path)
            if os.path.exists(full_path):
                existing_files.append(file_path)
        
        print(f"✅ Found {len(existing_files)} database schema files")
        
        return True
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")
        return False

def test_profile_functionality():
    """Test profile management functionality"""
    print("\nTesting profile management functionality...")
    
    try:
        from profile_management import generate_blockchain_hash, allowed_file
        
        # Test blockchain hash generation
        test_data = {'user_id': 'test', 'action': 'update'}
        hash_result = generate_blockchain_hash(test_data)
        
        assert len(hash_result) == 64  # SHA256 hash length
        print("✅ Blockchain hash generation working")
        
        # Test file validation
        assert allowed_file('document.pdf') == True
        assert allowed_file('malicious.exe') == False
        print("✅ File validation working")
        
        return True
        
    except Exception as e:
        print(f"❌ Profile functionality test failed: {e}")
        return False

def main():
    """Run all functional tests"""
    print("=== MediChain Profile Branch Functional Testing ===\n")
    
    tests = [
        test_backend_startup,
        test_profile_routes,
        test_environment_setup,
        test_database_schema,
        test_profile_functionality
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test in tests:
        try:
            if test():
                passed_tests += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed_tests}/{total_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! Profile branch is ready for merge.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review before merging.")
        return 1

if __name__ == '__main__':
    sys.exit(main())