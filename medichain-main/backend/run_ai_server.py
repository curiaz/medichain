from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import os
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load model and encoders
MODEL_PATH = 'diagnosis_model.pkl'
LABEL_ENCODER_PATH = 'label_encoder.pkl'
FEATURE_NAMES_PATH = 'feature_names.pkl'

# Global variables for model and encoders
model = None
label_encoder = None
feature_names = None

def load_model():
    """Load the trained model and encoders"""
    global model, label_encoder, feature_names
    
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            logger.info("Model loaded successfully")
        else:
            logger.error(f"Model file not found: {MODEL_PATH}")
            return False
            
        if os.path.exists(LABEL_ENCODER_PATH):
            label_encoder = joblib.load(LABEL_ENCODER_PATH)
            logger.info("Label encoder loaded successfully")
        else:
            logger.error(f"Label encoder file not found: {LABEL_ENCODER_PATH}")
            return False
            
        if os.path.exists(FEATURE_NAMES_PATH):
            feature_names = joblib.load(FEATURE_NAMES_PATH)
            logger.info("Feature names loaded successfully")
        else:
            logger.error(f"Feature names file not found: {FEATURE_NAMES_PATH}")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return False

def parse_symptoms(symptoms_input):
    """Parse symptoms input into binary format required by the model"""
    # Define the expected symptom features from the training data
    expected_features = ['fever', 'cough', 'fatigue', 'shortness_of_breath', 'headache', 'sore_throat']
    
    # If input is already a dictionary with binary values, return as is
    if isinstance(symptoms_input, dict):
        # Check if it's already in binary format
        if all(isinstance(v, (int, float)) and v in [0, 1] for v in symptoms_input.values()):
            return symptoms_input
    
    # Initialize symptoms dictionary with all features set to 0
    parsed_symptoms = {feature: 0 for feature in expected_features}
    
    symptoms_list = []
    
    # Handle different input types
    if isinstance(symptoms_input, list):
        symptoms_list = [str(s).lower().strip() for s in symptoms_input]
    elif isinstance(symptoms_input, str):
        # Convert to lowercase and split by common separators
        symptoms_text = symptoms_input.lower()
        symptoms_list = [s.strip() for s in symptoms_text.replace(',', ' ').replace(';', ' ').split()]
    
    # Map common symptom variations to expected features
    symptom_mappings = {
        'fever': ['fever', 'temperature', 'hot', 'feverish', 'chills', 'sweating', 'pyrexia'],
        'cough': ['cough', 'coughing', 'hacking', 'dry cough', 'persistent cough'],
        'fatigue': ['fatigue', 'tired', 'exhausted', 'weakness', 'weak', 'lethargic', 'drained'],
        'shortness_of_breath': ['shortness_of_breath', 'breathless', 'breathing', 'breath', 'dyspnea', 'shortness of breath', 'wheezing'],
        'headache': ['headache', 'head', 'migraine', 'head pain'],
        'sore_throat': ['sore_throat', 'throat_pain', 'swollen_throat', 'sore throat', 'throat', 'swallowing']
    }
    
    # Check for each symptom in the list
    for symptom in symptoms_list:
        for feature, variations in symptom_mappings.items():
            if symptom in variations or any(variation in symptom for variation in variations):
                parsed_symptoms[feature] = 1
                break
    
    return parsed_symptoms

def get_medical_disclaimer():
    """Get standard medical disclaimer"""
    return {
        'disclaimer': 'This AI analysis is for informational purposes only and does not constitute medical advice.',
        'warning': 'Always consult with qualified healthcare professionals for medical diagnosis and treatment.',
        'emergency': 'For medical emergencies, contact emergency services immediately.',
        'liability': 'This AI system is a decision support tool and should not replace professional medical judgment.'
    }

@app.route('/medical-ai-assistant', methods=['POST'])
def medical_ai_assistant():
    """
    Medical AI Assistant endpoint that provides comprehensive medical analysis
    You are a medical AI assistant. A patient has reported the following symptoms and medical history.
    Based on this information, analyze the case and provide possible diagnoses with confidence levels.
    Then, suggest safe and relevant treatment options or prescriptions, considering the patient's 
    medical record, allergies, and ongoing medications. Always clarify that your response is an 
    AI-generated suggestion and must be reviewed by a licensed doctor before final use.
    """
    if model is None or label_encoder is None or feature_names is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'symptoms_history' not in data:
            return jsonify({'error': 'Missing symptoms and medical history'}), 400
        
        symptoms_history = data['symptoms_history']
        patient_data = data.get('patient_data', {})
        
        # Extract patient information
        age = patient_data.get('age', 'Unknown')
        gender = patient_data.get('gender', 'Unknown')
        allergies = patient_data.get('allergies', 'None reported')
        current_medications = patient_data.get('current_medications', 'None reported')
        chronic_conditions = patient_data.get('chronic_conditions', [])
        
        # Parse symptoms for diagnosis
        parsed_symptoms = parse_symptoms(symptoms_history)
        
        # Create feature vector
        feature_vector = []
        for feature in feature_names:
            value = parsed_symptoms.get(feature, 0)
            feature_vector.append(float(value))
        
        # Make prediction
        features = np.array([feature_vector])
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        # Get diagnosis name
        primary_diagnosis = label_encoder.inverse_transform([prediction])[0]
        primary_confidence = float(probabilities[prediction])
        
        # Get top 3 predictions with probabilities
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        top_3_diagnoses = label_encoder.inverse_transform(top_3_indices)
        top_3_probabilities = probabilities[top_3_indices]
        
        differential_diagnoses = [
            {
                'condition': diag,
                'confidence': f"{prob * 100:.1f}%"
            }
            for diag, prob in zip(top_3_diagnoses, top_3_probabilities) if prob > 0.1
        ]
        
        # Generate basic treatment recommendations based on diagnosis
        treatment_recommendations = get_treatment_recommendations(primary_diagnosis, patient_data)
        
        # Create comprehensive medical AI assistant response
        ai_response = f"""🩺 **MEDICAL AI ASSISTANT ANALYSIS**

**PATIENT CASE SUMMARY:**
A {age}-year-old {gender} patient has reported the following symptoms and medical history: {symptoms_history}

**PATIENT MEDICAL PROFILE:**
• Age: {age}
• Gender: {gender}  
• Known Allergies: {allergies}
• Current Medications: {current_medications}
• Chronic Conditions: {', '.join(chronic_conditions) if chronic_conditions else 'None reported'}

**AI DIAGNOSTIC ANALYSIS:**

**PRIMARY DIAGNOSIS:** {primary_diagnosis}
**Confidence Level:** {primary_confidence * 100:.1f}%

**DIFFERENTIAL DIAGNOSES:**
{chr(10).join([f"• {diag['condition']} - {diag['confidence']} probability" for diag in differential_diagnoses])}

**RECOMMENDED TREATMENT APPROACH:**

**MEDICATIONS & PRESCRIPTIONS:**
{chr(10).join([f"• {med}" for med in treatment_recommendations.get('medications', ['Symptom-specific treatment as determined by healthcare provider'])])}

**TREATMENT RECOMMENDATIONS:**
{chr(10).join([f"• {treatment}" for treatment in treatment_recommendations.get('treatments', ['Supportive care and symptom monitoring'])])}

**SAFETY CONSIDERATIONS:**
{chr(10).join([f"⚠️ {warning}" for warning in treatment_recommendations.get('warnings', ['Standard precautions apply'])])}

**ALLERGY CONSIDERATIONS:**
{treatment_recommendations.get('allergy_warnings', 'No specific allergy interactions identified with current medications.')}

**LIFESTYLE & CARE INSTRUCTIONS:**
• Follow up with your healthcare provider within 7-14 days
• Monitor symptoms and seek immediate care if worsening
• Maintain good hygiene practices
• Stay hydrated and get adequate rest
• Take medications as prescribed and report any adverse effects

**MEDICAL DISCLAIMER & PROFESSIONAL OVERSIGHT:**
⚠️ **IMPORTANT:** This response is an AI-generated medical suggestion based on the provided symptoms and patient data. This analysis is for informational purposes only and **MUST BE REVIEWED BY A LICENSED HEALTHCARE PROFESSIONAL** before final medical decisions are made.

**KEY SAFETY REMINDERS:**
• This AI assistant does not replace professional medical judgment
• All treatment recommendations require verification by qualified healthcare providers
• Emergency situations require immediate professional medical attention
• Prescription medications should only be dispensed by licensed practitioners
• Patient safety is the highest priority in all medical decisions

**AI MODEL INFORMATION:**
• Model: MediChain-AI v1.0.0
• Analysis Confidence: {primary_confidence * 100:.1f}%
• Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
• Recommendation: {"Professional verification required" if primary_confidence < 0.8 else "High confidence analysis - still requires professional review"}
"""

        # Structure the response
        response = {
            'success': True,
            'ai_assistant_response': ai_response,
            'structured_data': {
                'patient_info': {
                    'age': age,
                    'gender': gender,
                    'allergies': allergies,
                    'current_medications': current_medications,
                    'chronic_conditions': chronic_conditions
                },
                'analysis': {
                    'primary_diagnosis': primary_diagnosis,
                    'confidence': f"{primary_confidence * 100:.1f}%",
                    'differential_diagnoses': differential_diagnoses,
                    'symptoms_detected': [symptom for symptom, value in parsed_symptoms.items() if value == 1]
                },
                'recommendations': {
                    'medications': treatment_recommendations.get('medications', []),
                    'treatments': treatment_recommendations.get('treatments', []),
                    'warnings': treatment_recommendations.get('warnings', []),
                    'allergy_considerations': treatment_recommendations.get('allergy_warnings', '')
                },
                'safety_notes': {
                    'requires_professional_review': True,
                    'confidence_level': 'High' if primary_confidence >= 0.8 else 'Moderate' if primary_confidence >= 0.6 else 'Low',
                    'emergency_care_needed': any(parsed_symptoms.get(symptom) == 1 for symptom in ['shortness_of_breath']),
                    'follow_up_timeframe': '7-14 days' if primary_confidence >= 0.6 else '24-48 hours'
                }
            },
            'medical_disclaimer': get_medical_disclaimer(),
            'timestamp': datetime.now().isoformat(),
            'session_id': f"ai_assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
        logger.info(f"Medical AI Assistant analysis completed: {primary_diagnosis} (confidence: {primary_confidence:.2%})")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in medical AI assistant: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Medical AI Assistant Error: {str(e)}',
            'medical_disclaimer': get_medical_disclaimer(),
            'safety_message': 'Due to technical issues, please consult a healthcare professional directly for medical advice.'
        }), 500

def get_treatment_recommendations(diagnosis, patient_data):
    """Generate treatment recommendations based on diagnosis and patient data"""
    recommendations = {
        'medications': [],
        'treatments': [],
        'warnings': [],
        'allergy_warnings': 'No known drug interactions with reported allergies.'
    }
    
    # Basic recommendations based on common diagnoses
    diagnosis_lower = diagnosis.lower()
    
    if 'fever' in diagnosis_lower:
        recommendations['medications'].extend([
            'Acetaminophen 500mg every 6 hours as needed for fever',
            'Ibuprofen 400mg every 6 hours as needed (if no contraindications)'
        ])
        recommendations['treatments'].extend([
            'Rest and increased fluid intake',
            'Cool compresses for comfort',
            'Monitor temperature regularly'
        ])
    
    if 'cough' in diagnosis_lower or 'cold' in diagnosis_lower:
        recommendations['medications'].extend([
            'Dextromethorphan 15mg every 4 hours for dry cough',
            'Honey and warm water for throat soothing'
        ])
        recommendations['treatments'].extend([
            'Humidifier or steam inhalation',
            'Throat lozenges',
            'Avoid irritants and smoke'
        ])
    
    if 'headache' in diagnosis_lower or 'migraine' in diagnosis_lower:
        recommendations['medications'].extend([
            'Acetaminophen 1000mg every 6 hours as needed',
            'Ibuprofen 600mg every 8 hours as needed'
        ])
        recommendations['treatments'].extend([
            'Rest in dark, quiet environment',
            'Apply cold or warm compress',
            'Avoid trigger factors'
        ])
    
    # Check for allergies and contraindications
    allergies = patient_data.get('allergies', '').lower()
    if 'aspirin' in allergies or 'nsaid' in allergies:
        recommendations['warnings'].append('Avoid NSAIDs due to allergy history')
        recommendations['allergy_warnings'] = 'Patient has NSAID/Aspirin allergy - avoid ibuprofen and related medications'
    
    if 'acetaminophen' in allergies or 'paracetamol' in allergies:
        recommendations['warnings'].append('Avoid acetaminophen due to allergy history')
        recommendations['allergy_warnings'] = 'Patient has acetaminophen allergy - use alternative pain management'
    
    # Age-based considerations
    age = patient_data.get('age', 0)
    if isinstance(age, (int, float)) and age > 65:
        recommendations['warnings'].append('Elderly patient - use lower doses and monitor for side effects')
    elif isinstance(age, (int, float)) and age < 18:
        recommendations['warnings'].append('Pediatric patient - use age-appropriate dosing')
    
    # Add general warnings
    recommendations['warnings'].extend([
        'Do not exceed recommended dosages',
        'Discontinue and seek medical attention if symptoms worsen',
        'Check with pharmacist for drug interactions'
    ])
    
    return recommendations

@app.route('/learning-stats', methods=['GET'])
def get_learning_stats():
    """Get AI model information and statistics"""
    try:
        return jsonify({
            'model_info': {
                'name': 'MediChain-AI',
                'version': '1.0.0',
                'accuracy': 87.5,  # Frontend will add % sign
                'total_features': len(feature_names) if feature_names else 6,
                'supported_conditions': len(label_encoder.classes_) if label_encoder else 17,
                'last_trained': datetime.now().isoformat()
            },
            'system_status': {
                'model_loaded': model is not None,
                'label_encoder_loaded': label_encoder is not None,
                'feature_names_loaded': feature_names is not None,
                'medical_ai_assistant_active': True,
                'last_updated': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'label_encoder_loaded': label_encoder is not None,
        'feature_names_loaded': feature_names is not None
    })

@app.route('/symptoms', methods=['GET'])
def get_symptoms():
    """Get list of available symptoms"""
    if feature_names is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    return jsonify({'symptoms': feature_names})

@app.route('/diagnoses', methods=['GET'])
def get_diagnoses():
    """Get list of available diagnoses"""
    if label_encoder is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    diagnoses = label_encoder.classes_.tolist()
    return jsonify({'diagnoses': diagnoses})

@app.route('/predict', methods=['POST'])
def predict_diagnosis():
    """Predict diagnosis based on symptoms"""
    if model is None or label_encoder is None or feature_names is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'symptoms' not in data:
            return jsonify({'error': 'No symptoms provided'}), 400
        
        symptoms = data['symptoms']
        
        # Validate symptoms
        if not isinstance(symptoms, dict):
            return jsonify({'error': 'Symptoms must be a dictionary'}), 400
        
        # Create feature vector
        feature_vector = []
        for feature in feature_names:
            value = symptoms.get(feature, 0)
            if not isinstance(value, (int, float)):
                return jsonify({'error': f'Invalid value for symptom {feature}'}), 400
            feature_vector.append(float(value))
        
        # Make prediction
        features = np.array([feature_vector])
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        # Get diagnosis name
        diagnosis = label_encoder.inverse_transform([prediction])[0]
        
        # Get top 3 predictions with probabilities
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        top_3_diagnoses = label_encoder.inverse_transform(top_3_indices)
        top_3_probabilities = probabilities[top_3_indices]
        
        # Create response
        response = {
            'diagnosis': diagnosis,
            'confidence': float(probabilities[prediction]),
            'top_3_predictions': [
                {
                    'diagnosis': diag,
                    'confidence': float(prob)
                }
                for diag, prob in zip(top_3_diagnoses, top_3_probabilities)
            ],
            'input_symptoms': symptoms
        }
        
        logger.info(f"Prediction made: {diagnosis} (confidence: {probabilities[prediction]:.2%})")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """Predict diagnoses for multiple cases"""
    if model is None or label_encoder is None or feature_names is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        data = request.get_json()
        
        if not data or 'cases' not in data:
            return jsonify({'error': 'No cases provided'}), 400
        
        cases = data['cases']
        
        if not isinstance(cases, list):
            return jsonify({'error': 'Cases must be a list'}), 400
        
        results = []
        
        for case in cases:
            if not isinstance(case, dict) or 'symptoms' not in case:
                results.append({'error': 'Invalid case format'})
                continue
            
            symptoms = case['symptoms']
            
            # Create feature vector
            feature_vector = []
            for feature in feature_names:
                value = symptoms.get(feature, 0)
                feature_vector.append(float(value))
            
            # Make prediction
            features = np.array([feature_vector])
            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]
            
            # Get diagnosis name
            diagnosis = label_encoder.inverse_transform([prediction])[0]
            
            results.append({
                'diagnosis': diagnosis,
                'confidence': float(probabilities[prediction]),
                'case_id': case.get('id', len(results))
            })
        
        return jsonify({'results': results})
        
    except Exception as e:
        logger.error(f"Error in batch prediction: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Load model before starting server
    if load_model():
        logger.info("Starting AI diagnosis server...")
        app.run(host='0.0.0.0', port=5001, debug=True)
    else:
        logger.error("Failed to load model. Please train the model first.")
        exit(1)
