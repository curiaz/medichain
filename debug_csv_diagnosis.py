import sys
sys.path.append('backend')
from app import EnhancedAIEngine

def debug_csv_diagnosis():
    ai_engine = EnhancedAIEngine()
    
    print("🔍 Debugging CSV Diagnosis Logic")
    print("=" * 45)
    
    # Test case 1: headache + dizziness should → Migraine
    print("Test 1: Headache + Dizziness")
    symptoms1 = ['headache', 'dizziness']
    csv_result1 = ai_engine.csv_diagnose(symptoms1, 'adult', 'male')
    print(f"Input symptoms: {symptoms1}")
    print(f"CSV result: {csv_result1}")
    
    # Check what records match these symptoms
    print("\nManual verification:")
    scores = []
    for row in ai_engine.dataset:
        user_symptoms = set(symptoms1)
        row_symptoms = set([col for col in ai_engine.symptom_columns if row.get(col) == 1])
        
        if len(user_symptoms) > 0 and len(row_symptoms) > 0:
            intersection = len(user_symptoms.intersection(row_symptoms))
            union = len(user_symptoms.union(row_symptoms))
            similarity = intersection / union
            
            if similarity > 0:  # Only show matches
                scores.append({
                    'diagnosis': row['diagnosis'],
                    'similarity': similarity,
                    'row_symptoms': list(row_symptoms),
                    'intersection': list(user_symptoms.intersection(row_symptoms))
                })
    
    # Sort by similarity
    scores.sort(key=lambda x: x['similarity'], reverse=True)
    
    print("Top 5 matches:")
    for i, score in enumerate(scores[:5]):
        print(f"  {i+1}. {score['diagnosis']} (similarity: {score['similarity']:.3f})")
        print(f"     Common symptoms: {score['intersection']}")
        print(f"     All symptoms in record: {score['row_symptoms'][:8]}")
    
    print()
    print("=" * 45)
    
    # Test case 2: fever + cough + fatigue + sore_throat + body_aches should → Flu
    print("Test 2: Fever + Cough + Fatigue + Sore Throat + Body Aches")
    symptoms2 = ['fever', 'cough', 'fatigue', 'sore_throat', 'body_aches']
    csv_result2 = ai_engine.csv_diagnose(symptoms2, 'adult', 'male')
    print(f"Input symptoms: {symptoms2}")
    print(f"CSV result: {csv_result2}")

if __name__ == "__main__":
    debug_csv_diagnosis()