#!/usr/bin/env python3
"""
Test script to verify AI system with Supabase integration
"""

import sys
import os
from dotenv import load_dotenv

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_ai_system():
    """Test the AI diagnosis system with Supabase data"""
    print("=" * 60)
    print("🧪 Testing AI Diagnosis System with Supabase")
    print("=" * 60)
    
    try:
        # Import and initialize AI system
        print("\n1️⃣  Initializing AI system...")
        from app import StreamlinedAIDiagnosis
        
        ai_engine = StreamlinedAIDiagnosis()
        print(f"✅ AI system initialized: {ai_engine.model_version}")
        
        # Check data loading
        print(f"\n2️⃣  Data Loading Status:")
        print(f"   Conditions: {len(ai_engine.conditions_df)} records")
        print(f"   Reasons: {len(ai_engine.reasons_df)} records")
        print(f"   Actions: {len(ai_engine.actions_df)} records")
        print(f"   Symptom columns: {len(ai_engine.symptom_columns)} symptoms")
        
        # Test symptom parsing
        print(f"\n3️⃣  Testing symptom parsing...")
        test_symptoms = "fever, cough, headache, fatigue"
        parsed = ai_engine.parse_symptoms(test_symptoms)
        detected = [sym for sym, val in parsed.items() if val == 1]
        print(f"   Input: {test_symptoms}")
        print(f"   Detected: {detected}")
        
        # Test diagnosis
        print(f"\n4️⃣  Testing diagnosis...")
        result = ai_engine.diagnose(test_symptoms)
        
        if result['success']:
            print(f"   ✅ Diagnosis successful!")
            data = result['data']
            print(f"   Primary Condition: {data['primary_condition']}")
            print(f"   Confidence: {data['primary_confidence']}")
            print(f"   Detected Symptoms: {len(data['detected_symptoms'])} symptoms")
            
            print(f"\n   📋 Detailed Results:")
            for i, detail in enumerate(data['detailed_results'][:3], 1):
                print(f"   {i}. {detail['condition']} ({detail['confidence']})")
                print(f"      Reason: {detail['reason'][:80]}...")
                print(f"      Action: {detail['recommended_action'][:80]}...")
                print(f"      Medication: {detail['medication'][:60]}...")
        else:
            print(f"   ❌ Diagnosis failed: {result['message']}")
            return False
        
        # Test another set of symptoms
        print(f"\n5️⃣  Testing with different symptoms...")
        test_symptoms2 = "runny nose, sneezing, sore throat"
        result2 = ai_engine.diagnose(test_symptoms2)
        
        if result2['success']:
            print(f"   ✅ Diagnosis successful!")
            data2 = result2['data']
            print(f"   Primary Condition: {data2['primary_condition']}")
            print(f"   Confidence: {data2['primary_confidence']}")
        else:
            print(f"   ❌ Diagnosis failed: {result2['message']}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! AI system working with Supabase data")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing AI system: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_ai_system()
    sys.exit(0 if success else 1)
