#!/usr/bin/env python3
"""
Simple API server for testing NLP-based diagnosis
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import re
from typing import Dict, List, Any

app = Flask(__name__)
CORS(app)

class SimpleNLPDiagnosis:
    def __init__(self):
        """Initialize with condition patterns based on dataset analysis"""
        self.condition_patterns = {
            'migraine': [
                'headache', 'head pain', 'severe headache', 'throbbing', 
                'sensitivity to light', 'photophobia', 'nausea', 'vomiting',
                'aura', 'visual disturbances'
            ],
            'tension headache': [
                'headache', 'head pain', 'tight band', 'pressure', 
                'stress', 'tension', 'neck pain', 'shoulder pain'
            ],
            'pneumonia': [
                'cough', 'fever', 'shortness of breath', 'difficulty breathing',
                'chest pain', 'phlegm', 'sputum', 'chills', 'fatigue'
            ],
            'bronchitis': [
                'cough', 'persistent cough', 'phlegm', 'sputum', 'chest discomfort',
                'wheezing', 'shortness of breath', 'fatigue'
            ],
            'anxiety disorder': [
                'anxiety', 'anxious', 'worry', 'restless', 'restlessness',
                'panic', 'nervousness', 'trouble sleeping', 'insomnia',
                'racing heart', 'palpitations'
            ],
            'depression': [
                'sad', 'sadness', 'depressed', 'hopeless', 'worthless',
                'loss of interest', 'fatigue', 'sleep problems', 'appetite changes'
            ],
            'common cold': [
                'runny nose', 'stuffy nose', 'sneezing', 'sore throat',
                'mild cough', 'congestion', 'nasal discharge'
            ],
            'flu': [
                'fever', 'body aches', 'muscle aches', 'fatigue', 'chills',
                'headache', 'cough', 'sore throat', 'weakness'
            ],
            'diabetes': [
                'excessive thirst', 'frequent urination', 'hunger',
                'weight loss', 'blurred vision', 'fatigue', 'slow healing'
            ],
            'hypertension': [
                'high blood pressure', 'headache', 'dizziness', 'chest pain',
                'shortness of breath', 'nosebleeds'
            ],
            'asthma': [
                'wheezing', 'shortness of breath', 'coughing', 'chest tightness',
                'difficulty breathing', 'breathless'
            ],
            'gastritis': [
                'stomach pain', 'nausea', 'vomiting', 'bloating', 'loss of appetite',
                'heartburn', 'indigestion'
            ]
        }
    
    def extract_conditions_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extract matching conditions and keywords from input text"""
        text_lower = text.lower()
        matches = {}
        
        for condition, keywords in self.condition_patterns.items():
            matched_keywords = []
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    matched_keywords.append(keyword)
            
            if matched_keywords:
                matches[condition] = matched_keywords
        
        return matches
    
    def predict_nlp_diagnosis(self, symptoms_text: str, patient_conditions: List[str] = None) -> Dict[str, Any]:
        """
        Predict diagnosis using NLP keyword matching
        """
        try:
            # Extract conditions from text
            condition_matches = self.extract_conditions_from_text(symptoms_text)
            
            if not condition_matches:
                return {
                    'diagnosis': 'Unable to determine',
                    'reasoning': 'No matching conditions found based on the provided symptoms.',
                    'matched_keywords': [],
                    'alternative_conditions': [],
                    'description': 'Please consult with a healthcare professional for proper evaluation.',
                    'detected_symptoms': {}
                }
            
            # Sort by number of matched keywords
            sorted_conditions = sorted(
                condition_matches.items(), 
                key=lambda x: len(x[1]), 
                reverse=True
            )
            
            primary_condition = sorted_conditions[0]
            primary_diagnosis = primary_condition[0]
            primary_keywords = primary_condition[1]
            
            # Create alternative conditions list
            alternative_conditions = []
            for condition, keywords in sorted_conditions[1:4]:  # Top 3 alternatives
                alternative_conditions.append({
                    'condition': condition.title(),
                    'matched_keywords': keywords
                })
            
            # Generate reasoning
            reasoning = f"Based on reported symptoms matching {len(primary_keywords)} key indicators for {primary_diagnosis}"
            
            # Create detected symptoms dict (for compatibility with existing frontend)
            detected_symptoms = {}
            for keyword in primary_keywords:
                detected_symptoms[keyword.replace(' ', '_')] = 1
            
            return {
                'diagnosis': primary_diagnosis.title(),
                'reasoning': reasoning,
                'matched_keywords': primary_keywords,
                'alternative_conditions': alternative_conditions,
                'description': f"The symptoms align with patterns commonly associated with {primary_diagnosis}. Please consult a healthcare professional for proper diagnosis and treatment.",
                'extracted_conditions': list(condition_matches.keys()),
                'detected_symptoms': detected_symptoms
            }
            
        except Exception as e:
            return {
                'diagnosis': 'Analysis Error',
                'reasoning': f'Error during analysis: {str(e)}',
                'matched_keywords': [],
                'alternative_conditions': [],
                'description': 'Please try again or consult with a healthcare professional.',
                'detected_symptoms': {}
            }

# Initialize the diagnosis engine
diagnosis_engine = SimpleNLPDiagnosis()

@app.route('/api/ai/diagnose', methods=['POST'])
def ai_diagnose():
    """API endpoint for AI diagnosis"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        symptoms = data.get('symptoms', '')
        patient_age = data.get('patient_age', '')
        patient_gender = data.get('patient_gender', '')
        
        if not symptoms:
            return jsonify({'error': 'Symptoms are required'}), 400
        
        # Get diagnosis using NLP
        result = diagnosis_engine.predict_nlp_diagnosis(symptoms)
        
        # Add patient info to result
        result['patient_age'] = patient_age
        result['patient_gender'] = patient_gender
        
        return jsonify({
            'success': True,
            'diagnosis': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Simple NLP Diagnosis API is running'})

if __name__ == '__main__':
    print("Starting Simple NLP Diagnosis API on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)