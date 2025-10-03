import sys
sys.path.append('backend')
from app import EnhancedAIEngine

def test_csv_confidence():
    ai_engine = EnhancedAIEngine()
    result = ai_engine.csv_diagnose(['headache', 'dizziness'], 'adult', 'male')
    print('CSV result with confidence scaling:')
    print(f'Diagnosis: {result["diagnosis"]}')
    print(f'Confidence: {result["confidence"]}')
    print(f'Raw result: {result}')

if __name__ == "__main__":
    test_csv_confidence()