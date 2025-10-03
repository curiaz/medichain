"""
Settings Backend Verification Script
Checks all components are properly set up
"""
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} NOT FOUND: {filepath}")
        return False

def check_imports():
    """Check if required imports work"""
    print("\n🔍 Checking Python imports...")
    
    try:
        from flask import Blueprint, request, jsonify
        print("✅ Flask imports working")
    except ImportError as e:
        print(f"❌ Flask import error: {e}")
        return False
    
    try:
        from firebase_admin import auth
        print("✅ Firebase Admin imports working")
    except ImportError as e:
        print(f"❌ Firebase Admin import error: {e}")
        return False
    
    try:
        from datetime import datetime, timedelta
        print("✅ Datetime imports working")
    except ImportError as e:
        print(f"❌ Datetime import error: {e}")
        return False
    
    return True

def check_env_variables():
    """Check if required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    required_vars = [
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    all_set = True
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is NOT set")
            all_set = False
    
    return all_set

def check_backend_structure():
    """Check backend file structure"""
    print("\n🔍 Checking backend file structure...")
    
    files_to_check = [
        ('backend/settings_routes.py', 'Settings routes file'),
        ('backend/app.py', 'Main application file'),
        ('backend/auth/firebase_auth.py', 'Firebase auth module'),
        ('backend/db/supabase_client.py', 'Supabase client module'),
        ('database/settings_complete_schema.sql', 'Database schema'),
    ]
    
    all_exist = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist

def verify_settings_routes():
    """Verify settings routes file content"""
    print("\n🔍 Verifying settings_routes.py content...")
    
    try:
        with open('backend/settings_routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ('settings_bp', 'Blueprint definition'),
            ('get_notification_preferences', 'GET notifications endpoint'),
            ('update_notification_preferences', 'PUT notifications endpoint'),
            ('change_password', 'Password change endpoint'),
            ('deactivate_account', 'Account deactivation endpoint'),
            ('delete_account', 'Account deletion endpoint'),
            ('get_security_audit_log', 'Audit log endpoint'),
            ('validate_password_strength', 'Password validation function'),
            ('log_security_event', 'Security logging function'),
        ]
        
        all_found = True
        for check_str, description in checks:
            if check_str in content:
                print(f"✅ {description} found")
            else:
                print(f"❌ {description} NOT FOUND")
                all_found = False
        
        return all_found
    
    except Exception as e:
        print(f"❌ Error reading settings_routes.py: {e}")
        return False

def check_app_registration():
    """Check if settings blueprint is registered in app.py"""
    print("\n🔍 Checking app.py blueprint registration...")
    
    try:
        with open('backend/app.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'from settings_routes import settings_bp' in content:
            print("✅ Settings blueprint import found")
        else:
            print("❌ Settings blueprint import NOT FOUND")
            return False
        
        if 'register_blueprint(settings_bp)' in content:
            print("✅ Settings blueprint registration found")
        else:
            print("❌ Settings blueprint registration NOT FOUND")
            return False
        
        return True
    
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def main():
    """Main verification function"""
    print("=" * 60)
    print("🔧 SETTINGS BACKEND VERIFICATION")
    print("=" * 60)
    
    results = {
        'File Structure': check_backend_structure(),
        'Python Imports': check_imports(),
        'Environment Variables': check_env_variables(),
        'Settings Routes Content': verify_settings_routes(),
        'App Registration': check_app_registration(),
    }
    
    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {check_name}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL CHECKS PASSED! Backend is ready to use!")
        print("\nNext steps:")
        print("1. Run database schema: database/settings_complete_schema.sql")
        print("2. Start backend: python backend/app.py")
        print("3. Test endpoints with Postman or curl")
    else:
        print("⚠️  SOME CHECKS FAILED! Please fix the issues above.")
        print("\nCommon fixes:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Set environment variables in .env file")
        print("3. Verify file paths are correct")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
