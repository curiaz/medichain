#!/usr/bin/env python3
"""
Test Enhanced API Endpoint
"""

import requests
import json

def test_enhanced_api():
    """Test the enhanced diagnosis API endpoint"""
    
    print('🧪 TESTING ENHANCED AI API ENDPOINT')
    print('='*50)
    
    # API endpoint
    url = 'http://localhost:5000/api/ai/diagnose'
    
    # Test case 1: Migraine symptoms
    test_data = {
        'symptoms': 'I have a severe headache, nausea, and feel dizzy',
        'age': 30,
        'gender': 'female'
    }
    
    try:
        print('📡 Sending request to API...')
        response = requests.post(url, json=test_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print('✅ API Response received successfully!')
            print(f'📋 Diagnosis: {result.get("diagnosis", "N/A")}')
            print(f'📊 Confidence: {result.get("confidence_percent", "N/A")}')
            
            # Check if enhanced features are present
            if 'medications' in result:
                print(f'💊 Medications: {len(result["medications"])} options')
                for med in result['medications'][:2]:  # Show first 2
                    print(f'   • {med.get("name", "N/A")}: {med.get("purpose", "N/A")}')
            
            if 'recommended_actions' in result:
                print(f'🎯 Actions: {len(result["recommended_actions"])} recommendations')
                for action in result['recommended_actions'][:2]:  # Show first 2
                    print(f'   • {action}')
            
            if 'when_to_see_doctor' in result:
                print(f'🩺 Doctor guidance: {result["when_to_see_doctor"][:60]}...')
                
            print('\n✅ Enhanced API working correctly!')
            
        else:
            print(f'❌ API Error: {response.status_code}')
            print(f'Response: {response.text}')
            
    except requests.exceptions.ConnectionError:
        print('❌ Cannot connect to API. Is the server running?')
    except Exception as e:
        print(f'❌ Error: {e}')

if __name__ == '__main__':
    test_enhanced_api()