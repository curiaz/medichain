import sys
sys.path.append('backend')
from app import EnhancedAIEngine

def test_symptom_accuracy():
    ai_engine = EnhancedAIEngine()
    
    # Test cases from screenshots
    test_cases = [
        {
            'input': "I'm experiencing sudden severe headache, blurred vision, and dizziness for the last 6 hours.",
            'expected_symptoms': ['headache', 'dizziness'],
            'description': 'Case 1: Headache + dizziness'
        },
        {
            'input': "I've had a fever and cough for 4 days, with body aches and sore throat. I feel very weak.",
            'expected_symptoms': ['fever', 'cough', 'body_aches', 'sore_throat', 'fatigue'],
            'description': 'Case 2: Fever + respiratory symptoms'
        }
    ]
    
    print("🔍 Testing AI Diagnosis Accuracy")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{test_case['description']}")
        print(f"Input: {test_case['input']}")
        print("-" * 40)
        
        # Extract symptoms
        symptom_data = ai_engine.advanced_symptom_extraction(test_case['input'])
        extracted_symptoms = symptom_data['symptoms']
        
        print(f"Expected symptoms: {test_case['expected_symptoms']}")
        print(f"Extracted symptoms: {extracted_symptoms}")
        
        # Check accuracy
        matched = len(set(extracted_symptoms) & set(test_case['expected_symptoms']))
        total_expected = len(test_case['expected_symptoms'])
        accuracy = (matched / total_expected) * 100 if total_expected > 0 else 0
        
        print(f"Symptom extraction accuracy: {accuracy:.1f}% ({matched}/{total_expected})")
        
        # Get full diagnosis
        result = ai_engine.diagnose(test_case['input'], age='Adult (18 - 64 years)', gender='Male')
        
        print(f"Final diagnosis: {result.get('diagnosis')}")
        print(f"Confidence: {result.get('confidence', 0):.2f}")
        print(f"Method used: {result.get('method', 'Unknown')}")
        
        # Check if diagnosis seems reasonable
        diagnosis = result.get('diagnosis', '').lower()
        input_text = test_case['input'].lower()
        
        print("\n🔍 Diagnosis Analysis:")
        if i == 1:  # Headache case
            if any(word in diagnosis for word in ['headache', 'migraine', 'hypertension', 'tension']):
                print("✅ Diagnosis appears relevant to symptoms")
            else:
                print("❌ Diagnosis may not match reported symptoms")
        elif i == 2:  # Fever case  
            if any(word in diagnosis for word in ['flu', 'cold', 'respiratory', 'infection', 'fever']):
                print("✅ Diagnosis appears relevant to symptoms")
            else:
                print("❌ Diagnosis may not match reported symptoms")

if __name__ == "__main__":
    test_symptom_accuracy()