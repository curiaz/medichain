#!/usr/bin/env python3
"""
Test script to verify Supabase AI data migration
"""

import sys
import os
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from db.supabase_client import SupabaseClient

def test_supabase_ai_tables():
    """Test fetching AI data from Supabase tables"""
    print("=" * 60)
    print("🧪 Testing Supabase AI Data Migration")
    print("=" * 60)
    
    try:
        # Initialize Supabase client
        print("\n1️⃣  Initializing Supabase client...")
        supabase = SupabaseClient()
        
        if not supabase.client:
            print("❌ Supabase client not initialized")
            return False
        
        print("✅ Supabase client initialized")
        
        # Test conditions table
        print("\n2️⃣  Fetching conditions table...")
        conditions = supabase.get_conditions()
        print(f"✅ Fetched {len(conditions)} conditions")
        
        if conditions:
            print("\n📋 Sample condition record:")
            sample = conditions[0]
            print(f"   Keys: {list(sample.keys())[:10]}...")  # Show first 10 keys
            if 'condition' in sample or 'diagnosis' in sample:
                key = 'condition' if 'condition' in sample else 'diagnosis'
                print(f"   {key}: {sample.get(key)}")
        
        # Test condition_reasons table
        print("\n3️⃣  Fetching condition_reasons table...")
        reasons = supabase.get_condition_reasons()
        print(f"✅ Fetched {len(reasons)} condition reasons")
        
        if reasons:
            print("\n📋 Sample reason record:")
            sample = reasons[0]
            print(f"   Keys: {list(sample.keys())}")
            if 'condition' in sample:
                print(f"   Condition: {sample.get('condition')}")
            if 'reason' in sample:
                reason_text = sample.get('reason', '')
                print(f"   Reason: {reason_text[:100]}..." if len(reason_text) > 100 else f"   Reason: {reason_text}")
        
        # Test action_conditions table
        print("\n4️⃣  Fetching action_conditions table...")
        actions = supabase.get_action_conditions()
        print(f"✅ Fetched {len(actions)} action conditions")
        
        if actions:
            print("\n📋 Sample action record:")
            sample = actions[0]
            print(f"   Keys: {list(sample.keys())}")
            if 'diagnosis' in sample or 'condition' in sample:
                key = 'diagnosis' if 'diagnosis' in sample else 'condition'
                print(f"   {key}: {sample.get(key)}")
            if 'medicine' in sample:
                print(f"   Medicine: {sample.get('medicine')}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Migration Summary:")
        print(f"   Conditions: {len(conditions)} records")
        print(f"   Reasons: {len(reasons)} records")
        print(f"   Actions: {len(actions)} records")
        print("=" * 60)
        
        if conditions and reasons and actions:
            print("✅ All tables successfully migrated to Supabase!")
            return True
        else:
            print("⚠️  Some tables are empty. Please ensure data is migrated.")
            return False
            
    except Exception as e:
        print(f"\n❌ Error testing Supabase tables: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_supabase_ai_tables()
    sys.exit(0 if success else 1)
