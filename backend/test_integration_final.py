#!/usr/bin/env python3
"""
Integration test for the complete MediChain system
"""
import sys
import os
import traceback

def test_system_integration():
    """Test complete system integration"""
    
    print("🧪 MEDICHAIN SYSTEM INTEGRATION TEST")
    print("=" * 50)
    
    results = {}
    
    # Test 1: Core imports
    print("1️⃣ Testing Core Imports...")
    try:
        from app import app
        from auth.firebase_auth import firebase_auth_service
        from services.simple_otp_manager import simple_otp_manager
        from db.supabase_client import SupabaseClient
        results["core_imports"] = "✅ PASS"
        print("   ✅ All core modules imported successfully")
    except Exception as e:
        results["core_imports"] = f"❌ FAIL: {e}"
        print(f"   ❌ Core imports failed: {e}")
    
    # Test 2: Flask app configuration
    print("2️⃣ Testing Flask App Configuration...")
    try:
        from app import app
        assert app is not None
        assert len(app.blueprints) >= 5  # Should have multiple blueprints
        results["flask_config"] = "✅ PASS"
        print(f"   ✅ Flask app configured with {len(app.blueprints)} blueprints")
    except Exception as e:
        results["flask_config"] = f"❌ FAIL: {e}"
        print(f"   ❌ Flask configuration failed: {e}")
    
    # Test 3: Firebase initialization
    print("3️⃣ Testing Firebase Authentication...")
    try:
        import firebase_admin
        from firebase_admin import auth
        
        # Check if Firebase is initialized
        if firebase_admin._apps:
            results["firebase"] = "✅ PASS"
            print("   ✅ Firebase Admin SDK initialized")
        else:
            results["firebase"] = "⚠️ WARN: Firebase not initialized"
            print("   ⚠️ Firebase Admin SDK not initialized")
    except Exception as e:
        results["firebase"] = f"❌ FAIL: {e}"
        print(f"   ❌ Firebase test failed: {e}")
    
    # Test 4: Supabase connection
    print("4️⃣ Testing Supabase Database...")
    try:
        from db.supabase_client import SupabaseClient
        supabase = SupabaseClient()
        
        # Test basic connection
        health_check = supabase.client.table('user_profiles').select('email').limit(1).execute()
        results["supabase"] = "✅ PASS"
        print("   ✅ Supabase database connection working")
    except Exception as e:
        results["supabase"] = f"❌ FAIL: {e}"
        print(f"   ❌ Supabase test failed: {e}")
    
    # Test 5: Password Reset System
    print("5️⃣ Testing Password Reset System...")
    try:
        from services.simple_otp_manager import simple_otp_manager
        
        # Test OTP generation
        test_result = simple_otp_manager.store_otp('test@test.com', 'https://test.com')
        assert test_result['success'] == True
        
        # Test OTP verification
        otp_code = test_result['otp_code']
        verify_result = simple_otp_manager.verify_otp('test@test.com', otp_code)
        assert verify_result['success'] == True
        
        results["password_reset"] = "✅ PASS"
        print("   ✅ Password reset system functional")
    except Exception as e:
        results["password_reset"] = f"❌ FAIL: {e}"
        print(f"   ❌ Password reset test failed: {e}")
    
    # Test 6: API Routes Registration
    print("6️⃣ Testing API Routes...")
    try:
        from app import app
        
        # Check if key blueprints are registered
        required_blueprints = ['auth', 'medical', 'appointments']
        registered_blueprints = list(app.blueprints.keys())
        
        missing_blueprints = [bp for bp in required_blueprints if bp not in registered_blueprints]
        
        if not missing_blueprints:
            results["api_routes"] = "✅ PASS"
            print(f"   ✅ All required blueprints registered: {registered_blueprints}")
        else:
            results["api_routes"] = f"⚠️ WARN: Missing blueprints: {missing_blueprints}"
            print(f"   ⚠️ Missing blueprints: {missing_blueprints}")
    except Exception as e:
        results["api_routes"] = f"❌ FAIL: {e}"
        print(f"   ❌ API routes test failed: {e}")
    
    # Test 7: Environment Configuration
    print("7️⃣ Testing Environment Configuration...")
    try:
        required_env_vars = ['GMAIL_USER', 'GMAIL_APP_PASSWORD']
        missing_vars = []
        
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if not missing_vars:
            results["environment"] = "✅ PASS"
            print("   ✅ All required environment variables configured")
        else:
            results["environment"] = f"⚠️ WARN: Missing env vars: {missing_vars}"
            print(f"   ⚠️ Missing environment variables: {missing_vars}")
    except Exception as e:
        results["environment"] = f"❌ FAIL: {e}"
        print(f"   ❌ Environment test failed: {e}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 INTEGRATION TEST RESULTS")
    print("=" * 50)
    
    passed_tests = sum(1 for result in results.values() if "✅ PASS" in result)
    warned_tests = sum(1 for result in results.values() if "⚠️ WARN" in result)
    failed_tests = sum(1 for result in results.values() if "❌ FAIL" in result)
    
    for test_name, result in results.items():
        print(f"{test_name.replace('_', ' ').title()}: {result}")
    
    print(f"\n📈 SUMMARY: {passed_tests} passed, {warned_tests} warnings, {failed_tests} failed")
    
    if failed_tests == 0:
        print("🎉 SYSTEM READY FOR DEPLOYMENT!")
        return True
    else:
        print("❌ SYSTEM NEEDS FIXES BEFORE DEPLOYMENT")
        return False

if __name__ == "__main__":
    # Change to backend directory
    backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.insert(0, backend_path)
    
    success = test_system_integration()
    sys.exit(0 if success else 1)