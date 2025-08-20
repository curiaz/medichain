import pandas as pd
import pickle
import numpy as np

# Load the trained model
with open('diagnosis_model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('label_encoder.pkl', 'rb') as f:
    label_encoder = pickle.load(f)

with open('feature_names.pkl', 'rb') as f:
    feature_names = pickle.load(f)

def parse_symptoms(symptoms_text):
    """Parse symptoms text into binary features"""
    symptoms_text = symptoms_text.lower()
    
    parsed = {}
    for feature in feature_names:
        parsed[feature] = 0
    
    # Check for each symptom
    if 'fever' in symptoms_text:
        parsed['fever'] = 1
    if 'cough' in symptoms_text:
        parsed['cough'] = 1
    if 'headache' in symptoms_text:
        parsed['headache'] = 1
    if 'fatigue' in symptoms_text or 'tired' in symptoms_text:
        parsed['fatigue'] = 1
    if 'sore throat' in symptoms_text or 'throat' in symptoms_text:
        parsed['sore_throat'] = 1
    if 'shortness of breath' in symptoms_text or 'short of breath' in symptoms_text or 'breathing' in symptoms_text:
        parsed['shortness_of_breath'] = 1
    
    return parsed

def test_confidence(symptoms_text):
    """Test what confidence the model gives for specific symptoms"""
    print(f"\n=== Testing Confidence: '{symptoms_text}' ===")
    
    # Parse symptoms
    parsed_symptoms = parse_symptoms(symptoms_text)
    print(f"Parsed symptoms: {parsed_symptoms}")
    
    # Create input array
    input_data = []
    for feature in feature_names:
        input_data.append(parsed_symptoms.get(feature, 0))
    
    print(f"Input array: {input_data}")
    
    # Get prediction and probabilities
    prediction = model.predict([input_data])[0]
    probabilities = model.predict_proba([input_data])[0]
    
    # Get primary diagnosis and confidence
    primary_diagnosis = label_encoder.inverse_transform([prediction])[0]
    primary_confidence = float(probabilities[prediction])
    
    print(f"Primary Diagnosis: {primary_diagnosis}")
    print(f"Primary Confidence: {primary_confidence:.3f} ({primary_confidence*100:.1f}%)")
    
    # Show top 3 predictions
    top_indices = np.argsort(probabilities)[::-1][:3]
    print("\nTop 3 predictions:")
    for i, idx in enumerate(top_indices):
        condition = label_encoder.inverse_transform([idx])[0]
        confidence = probabilities[idx]
        print(f"  {i+1}. {condition}: {confidence:.3f} ({confidence*100:.1f}%)")

if __name__ == "__main__":
    test_cases = [
        "Fever",
        "Cough", 
        "Fever and cough",
        "Fever, headache, and fatigue"
    ]
    
    for case in test_cases:
        test_confidence(case)
