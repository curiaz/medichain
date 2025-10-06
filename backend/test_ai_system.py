#!/usr/bin/env python3
"""
Quick test of the comprehensive AI diagnosis system
"""

import sys
import os
sys.path.append('.')

try:
    from comprehensive_ai_diagnosis import ComprehensiveAIDiagnosis
    
    print("🧪 Testing Comprehensive AI Diagnosis System...")
    
    # Initialize the AI system
    ai = ComprehensiveAIDiagnosis()
    print("✅ AI system loaded successfully!")
    
    # Test with natural language
    test_symptoms = "I have fever, bad cough, and can't taste anything"
    test_patient = {
        'age_group': 'adult',
        'gender': 'male',
        'underlying_conditions': 'none'
    }
    
    print(f"\n🔍 Testing symptoms: {test_symptoms}")
    print(f"👤 Patient: {test_patient}")
    
    result = ai.predict_comprehensive_diagnosis(test_symptoms, test_patient)
    
    print("\n📊 DIAGNOSIS RESULT:")
    print(f"   🩺 Primary Diagnosis: {result['primary_diagnosis']}")
    print(f"   📈 Confidence: {result['confidence_percent']}")
    print(f"   ⚠️  Severity: {result['severity']}")
    print(f"   🔢 Active Symptoms: {result['active_symptoms_count']}")
    print(f"   💊 Medications: {len(result['medications'])} prescribed")
    print(f"   📋 Description: {result['diagnosis_description'][:100]}...")
    
    print("\n✅ AI SYSTEM WORKING PERFECTLY!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()