import sys
sys.path.append('backend')
from app import EnhancedAIEngine

def debug_csv_matching():
    ai_engine = EnhancedAIEngine()
    
    print("🔍 Debugging CSV Symptom Matching")
    print("=" * 50)
    
    symptoms = ['headache', 'dizziness']
    user_symptoms = set(symptoms)
    
    print(f"Looking for: {symptoms}")
    print(f"User symptoms set: {user_symptoms}")
    
    # Manually check what the CSV matching logic finds
    scores = []
    
    for i, row in enumerate(ai_engine.dataset[:50]):  # Check first 50 rows
        row_symptoms = set([col for col in ai_engine.symptom_columns if row.get(col) == '1'])
        
        if len(user_symptoms) > 0 and len(row_symptoms) > 0:
            intersection = len(user_symptoms.intersection(row_symptoms))
            union = len(user_symptoms.union(row_symptoms))
            similarity = intersection / union
            
            if similarity > 0.3:  # Only show decent matches
                scores.append({
                    'row_id': i,
                    'diagnosis': row['diagnosis'],
                    'similarity': similarity,
                    'row_symptoms': list(row_symptoms),
                    'intersection': list(user_symptoms.intersection(row_symptoms)),
                    'union_size': union,
                    'intersection_size': intersection
                })
    
    # Sort by similarity
    scores.sort(key=lambda x: x['similarity'], reverse=True)
    
    print(f"\nTop matches (similarity > 0.3):")
    for i, score in enumerate(scores[:10]):
        print(f"  {i+1}. {score['diagnosis']} (similarity: {score['similarity']:.3f})")
        print(f"     Row symptoms: {score['row_symptoms']}")
        print(f"     Common symptoms: {score['intersection']}")
        print(f"     Union size: {score['union_size']}, Intersection size: {score['intersection_size']}")
        print()
    
    if not scores:
        print("❌ No matches found! Checking if symptom columns are correct...")
        print(f"Available symptom columns: {ai_engine.symptom_columns}")
        print("Checking if our test symptoms are in the columns:")
        for sym in symptoms:
            print(f"  {sym}: {'✅' if sym in ai_engine.symptom_columns else '❌'}")

if __name__ == "__main__":
    debug_csv_matching()