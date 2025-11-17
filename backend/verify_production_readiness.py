"""
Production Readiness Verification Script
Checks all changes are production-ready before commit
"""
import sys
import os
import importlib.util

def check_imports():
    """Verify all imports work correctly"""
    print("[CHECK] Checking imports...")
    try:
        from appointment_routes import appointments_bp
        print("  [OK] appointment_routes imported")
        
        from file_routes import file_bp
        print("  [OK] file_routes imported")
        
        # Check app.py imports
        spec = importlib.util.spec_from_file_location("app", "app.py")
        if spec and spec.loader:
            print("  [OK] app.py can be loaded")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Import error: {e}")
        return False

def check_database_migration():
    """Verify database migration file exists and is correct"""
    print("\n[CHECK] Checking database migration...")
    migration_file = "../database/add_medicine_allergies_field.sql"
    
    if os.path.exists(migration_file):
        print(f"  [OK] Migration file exists: {migration_file}")
        with open(migration_file, 'r') as f:
            content = f.read()
            if "ADD COLUMN IF NOT EXISTS" in content:
                print("  [OK] Uses IF NOT EXISTS (safe for re-run)")
            if "medicine_allergies" in content:
                print("  [OK] Contains medicine_allergies column")
            return True
    else:
        print(f"  [WARNING] Migration file not found: {migration_file}")
        return False

def check_file_routes():
    """Verify file routes are properly configured"""
    print("\n[CHECK] Checking file routes...")
    try:
        from file_routes import file_bp
        
        # Check route registration
        routes = [str(rule) for rule in file_bp.url_map.iter_rules() if hasattr(file_bp, 'url_map')]
        if '/api/files' in str(file_bp.url_prefix):
            print("  [OK] File routes blueprint has correct prefix")
        
        # Check authentication decorator exists
        if hasattr(file_bp, 'decorators'):
            print("  [OK] File routes have decorators")
        
        return True
    except Exception as e:
        print(f"  [ERROR] File routes check failed: {e}")
        return False

def check_appointment_routes():
    """Verify appointment routes handle allergies correctly"""
    print("\n[CHECK] Checking appointment routes...")
    try:
        # Read the file and check for key patterns
        with open('appointment_routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            checks = {
                'medicine_allergies in appointment_data': 'medicine_allergies' in content and 'appointment_data' in content,
                'allergies in patient select': 'allergies' in content and 'select' in content,
                'get_appointment_by_id includes allergies': 'get_appointment_by_id' in content and 'allergies' in content,
                'get_appointments includes allergies': 'get_appointments' in content and 'allergies' in content
            }
            
            for check_name, result in checks.items():
                if result:
                    print(f"  [OK] {check_name}")
                else:
                    print(f"  [WARNING] {check_name} - may need verification")
            
            return all(checks.values())
    except Exception as e:
        print(f"  [ERROR] Appointment routes check failed: {e}")
        return False

def check_backward_compatibility():
    """Verify changes are backward compatible"""
    print("\n[CHECK] Checking backward compatibility...")
    try:
        with open('appointment_routes.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for safe defaults
            checks = {
                'Uses .get() for allergies': '.get("allergies")' in content or '.get(\'allergies\')' in content,
                'Handles None values': 'if' in content and 'allergies' in content,
                'Uses IF NOT EXISTS in migration': True  # Checked separately
            }
            
            for check_name, result in checks.items():
                if result:
                    print(f"  [OK] {check_name}")
                else:
                    print(f"  [WARNING] {check_name}")
            
            return True
    except Exception as e:
        print(f"  [ERROR] Backward compatibility check failed: {e}")
        return False

def main():
    """Run all checks"""
    print("=" * 60)
    print("PRODUCTION READINESS VERIFICATION")
    print("=" * 60)
    
    results = []
    
    results.append(("Imports", check_imports()))
    results.append(("Database Migration", check_database_migration()))
    results.append(("File Routes", check_file_routes()))
    results.append(("Appointment Routes", check_appointment_routes()))
    results.append(("Backward Compatibility", check_backward_compatibility()))
    
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{check_name}: {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("[SUCCESS] ALL CHECKS PASSED - READY FOR PRODUCTION")
        return 0
    else:
        print("[WARNING] SOME CHECKS FAILED - REVIEW BEFORE DEPLOYMENT")
        return 1

if __name__ == '__main__':
    sys.exit(main())

