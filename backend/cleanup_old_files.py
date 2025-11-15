#!/usr/bin/env python3
"""
Cleanup script to remove old CSV files, unused models, and deprecated code
"""

import os
import sys

def main():
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Files to delete
    files_to_delete = [
        # Old CSV files (now in Supabase)
        'condition - Sheet1.csv',
        'condition_reason - Sheet1.csv',
        'action_medication - Sheet1.csv',
        
        # Old model files
        'streamlined_model_v5.pkl',
        
        # Deprecated AI implementations
        'comprehensive_ai_diagnosis.py',
        'simple_ai_server.py',
        'nlp_app.py',
        
        # Old test files (if any specific ones exist)
        # We keep the new test files: test_supabase_ai_data.py, test_ai_supabase.py
    ]
    
    print("=" * 60)
    print("🧹 Cleaning up old files...")
    print("=" * 60)
    
    deleted_count = 0
    skipped_count = 0
    error_count = 0
    
    for filename in files_to_delete:
        filepath = os.path.join(backend_dir, filename)
        
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"✅ Deleted: {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ Error deleting {filename}: {e}")
                error_count += 1
        else:
            print(f"⏭️  Skipped: {filename} (not found)")
            skipped_count += 1
    
    print("\n" + "=" * 60)
    print("📊 Cleanup Summary:")
    print(f"   ✅ Deleted: {deleted_count} files")
    print(f"   ⏭️  Skipped: {skipped_count} files")
    print(f"   ❌ Errors: {error_count} files")
    print("=" * 60)
    
    if error_count > 0:
        print("\n⚠️  Some files could not be deleted (may be in use).")
        print("   Please close any programs using these files and run again.")
        return False
    
    print("\n✅ Cleanup completed successfully!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
