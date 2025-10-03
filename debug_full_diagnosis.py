import sys
sys.path.append('backend')
from app import EnhancedAIEngine

def debug_full_diagnosis():
    ai_engine = EnhancedAIEngine()
    
    print("🔍 Full Diagnosis Debug")
    print("=" * 50)
    
    # Test case 1: headache + dizziness should → Migraine
    print("Test 1: Headache + Dizziness")
    symptoms1 = ['headache', 'dizziness']
    
    print(f"Input symptoms: {symptoms1}")
    
    # Test CSV directly
    csv_result = ai_engine.csv_diagnose(symptoms1, 'adult', 'male')
    print(f"CSV result: {csv_result}")
    
    # Test ML directly
    ml_result = None
    try:
        ml_result = ai_engine.ml_predict(symptoms1, 'adult', 'male')
        print(f"ML result: {ml_result}")
    except Exception as e:
        print(f"ML error: {e}")
    
    # Test combined
    combined = ai_engine.combine_predictions(ml_result, csv_result, symptoms1, 'adult', 'male', ['Headache', 'Dizziness'])
    print(f"Combined result: {combined}")
    
    print()
    print("=" * 50)
    
    # Test case 2: fever + cough + fatigue + sore_throat + body_aches should → Flu
    print("Test 2: Fever + Cough + Fatigue + Sore Throat + Body Aches")
    symptoms2 = ['fever', 'cough', 'fatigue', 'sore_throat', 'body_aches']
    
    print(f"Input symptoms: {symptoms2}")
    
    # Test CSV directly
    csv_result2 = ai_engine.csv_diagnose(symptoms2, 'adult', 'male')
    print(f"CSV result: {csv_result2}")
    
    # Test ML directly
    ml_result2 = None
    try:
        ml_result2 = ai_engine.ml_predict(symptoms2, 'adult', 'male')
        print(f"ML result: {ml_result2}")
    except Exception as e:
        print(f"ML error: {e}")
    
    # Test combined
    combined2 = ai_engine.combine_predictions(ml_result2, csv_result2, symptoms2, 'adult', 'male', ['Fever', 'Cough', 'Weak', 'Sore Throat', 'Body Aches'])
    print(f"Combined result: {combined2}")

if __name__ == "__main__":
    debug_full_diagnosis()