#!/usr/bin/env python3
import sys
import os
sys.path.append('./backend')

# Import the AI engine
from app import EnhancedAIEngine

# Test the diagnosis system directly
engine = EnhancedAIEngine()

print("=== Testing CSV Data Usage ===")
print(f"Dataset loaded: {len(engine.dataset)} records")
print(f"Available diagnoses: {len(engine.diagnoses)}")
print()

# Test description retrieval
test_conditions = ['Migraine', 'Flu', 'Food Poisoning', 'Tonsillitis']

for condition in test_conditions:
    print(f"Testing condition: {condition}")
    print("-" * 40)
    
    # Check if condition exists in CSV
    csv_matches = [row for row in engine.dataset if row.get('diagnosis', '').strip() == condition]
    print(f"CSV records found: {len(csv_matches)}")
    
    if csv_matches:
        sample = csv_matches[0]
        csv_desc = sample.get('diagnosis_description', '').strip()
        csv_action = sample.get('recommended_action', '').strip()
        print(f"CSV Description: {csv_desc[:100]}..." if len(csv_desc) > 100 else f"CSV Description: {csv_desc}")
        print(f"CSV Action: {csv_action[:100]}..." if len(csv_action) > 100 else f"CSV Action: {csv_action}")
    
    # Get the description the system would use
    system_desc = engine.get_condition_description(condition)
    print(f"System Description: {system_desc[:100]}..." if len(system_desc) > 100 else f"System Description: {system_desc}")
    
    print()

print("=== Testing Diagnosis Process ===")
# Test actual diagnosis
test_input = "I have severe headache and dizziness for 2 days"
result = engine.diagnose(test_input)

print(f"Input: {test_input}")
print(f"Diagnosis: {result.get('diagnosis')}")
print(f"Confidence: {result.get('confidence')}")
print(f"Method: {result.get('method')}")
print()

# Check if it's using CSV descriptions in output
if 'possible_conditions' in result:
    print("Possible conditions with descriptions:")
    for i, condition in enumerate(result['possible_conditions'][:3], 1):
        print(f"{i}. {condition.get('name')}")
        desc = condition.get('description', '')
        print(f"   Description: {desc[:150]}..." if len(desc) > 150 else f"   Description: {desc}")
        print()