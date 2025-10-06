#!/usr/bin/env python3
"""
Debug the AI engine initialization
"""

import sys
import os
sys.path.append('.')

def debug_ai_engine():
    """Debug the AI engine setup"""
    
    print("🔍 DEBUGGING AI ENGINE INITIALIZATION")
    print("=" * 50)
    
    try:
        # Test 1: Import comprehensive AI
        print("\n1️⃣ Testing comprehensive AI import...")
        from comprehensive_ai_diagnosis import ComprehensiveAIDiagnosis
        print("✅ Successfully imported ComprehensiveAIDiagnosis")
        
        # Test 2: Initialize AI
        print("\n2️⃣ Testing AI initialization...")
        ai = ComprehensiveAIDiagnosis()
        print("✅ AI engine initialized")
        
        # Test 3: Check attributes
        print("\n3️⃣ Checking AI engine attributes...")
        print(f"   - Has model: {hasattr(ai, 'model')}")
        print(f"   - Has predict_comprehensive_diagnosis: {hasattr(ai, 'predict_comprehensive_diagnosis')}")
        print(f"   - Model version: {getattr(ai, 'model_version', 'Unknown')}")
        print(f"   - Symptom columns: {len(getattr(ai, 'symptom_columns', []))}")
        
        # Test 4: Test diagnosis
        print("\n4️⃣ Testing diagnosis...")
        result = ai.predict_comprehensive_diagnosis(
            "I have fever and cough",
            {'age_group': 'adult', 'gender': 'male', 'underlying_conditions': 'none'}
        )
        print(f"✅ Diagnosis successful: {result['primary_diagnosis']}")
        
        # Test 5: Check what the backend validation would see
        print("\n5️⃣ Backend validation check...")
        has_model = hasattr(ai, 'model')
        has_comprehensive = hasattr(ai, 'predict_comprehensive_diagnosis')
        print(f"   - Backend model check: {has_model}")
        print(f"   - Backend comprehensive check: {has_comprehensive}")
        print(f"   - Combined check: {has_model and has_comprehensive}")
        
        if not has_model or not has_comprehensive:
            print("❌ Backend validation would FAIL!")
            return False
        else:
            print("✅ Backend validation would PASS!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_ai_engine()