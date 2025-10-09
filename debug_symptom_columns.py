import sys
sys.path.append('backend')
from app import EnhancedAIEngine

def debug_symptom_columns():
    ai_engine = EnhancedAIEngine()
    
    print("🔍 Debugging Symptom Columns")
    print("=" * 40)
    print(f"Total symptom columns: {len(ai_engine.symptom_columns)}")
    print(f"Symptom columns: {ai_engine.symptom_columns}")
    
    # Check if our test symptoms are in the columns
    test_symptoms = ['headache', 'dizziness', 'fever', 'cough', 'fatigue', 'sore_throat', 'body_aches']
    print("\nTest symptom presence:")
    for symptom in test_symptoms:
        present = symptom in ai_engine.symptom_columns
        print(f"  {symptom}: {'✅' if present else '❌'}")
    
    # Check a sample row
    if ai_engine.dataset:
        sample_row = ai_engine.dataset[0]
        print(f"\nSample row keys: {list(sample_row.keys())}")
        
        # Find rows with headache=1 and dizziness=1
        matching_rows = []
        for i, row in enumerate(ai_engine.dataset):
            if row.get('headache') == 1 and row.get('dizziness') == 1:
                matching_rows.append((i, row))
                if len(matching_rows) >= 3:
                    break
        
        print(f"\nFound {len(matching_rows)} rows with headache=1 and dizziness=1:")
        for i, (idx, row) in enumerate(matching_rows):
            print(f"  Row {idx}: diagnosis='{row['diagnosis']}'")
            active_symptoms = [col for col in ai_engine.symptom_columns if row.get(col) == 1]
            print(f"    Active symptoms: {active_symptoms}")

if __name__ == "__main__":
    debug_symptom_columns()