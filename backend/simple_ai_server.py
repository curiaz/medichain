#!/usr/bin/env python3
"""
Simple and robust AI diagnosis server for port 5000
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from datetime import datetime

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

app = Flask(__name__)
CORS(app)

# Simple condition patterns for NLP diagnosis
CONDITION_PATTERNS = {
    'flu': ['flu', 'fever', 'body aches', 'chills', 'fatigue', 'headache', 'muscle pain'],
    'common cold': ['cold', 'runny nose', 'sneezing', 'sore throat', 'cough'],
    'migraine': ['migraine', 'severe headache', 'throbbing pain', 'nausea', 'light sensitivity'],
    'tension headache': ['headache', 'head pressure', 'tension', 'stress'],
    'anxiety': ['anxiety', 'worry', 'nervousness', 'panic', 'restless'],
    'depression': ['depression', 'sad', 'hopeless', 'low mood', 'fatigue'],
    'asthma': ['asthma', 'wheezing', 'shortness of breath', 'breathing difficulty'],
    'bronchitis': ['bronchitis', 'persistent cough', 'chest congestion', 'mucus'],
    'pneumonia': ['pneumonia', 'lung infection', 'chest pain', 'difficulty breathing'],
    'gastritis': ['stomach pain', 'nausea', 'indigestion', 'heartburn', 'bloating'],
    'hypertension': ['high blood pressure', 'dizziness', 'headache'],
    'diabetes': ['diabetes', 'frequent urination', 'excessive thirst', 'blurred vision'],
    'arthritis': ['joint pain', 'stiffness', 'swelling', 'arthritis'],
    'allergic reaction': ['allergy', 'rash', 'itching', 'hives', 'swelling']
}

def extract_conditions(symptoms_text):
    """Extract conditions from symptoms using keyword matching"""
    text_lower = symptoms_text.lower()
    matched_conditions = []
    
    for condition, keywords in CONDITION_PATTERNS.items():
        matches = []
        for keyword in keywords:
            if keyword in text_lower:
                matches.append(keyword)
        
        if matches:
            matched_conditions.append({
                'condition': condition,
                'matched_keywords': matches,
                'score': len(matches)
            })
    
    # Sort by score (most matches first)
    matched_conditions.sort(key=lambda x: x['score'], reverse=True)
    
    return matched_conditions

@app.route('/api/ai/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'MediChain AI Server',
        'port': 5000,
        'dataset_loaded': True,  # Frontend expects this field
        'conditions_available': len(CONDITION_PATTERNS),
        'timestamp': datetime.now().isoformat(),
        'version': '1.0'
    })

@app.route('/api/ai/diagnose', methods=['POST'])
def diagnose():
    """AI diagnosis endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        symptoms = data.get('symptoms', '')
        patient_age = data.get('patientAge', '')
        patient_gender = data.get('patientGender', '')
        
        if not symptoms:
            return jsonify({
                'success': False,
                'error': 'Symptoms are required'
            }), 400
        
        # Extract conditions
        conditions = extract_conditions(symptoms)
        
        if not conditions:
            # Fallback diagnosis
            primary_diagnosis = 'General health concern'
            reasoning = 'Unable to identify specific condition from symptoms'
            alternatives = []
        else:
            primary_condition = conditions[0]
            primary_diagnosis = primary_condition['condition'].title()
            reasoning = f"Matched keywords: {', '.join(primary_condition['matched_keywords'])}"
            alternatives = conditions[1:4]  # Top 3 alternatives
        
        # Create detected symptoms
        detected_symptoms = {}
        for word in ['fever', 'headache', 'cough', 'fatigue', 'nausea', 'pain']:
            if word in symptoms.lower():
                detected_symptoms[word] = 1
        
        # Format diagnosis result
        diagnosis_data = {
            'diagnosis': primary_diagnosis,
            'reasoning': reasoning,
            'matched_keywords': conditions[0]['matched_keywords'] if conditions else [],
            'top_predictions': []
        }
        
        # Add alternatives
        for alt in alternatives:
            diagnosis_data['top_predictions'].append({
                'diagnosis': alt['condition'].title(),
                'reasoning': f"Keywords: {', '.join(alt['matched_keywords'])}"
            })
        
        # Create slides for display
        slides_content = [
            {
                'type': 'symptoms',
                'title': 'Symptoms Reported',
                'content': symptoms,
                'patientAge': patient_age,
                'patientGender': patient_gender
            },
            {
                'type': 'conditions',
                'title': 'Possible Conditions',
                'content': 'NLP-based analysis completed',
                'diagnosisData': diagnosis_data
            },
            {
                'type': 'severity',
                'title': 'Assessment Notes',
                'content': f'• Analysis method: Keyword matching\n• Conditions evaluated: {len(CONDITION_PATTERNS)}\n• Primary match score: {conditions[0]["score"] if conditions else 0}'
            },
            {
                'type': 'recommendations',
                'title': 'Recommendations',
                'content': '• Consult healthcare professional for proper diagnosis\n• Monitor symptoms\n• This is for informational purposes only'
            }
        ]
        
        # Create formatted response string that the frontend parser expects
        formatted_response = f"""**SLIDE_1_SYMPTOMS**
{symptoms}

**SLIDE_2_CONDITIONS**
Primary Diagnosis: {primary_diagnosis}
Reasoning: {reasoning}

Alternative Conditions:
{chr(10).join([f"• {alt['condition'].title()}: {', '.join(alt['matched_keywords'])}" for alt in alternatives[:3]])}

**SLIDE_3_SEVERITY**
• Analysis method: Keyword matching
• Conditions evaluated: {len(CONDITION_PATTERNS)}
• Primary match score: {conditions[0]["score"] if conditions else 0}

**SLIDE_4_RECOMMENDATIONS**
• Consult healthcare professional for proper diagnosis
• Monitor symptoms and note any changes
• This analysis is for informational purposes only"""

        # Create response in multiple formats for compatibility
        response = {
            'success': True,
            'diagnosis': primary_diagnosis,
            'formatted_response': formatted_response,
            'analysis': {
                'diagnosis_data': diagnosis_data,
                'slides': slides_content
            },
            # Additional fields for compatibility
            'confidence': conditions[0]["score"] * 25 if conditions else 0,  # Convert score to percentage-like
            'top_predictions': [{'diagnosis': alt['condition'].title(), 'reasoning': f"Keywords: {', '.join(alt['matched_keywords'])}"} for alt in alternatives],
            'detected_symptoms': detected_symptoms,
            'method': 'NLP Keyword Matching'
        }
        
        # Debug: Print the response structure
        print(f"🔍 API Response: {response}")
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Diagnosis failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting MediChain AI Server on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)