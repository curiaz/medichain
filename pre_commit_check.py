#!/usr/bin/env python3
"""
Pre-Commit Validation Script
Run this before committing to ensure system is ready
"""

import subprocess
import sys

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print('='*70)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: {description}")
            return True
        else:
            print(f"❌ FAILED: {description}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  PRE-COMMIT VALIDATION")
    print("  Verifying system before commit to master")
    print("="*70)
    
    checks = []
    
    # Check 1: Run pre-commit tests
    checks.append(run_command(
        "python -m pytest test_pre_commit.py -v",
        "Running pre-commit test suite"
    ))
    
    # Check 2: Run appointment tests
    checks.append(run_command(
        "python -m pytest test_appointment_complete.py -v",
        "Running appointment unit tests"
    ))
    
    # Check 3: Run API tests
    checks.append(run_command(
        "python -m pytest test_appointment_api.py -v",
        "Running API integration tests"
    ))
    
    # Check 4: Check backend health
    checks.append(run_command(
        "curl https://medichain.clinic/health",
        "Verifying backend health"
    ))
    
    # Summary
    print("\n" + "="*70)
    print("  VALIDATION SUMMARY")
    print("="*70)
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if all(checks):
        print("\n✅ ALL CHECKS PASSED - READY TO COMMIT")
        print("\nRecommended commands:")
        print("  git add .")
        print('  git commit -m "feat: Implement appointment system with testing"')
        print("  git push origin master")
        return 0
    else:
        print("\n❌ SOME CHECKS FAILED - FIX ISSUES BEFORE COMMITTING")
        return 1

if __name__ == '__main__':
    sys.exit(main())
