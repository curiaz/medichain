import requests
import json

def test_diagnosis_api():
    """Test the improved AI diagnosis system via API calls"""
    
    test_cases = [
        {
            'symptoms': 'I am experiencing sudden severe headache and dizziness for the last 6 hours.',
            'age': 'Adult (18 - 64 years)',
            'gender': 'Male',
            'expected': 'Migraine'
        },
        {
            'symptoms': 'I have had a fever and cough for 4 days, with body aches and sore throat. I feel very weak.',
            'age': 'Adult (18 - 64 years)', 
            'gender': 'Male',
            'expected': 'Flu'
        }
    ]

    print('🔍 Testing Enhanced AI Diagnosis System')
    print('=' * 50)

    for i, test in enumerate(test_cases, 1):
        print(f'\nTest Case {i}: {test["expected"]} Expected')
        print(f'Input: {test["symptoms"][:50]}...')
        
        try:
            response = requests.post('http://localhost:5000/api/ai/diagnose', 
                                   json={
                                       'symptoms': test['symptoms'],
                                       'age': test['age'],
                                       'gender': test['gender']
                                   },
                                   timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                diagnosis = result.get('diagnosis', 'Unknown')
                method = result.get('method', 'Unknown')
                confidence = result.get('confidence', 0)
                
                print(f'✅ Result: {diagnosis}')
                print(f'   Method: {method}')
                print(f'   Confidence: {confidence:.2f}')
                
                # Check if diagnosis matches expectation
                if test['expected'].lower() in diagnosis.lower():
                    print(f'   Status: ✅ CORRECT (Expected: {test["expected"]})')
                else:
                    print(f'   Status: ❌ INCORRECT (Expected: {test["expected"]}, Got: {diagnosis})')
            else:
                print(f'❌ API Error: {response.status_code} - {response.text}')
                
        except requests.exceptions.ConnectionError:
            print('❌ Connection Error: Backend server not running on localhost:5000')
        except Exception as e:
            print(f'❌ Error: {str(e)}')

    print('\n🎯 Live API Testing Complete!')

if __name__ == "__main__":
    test_diagnosis_api()