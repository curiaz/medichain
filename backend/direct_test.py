#!/usr/bin/env python3
"""
Direct test of the 3-diagnosis functionality
"""

import requests
import json
import time

def test_diagnosis_direct():
    """Test the diagnosis endpoint directly"""
    base_url = 'http://localhost:5000'
    
    print("🚀 Testing 3-Diagnosis Functionality")
    print("=" * 50)
    
    # Test cases with different symptoms
    test_cases = [
        {
            'name': 'Respiratory Symptoms',
            'data': {
                'description': 'cough, fever, shortness of breath, fatigue',
                'age': '35',
                'gender': 'male'
            }
        },
        {
            'name': 'Cardiac Symptoms',
            'data': {
                'description': 'chest pain, sweating, dizziness, nausea',
                'age': '45',
                'gender': 'male'
            }
        },
        {
            'name': 'Neurological Symptoms',
            'data': {
                'description': 'severe headache, nausea, sensitivity to light, neck stiffness',
                'age': '28',
                'gender': 'female'
            }
        },
        {
            'name': 'Digestive Symptoms',
            'data': {
                'description': 'abdominal pain, diarrhea, vomiting, dehydration',
                'age': '22',
                'gender': 'female'
            }
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"Symptoms: {test_case['data']['description']}")
        print(f"Age: {test_case['data']['age']}, Gender: {test_case['data']['gender']}")
        
        try:
            # Make diagnosis request
            response = requests.post(
                f"{base_url}/api/ai/diagnose",
                json=test_case['data'],
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if we have a diagnosis (the API is working)
                if result.get('diagnosis') and result.get('formatted_response'):
                    # Check for 3 diagnoses in the formatted response
                    formatted_text = result.get('formatted_response', '')
                    diagnosis_count = formatted_text.count('**') // 2  # Count diagnosis pairs
                    
                    print(f"✅ Status: SUCCESS")
                    print(f"📊 Diagnoses found: {diagnosis_count}")
                    print(f"🔬 Primary: {result.get('diagnosis', 'N/A')}")
                    print(f"📈 Method: {result.get('method', 'N/A')}")
                    print(f"🎯 Severity: {result.get('severity_level', 'N/A')}")
                    
                    # Check alternatives
                    alternatives = result.get('alternative_diagnoses', [])
                    print(f"🔄 Alternatives: {len(alternatives)}")
                    
                    if diagnosis_count >= 3:
                        print(f"🎉 SUCCESS: Found {diagnosis_count} diagnoses!")
                        success_count += 1
                    else:
                        print(f"⚠️  WARNING: Only {diagnosis_count} diagnoses found (expected 3)")
                    
                    # Show some of the formatted response
                    preview = formatted_text[:300] + "..." if len(formatted_text) > 300 else formatted_text
                    print(f"📋 Preview: {preview}")
                    
                else:
                    print(f"❌ FAILED: Invalid response structure")
                    print(f"📥 Response keys: {list(result.keys())}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error: {error_data}")
                except:
                    print(f"Error: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
        
        # Small delay between tests
        time.sleep(1)
    
    print(f"\n🏁 Test Summary")
    print("=" * 50)
    print(f"✅ Successful tests: {success_count}/{len(test_cases)}")
    
    if success_count == len(test_cases):
        print("🎉 ALL TESTS PASSED! 3-diagnosis system is working correctly.")
    elif success_count > 0:
        print(f"⚠️  PARTIAL SUCCESS: {success_count} out of {len(test_cases)} tests passed.")
    else:
        print("❌ ALL TESTS FAILED. Please check the system.")

if __name__ == "__main__":
    test_diagnosis_direct()