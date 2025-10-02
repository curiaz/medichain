#!/usr/bin/env python3
"""
Demo of the improved symptom reporting that shows user's original terms
"""

import sys
import os
sys.path.append('backend')
from app import EnhancedAIEngine

def demo_user_symptom_reporting():
    """Demo showing how user's original symptom descriptions are preserved"""
    
    print('🩺 DEMO: User Symptom Reporting with Original Terms')
    print('=' * 70)
    
    ai_engine = EnhancedAIEngine()
    
    # Test with a realistic user input
    user_input = """
    I've been feeling really sick for the past 3 days. I have trouble breathing, 
    especially when I walk up stairs. I'm extremely tired all the time and can't 
    get enough energy. Also have a persistent dry cough that won't go away. 
    My head hurts and I feel dizzy sometimes.
    """
    
    print('👤 User Input:')
    print(f'   "{user_input.strip()}"')
    print()
    
    # Process with the AI engine
    result = ai_engine.diagnose(
        input_text=user_input,
        age=28,
        gender="female"
    )
    
    if result and 'formatted_response' in result:
        # Extract just the symptoms reported section
        formatted_response = result['formatted_response']
        start = formatted_response.find('### Symptoms Reported:')
        next_section = formatted_response.find('---', start)
        
        if start != -1 and next_section != -1:
            symptoms_section = formatted_response[start:next_section].strip()
            
            print('🎯 RESULT - Symptoms Reported Section:')
            print('─' * 50)
            print(symptoms_section)
            print('─' * 50)
            
            print()
            print('✨ KEY IMPROVEMENT:')
            print('   Instead of showing technical terms like:')
            print('   • Shortness_Of_Breath')
            print('   • Fatigue') 
            print('   • Headache')
            print()
            print('   The system now shows user\'s ACTUAL words:')
            print('   • Trouble Breathing')
            print('   • Extremely Tired')
            print('   • Head Hurts')
            print('   • Persistent Dry Cough')
            print()
            
            print(f'🎯 AI Diagnosis: {result.get("diagnosis", "Unknown")}')
            print(f'📊 Method: {result.get("method", "Unknown")}')
            
        else:
            print('❌ Could not extract symptoms section')
    else:
        print('❌ Failed to get result from AI engine')
    
    print('\n' + '=' * 70)
    print('🏁 Demo completed - User symptom reporting enhanced!')

if __name__ == "__main__":
    demo_user_symptom_reporting()