#!/usr/bin/env python3
"""
Master User Data Cleanup Script
Clears both Firebase Auth and Supabase data for complete reset
"""

import os
import sys
import subprocess
from pathlib import Path

def run_script(script_name, description):
    """Run a Python script and return success status"""
    try:
        print(f"\n🔄 Running {description}...")
        print("=" * 60)
        
        result = subprocess.run([
            sys.executable, script_name
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"⚠️ {description} completed with warnings (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False

def main():
    """Main cleanup orchestrator"""
    print("🧹 MediChain Master Cleanup Tool")
    print("=" * 60)
    print("This will clear ALL user data from both Firebase and Supabase")
    print("⚠️ WARNING: This action cannot be undone!")
    print("=" * 60)
    
    # Confirm the operation
    confirm = input("\nAre you sure you want to proceed with complete data cleanup? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Operation cancelled")
        return
    
    print("\n🚀 Starting complete cleanup process...")
    
    # Step 1: Clear Supabase data
    supabase_success = run_script('clear_supabase_data.py', 'Supabase Data Cleanup')
    
    # Step 2: Clear Firebase users
    firebase_success = run_script('clear_firebase_users.py', 'Firebase Auth Cleanup')
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 CLEANUP SUMMARY")
    print("=" * 60)
    
    if supabase_success and firebase_success:
        print("✅ Complete cleanup successful!")
        print("📝 You can now create new user accounts")
        print("\n🔄 To restart the system:")
        print("   1. Frontend: npm start")
        print("   2. Backend: python app.py")
        print("   3. AI Server: python ai_server.py")
    else:
        print("⚠️ Cleanup completed with some issues:")
        if not supabase_success:
            print("   - Supabase cleanup had issues")
        if not firebase_success:
            print("   - Firebase cleanup had issues")
        print("\nℹ️ You may need to run the individual scripts manually")
    
    print("\n👋 Cleanup process finished")

if __name__ == "__main__":
    main()