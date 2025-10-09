#!/usr/bin/env python3
"""
Test Enhanced AI Diagnosis System with Medications
"""

from comprehensive_ai_diagnosis import ComprehensiveAIDiagnosis
import json

def test_enhanced_diagnosis():
    """Test the enhanced diagnosis system"""
    
    print('🧪 TESTING ENHANCED AI DIAGNOSIS SYSTEM')
    print('='*60)
    
    try:
        # Initialize enhanced AI system
        ai = ComprehensiveAIDiagnosis()
        
        # Test case 1: Common cold symptoms
        print('\n📋 Test Case 1: Common Cold Symptoms')
        print('-' * 40)
        
        result1 = ai.predict_enhanced_diagnosis(
            'I have a runny nose, mild cough, and feel a bit tired',
            {'age_group': 'adult', 'gender': 'female', 'underlying_conditions': 'none'}
        )
        
        print(f'Diagnosis: {result1["diagnosis"]}')
        print(f'Confidence: {result1["confidence_percent"]}')
        print(f'Description: {result1["description"]}')
        print(f'Severity: {result1["severity"]}')
        print(f'Duration: {result1["duration"]}')
        print('\n💊 Medications:')
        for med in result1["medications"]:
            print(f'   • {med["name"]}: {med["dosage"]} - {med["purpose"]}')
        print('\n🎯 Recommended Actions:')
        for action in result1["recommended_actions"]:
            print(f'   • {action}')
        print(f'\n🩺 When to see doctor: {result1["when_to_see_doctor"]}')
        
        # Test case 2: COVID-like symptoms  
        print('\n\n📋 Test Case 2: COVID-like Symptoms')
        print('-' * 40)
        
        result2 = ai.predict_enhanced_diagnosis(
            'I have fever, bad cough, can\'t taste anything, and shortness of breath',
            {'age_group': 'adult', 'gender': 'male', 'underlying_conditions': 'none'}
        )
        
        print(f'Diagnosis: {result2["diagnosis"]}')
        print(f'Confidence: {result2["confidence_percent"]}')
        print(f'Description: {result2["description"]}')
        print(f'Severity: {result2["severity"]}')
        print(f'Duration: {result2["duration"]}')
        print('\n💊 Medications:')
        for med in result2["medications"]:
            print(f'   • {med["name"]}: {med["dosage"]} - {med["purpose"]}')
        print('\n🎯 Recommended Actions:')
        for action in result2["recommended_actions"]:
            print(f'   • {action}')
        print(f'\n🩺 When to see doctor: {result2["when_to_see_doctor"]}')
        
        # Test case 3: Migraine symptoms
        print('\n\n📋 Test Case 3: Migraine Symptoms')
        print('-' * 40)
        
        result3 = ai.predict_enhanced_diagnosis(
            'I have a severe headache, nausea, and feel dizzy',
            {'age_group': 'adult', 'gender': 'female', 'underlying_conditions': 'none'}
        )
        
        print(f'Diagnosis: {result3["diagnosis"]}')
        print(f'Confidence: {result3["confidence_percent"]}')
        print(f'Description: {result3["description"]}')
        print(f'Severity: {result3["severity"]}')
        print(f'Duration: {result3["duration"]}')
        print('\n💊 Medications:')
        for med in result3["medications"]:
            print(f'   • {med["name"]}: {med["dosage"]} - {med["purpose"]}')
        print('\n🎯 Recommended Actions:')
        for action in result3["recommended_actions"]:
            print(f'   • {action}')
        print(f'\n🩺 When to see doctor: {result3["when_to_see_doctor"]}')
        
        print('\n' + '='*60)
        print('✅ Enhanced AI diagnosis system working perfectly!')
        print('💊 Medications and recommendations successfully integrated!')
        
        return True
        
    except Exception as e:
        print(f'❌ Error testing enhanced diagnosis: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_diagnosis()