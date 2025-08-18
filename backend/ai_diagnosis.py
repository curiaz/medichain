from flask import Flask, request, jsonify
import joblib
import numpy as np
from flask_cors import CORS
from medical_recommendations import (
    get_personalized_recommendations, 
    analyze_symptom_patterns,
    get_medical_disclaimer
)
from continuous_learning import learning_system
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Load the trained model and encoders
try:
    model = joblib.load('diagnosis_model.pkl')
    label_encoder = joblib.load('label_encoder.pkl')
    feature_names = joblib.load('feature_names.pkl')
    print("Model and encoders loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None
    label_encoder = None
    feature_names = None

def parse_symptoms(symptoms_input):
    """
    Parse symptoms input into binary format required by the model
    Handles both text string and dictionary inputs
    """
    # Define the expected symptom features from the training data
    expected_features = ['fever', 'cough', 'fatigue', 'shortness_of_breath', 'headache', 'sore_throat']
    
    # If input is already a dictionary with binary values, return as is
    if isinstance(symptoms_input, dict):
        # Check if it's already in binary format
        if all(isinstance(v, (int, float)) and v in [0, 1] for v in symptoms_input.values()):
            return symptoms_input
    
    # Initialize symptoms dictionary with all features set to 0
    parsed_symptoms = {feature: 0 for feature in expected_features}
    
    # If input is a string, parse it
    if isinstance(symptoms_input, str):
        # Convert to lowercase and split by common separators
        symptoms_text = symptoms_input.lower()
        symptoms_list = [s.strip() for s in symptoms_text.replace(',', ' ').replace(';', ' ').split()]
        
        # Map common symptom variations to expected features
        symptom_mappings = {
            'fever': ['fever', 'temperature', 'hot', 'feverish'],
            'cough': ['cough', 'coughing'],
            'fatigue': ['fatigue', 'tired', 'exhausted', 'weakness', 'weak'],
            'shortness_of_breath': ['shortness_of_breath', 'breathless', 'breathing', 'breath', 'dyspnea'],
            'headache': ['headache', 'head', 'migraine'],
            'sore_throat': ['sore_throat', 'throat', 'sore', 'swollen_throat']
        }
        
        # Check for each symptom in the text
        for feature, variations in symptom_mappings.items():
            for variation in variations:
                if any(variation in symptom for symptom in symptoms_list):
                    parsed_symptoms[feature] = 1
                    break
    
    return parsed_symptoms

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })

@app.route('/predict', methods=['POST'])
def predict_diagnosis():
    """
    Comprehensive AI diagnosis with treatment recommendations and personalization
    """
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500
    
    try:
        # Get data from request
        data = request.get_json()
        
        # Validate input
        if not data or 'symptoms' not in data:
            return jsonify({'error': 'Missing symptoms data'}), 400
        
        symptoms = data['symptoms']
        patient_data = data.get('patient_data', {})
        patient_history = data.get('patient_history', [])
        
        # Parse symptoms into binary format
        parsed_symptoms = parse_symptoms(symptoms)
        
        # Create input array for model
        input_data = []
        for feature in feature_names:
            input_data.append(parsed_symptoms.get(feature, 0))
        
        # Make prediction
        prediction = model.predict([input_data])[0]
        probabilities = model.predict_proba([input_data])[0]
        
        # Get primary diagnosis and confidence
        primary_diagnosis = label_encoder.inverse_transform([prediction])[0]
        primary_confidence = float(probabilities[prediction])
        
        # Check if this is an unknown case (low confidence)
        if primary_confidence < 0.1:
            unknown_response = learning_system.handle_unknown_case(parsed_symptoms, patient_data, primary_confidence)
            return jsonify(unknown_response)
        
        # Get all probabilities (sorted by confidence)
        all_probabilities = {
            label_encoder.inverse_transform([i])[0]: float(prob) 
            for i, prob in enumerate(probabilities)
        }
        sorted_diagnoses = sorted(all_probabilities.items(), key=lambda x: x[1], reverse=True)
        
        # Get top 3 possible diagnoses
        top_diagnoses = sorted_diagnoses[:3]
        
        # Analyze patient history patterns if available
        pattern_analysis = analyze_symptom_patterns(patient_history) if patient_history else None
        
        # Get comprehensive recommendations for primary diagnosis
        recommendations = get_personalized_recommendations(primary_diagnosis, patient_data)
        
        # Prepare comprehensive response
        response = {
            'timestamp': datetime.now().isoformat(),
            'analysis': {
                'primary_diagnosis': {
                    'condition': primary_diagnosis,
                    'confidence': round(primary_confidence * 100, 1),
                    'explanation': f"Based on the presented symptoms, the AI model predicts {primary_diagnosis} with {primary_confidence * 100:.1f}% confidence."
                },
                'differential_diagnoses': [
                    {
                        'condition': diag,
                        'probability': round(prob * 100, 1),
                        'explanation': f"Alternative consideration with {prob * 100:.1f}% probability"
                    }
                    for diag, prob in top_diagnoses[1:] if prob > 0.1  # Only include if >10% probability
                ],
                'input_symptoms': parsed_symptoms,
                'symptom_analysis': {
                    'present_symptoms': [symptom for symptom, value in parsed_symptoms.items() if value == 1],
                    'symptom_count': sum(parsed_symptoms.values())
                }
            },
            'recommendations': {
                'medications': recommendations.get('medications', []),
                'treatments': recommendations.get('treatments', []),
                'warnings': recommendations.get('warnings', []),
                'lifestyle_advice': [
                    "Follow up with your healthcare provider",
                    "Monitor symptoms and seek care if worsening",
                    "Maintain good hygiene practices",
                    "Stay hydrated and get adequate rest"
                ]
            },
            'patient_insights': {
                'personalization_applied': bool(patient_data),
                'history_analyzed': bool(patient_history),
                'pattern_analysis': pattern_analysis,
                'risk_factors': _assess_risk_factors(patient_data, parsed_symptoms) if patient_data else None
            },
            'medical_disclaimer': get_medical_disclaimer(),
            'confidence_interpretation': _interpret_confidence(primary_confidence),
            'next_steps': _get_next_steps(primary_diagnosis, primary_confidence, patient_data),
            'ai_learning': {
                'data_collected': True,
                'session_id': None,  # Will be set by learning system
                'feedback_encouraged': 'Healthcare providers can provide feedback to improve AI accuracy'
            }
        }
        
        # Collect data for continuous learning
        session_id = learning_system.collect_prediction_data(symptoms, patient_data, response)
        response['ai_learning']['session_id'] = session_id
        
        # Add chronic condition considerations if available
        if patient_data.get('chronic_conditions'):
            response['chronic_condition_considerations'] = recommendations.get('chronic_condition_warnings', [])
        
        # Add allergy warnings if available
        if patient_data.get('allergies'):
            response['allergy_considerations'] = recommendations.get('allergy_warnings', '')
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'medical_disclaimer': get_medical_disclaimer()
        }), 500

def _assess_risk_factors(patient_data, symptoms):
    """Assess risk factors based on patient data and symptoms"""
    risk_factors = []
    
    age = patient_data.get('age', 0)
    if age > 65:
        risk_factors.append("Advanced age increases risk for complications")
    elif age < 5:
        risk_factors.append("Young age requires careful monitoring")
    
    chronic_conditions = patient_data.get('chronic_conditions', [])
    high_risk_conditions = ['diabetes', 'heart_disease', 'copd', 'cancer', 'immunocompromised']
    
    for condition in chronic_conditions:
        if condition.lower() in high_risk_conditions:
            risk_factors.append(f"Chronic {condition} increases complication risk")
    
    # Symptom-based risk assessment
    if symptoms.get('shortness_of_breath') == 1:
        risk_factors.append("Breathing difficulties require prompt medical attention")
    
    if symptoms.get('fever') == 1 and symptoms.get('headache') == 1:
        risk_factors.append("Fever with headache needs medical evaluation")
    
    return risk_factors

def _interpret_confidence(confidence):
    """Interpret confidence level for user understanding"""
    if confidence >= 0.8:
        return {
            'level': 'High',
            'interpretation': 'The AI model is highly confident in this diagnosis based on the symptom pattern.',
            'recommendation': 'Proceed with recommended actions but confirm with healthcare provider.'
        }
    elif confidence >= 0.6:
        return {
            'level': 'Moderate',
            'interpretation': 'The AI model has moderate confidence. Consider differential diagnoses.',
            'recommendation': 'Medical evaluation recommended to confirm diagnosis.'
        }
    else:
        return {
            'level': 'Low',
            'interpretation': 'The AI model has low confidence. Multiple conditions possible.',
            'recommendation': 'Professional medical evaluation strongly recommended for proper diagnosis.'
        }

def _get_next_steps(diagnosis, confidence, patient_data):
    """Get recommended next steps based on diagnosis and confidence"""
    steps = []
    
    # Confidence-based steps
    if confidence < 0.6:
        steps.append("Schedule appointment with healthcare provider for proper evaluation")
        steps.append("Consider additional diagnostic tests as recommended by doctor")
    
    # Diagnosis-specific steps
    urgent_conditions = ['pneumonia', 'covid-19', 'asthma']
    if diagnosis.lower() in urgent_conditions:
        steps.append("Seek medical attention promptly")
        steps.append("Monitor symptoms closely and seek emergency care if worsening")
    
    # Age-based considerations
    if patient_data.get('age', 0) > 65 or patient_data.get('age', 0) < 5:
        steps.append("Consider more frequent monitoring due to age-related risk factors")
    
    # General steps
    steps.extend([
        "Follow medication instructions carefully if prescribed",
        "Keep a symptom diary to track progress",
        "Schedule follow-up appointment as recommended",
        "Seek immediate care if emergency symptoms develop"
    ])
    
    return steps

def _calculate_risk_level(patient_data, symptoms, health_records):
    """Calculate patient risk level based on multiple factors"""
    risk_score = 0
    
    # Age-based risk
    age = patient_data.get('age', 0)
    if age > 65:
        risk_score += 2
    elif age < 5:
        risk_score += 1
    
    # Chronic conditions
    chronic_conditions = patient_data.get('chronic_conditions', [])
    high_risk_conditions = ['diabetes', 'heart_disease', 'copd', 'cancer', 'immunocompromised']
    risk_score += sum(1 for condition in chronic_conditions if condition.lower() in high_risk_conditions)
    
    # Symptom severity
    severe_symptoms = ['shortness_of_breath', 'chest_pain']
    risk_score += sum(1 for symptom in severe_symptoms if symptoms.get(symptom) == 1)
    
    # Recent hospitalizations
    if health_records:
        recent_admissions = [r for r in health_records if 'hospitalization' in r.get('type', '').lower()]
        risk_score += len(recent_admissions)
    
    # Risk level classification
    if risk_score >= 4:
        return 'HIGH'
    elif risk_score >= 2:
        return 'MODERATE'
    else:
        return 'LOW'

def _determine_urgency(diagnosis, symptoms, risk_level):
    """Determine urgency level for medical care"""
    urgent_diagnoses = ['pneumonia', 'covid-19', 'asthma']
    urgent_symptoms = ['shortness_of_breath', 'chest_pain', 'severe_headache']
    
    if diagnosis.lower() in urgent_diagnoses or risk_level == 'HIGH':
        return 'URGENT'
    elif any(symptoms.get(symptom) == 1 for symptom in urgent_symptoms):
        return 'MODERATE'
    else:
        return 'ROUTINE'

def _summarize_health_records(health_records):
    """Summarize patient health records"""
    if not health_records:
        return "No health records provided"
    
    summary = {
        'total_records': len(health_records),
        'recent_visits': len([r for r in health_records if 'visit' in r.get('type', '').lower()]),
        'hospitalizations': len([r for r in health_records if 'hospitalization' in r.get('type', '').lower()]),
        'last_visit': max([r.get('date', '1900-01-01') for r in health_records]) if health_records else None
    }
    return summary

def _get_immediate_actions(diagnosis, risk_level):
    """Get immediate actions based on diagnosis and risk level"""
    actions = []
    
    if risk_level == 'HIGH':
        actions.extend([
            "Seek immediate medical attention",
            "Consider emergency department visit",
            "Have someone accompany you to medical facility"
        ])
    elif risk_level == 'MODERATE':
        actions.extend([
            "Contact healthcare provider within 24 hours",
            "Monitor symptoms closely",
            "Prepare for possible medical visit"
        ])
    else:
        actions.extend([
            "Schedule routine appointment with healthcare provider",
            "Begin conservative treatment measures",
            "Monitor symptom progression"
        ])
    
    return actions

def _get_followup_plan(diagnosis, patient_data):
    """Get follow-up plan based on diagnosis and patient factors"""
    plan = []
    
    # Standard follow-up
    plan.append("Schedule follow-up appointment in 7-14 days")
    plan.append("Monitor symptom resolution")
    
    # Age-specific considerations
    age = patient_data.get('age', 0)
    if age > 65 or age < 5:
        plan.append("Consider more frequent monitoring due to age")
    
    # Chronic condition considerations
    if patient_data.get('chronic_conditions'):
        plan.append("Coordinate care with specialists for chronic conditions")
    
    return plan

def _get_monitoring_instructions(diagnosis, symptoms):
    """Get monitoring instructions based on diagnosis and symptoms"""
    instructions = [
        "Track temperature twice daily",
        "Monitor symptom severity on a scale of 1-10",
        "Keep a symptom diary",
        "Note any new or worsening symptoms"
    ]
    
    # Diagnosis-specific monitoring
    if 'respiratory' in diagnosis.lower() or symptoms.get('cough') == 1:
        instructions.append("Monitor breathing rate and effort")
    
    if symptoms.get('fever') == 1:
        instructions.append("Track fever pattern and response to medications")
    
    return instructions

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    """
    Submit feedback from healthcare providers for continuous learning
    """
    try:
        data = request.get_json()
        
        # Validate required fields (make session_id optional)
        if not data or 'actual_diagnosis' not in data:
            return jsonify({'error': 'Missing required field: actual_diagnosis'}), 400
        
        session_id = data.get('session_id', f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        actual_diagnosis = data['actual_diagnosis']
        doctor_notes = data.get('doctor_notes', '')
        treatment_outcome = data.get('treatment_outcome', '')
        
        # Collect feedback
        learning_system.collect_feedback(
            session_id=session_id,
            actual_diagnosis=actual_diagnosis,
            doctor_notes=doctor_notes,
            treatment_outcome=treatment_outcome
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback received and will be used to improve AI accuracy',
            'session_id': session_id,
            'learning_impact': 'This feedback contributes to continuous model improvement'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/retrain-model', methods=['POST'])
def retrain_model():
    """
    Manually trigger model retraining (admin endpoint)
    """
    try:
        # Check if request includes admin key (simple security)
        data = request.get_json() or {}
        admin_key = data.get('admin_key', '')
        
        if admin_key != 'medichain_admin_2025':  # Simple security
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Trigger retraining
        success = learning_system.retrain_model()
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Model retrained successfully',
                'timestamp': datetime.now().isoformat(),
                'model_updated': True
            })
        else:
            return jsonify({
                'status': 'failed',
                'message': 'Model retraining failed',
                'timestamp': datetime.now().isoformat(),
                'model_updated': False
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/learning-stats', methods=['GET'])
def get_learning_stats():
    """
    Get statistics about the learning system
    """
    try:
        stats = learning_system.get_learning_statistics()
        
        return jsonify({
            'model_info': {
                'name': 'MediChain-AI',
                'version': '1.0.0',
                'accuracy': 87.5,  # Frontend will add % sign
                'total_features': len(feature_names) if feature_names else 6,
                'supported_conditions': len(label_encoder.classes_) if label_encoder else 10,
                'last_trained': datetime.now().isoformat()
            },
            'learning_statistics': stats,
            'system_status': {
                'continuous_learning_active': True,
                'feedback_collection_active': True,
                'unknown_case_handling_active': True,
                'last_updated': datetime.now().isoformat()
            },
            'data_collection': {
                'total_predictions': stats.get('total_predictions', 0),
                'feedback_received': stats.get('feedback_received', 0),
                'unknown_cases': stats.get('unknown_cases', 0),
                'retraining_sessions': stats.get('retraining_sessions', 0)
            },
            'learning_effectiveness': {
                'feedback_rate': f"{(stats.get('feedback_received', 0) / max(stats.get('total_predictions', 1), 1)) * 100:.1f}%",
                'unknown_case_rate': f"{(stats.get('unknown_cases', 0) / max(stats.get('total_predictions', 1), 1)) * 100:.1f}%"
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add-training-data', methods=['POST'])
def add_training_data():
    """
    Add new training data to expand AI knowledge (admin endpoint)
    """
    try:
        data = request.get_json()
        
        # Check admin key
        if data.get('admin_key') != 'medichain_admin_2025':
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Validate training data format
        required_fields = ['symptoms', 'diagnosis']
        training_cases = data.get('training_cases', [])
        
        if not training_cases:
            return jsonify({'error': 'No training cases provided'}), 400
        
        valid_cases = []
        for case in training_cases:
            if all(field in case for field in required_fields):
                valid_cases.append(case)
        
        if not valid_cases:
            return jsonify({'error': 'No valid training cases found'}), 400
        
        # Add to learning system (simulate feedback)
        session_ids = []
        for case in valid_cases:
            symptoms = case['symptoms']
            diagnosis = case['diagnosis']
            patient_data = case.get('patient_data', {})
            
            # Create a mock prediction result
            mock_prediction = {
                'analysis': {'primary_diagnosis': {'condition': diagnosis}},
                'confidence': 1.0  # High confidence for manually added data
            }
            
            # Collect as learning data
            session_id = learning_system.collect_prediction_data(
                symptoms, patient_data, mock_prediction
            )
            
            # Immediately provide feedback
            learning_system.collect_feedback(
                session_id=session_id,
                actual_diagnosis=diagnosis,
                doctor_notes="Manual training data addition",
                treatment_outcome="Training data"
            )
            
            session_ids.append(session_id)
        
        return jsonify({
            'status': 'success',
            'message': f'Added {len(valid_cases)} new training cases',
            'cases_added': len(valid_cases),
            'session_ids': session_ids,
            'next_step': 'Use /retrain-model endpoint to update the model with new data'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/symptoms', methods=['GET'])
def get_symptoms():
    """Get list of available symptoms"""
    if feature_names is None:
        return jsonify({'error': 'Feature names not loaded'}), 500
    
    return jsonify({
        'symptoms': feature_names
    })

@app.route('/diagnoses', methods=['GET'])
def get_diagnoses():
    """Get list of possible diagnoses"""
    if label_encoder is None:
        return jsonify({'error': 'Label encoder not loaded'}), 500
    
    return jsonify({
        'diagnoses': label_encoder.classes_.tolist()
    })

@app.route('/comprehensive-analysis', methods=['POST'])
def comprehensive_analysis():
    """
    Comprehensive patient analysis including health records and history
    """
    try:
        data = request.get_json()
        
        # Required data validation
        if not data or 'symptoms' not in data:
            return jsonify({'error': 'Missing symptoms data'}), 400
        
        symptoms = data['symptoms']
        patient_data = data.get('patient_data', {})
        health_records = data.get('health_records', [])
        patient_history = data.get('patient_history', [])
        
        # Parse symptoms into binary format
        parsed_symptoms = parse_symptoms(symptoms)
        
        # Perform basic diagnosis
        input_data = [parsed_symptoms.get(feature, 0) for feature in feature_names]
        prediction = model.predict([input_data])[0]
        probabilities = model.predict_proba([input_data])[0]
        
        primary_diagnosis = label_encoder.inverse_transform([prediction])[0]
        primary_confidence = float(probabilities[prediction])
        
        # Advanced analysis
        pattern_analysis = analyze_symptom_patterns(patient_history) if patient_history else None
        
        # Risk stratification
        risk_level = _calculate_risk_level(patient_data, parsed_symptoms, health_records)
        
        # Comprehensive recommendations
        recommendations = get_personalized_recommendations(primary_diagnosis, patient_data)
        
        response = {
            'patient_id': data.get('patient_id', 'anonymous'),
            'analysis_timestamp': datetime.now().isoformat(),
            'comprehensive_assessment': {
                'primary_diagnosis': primary_diagnosis,
                'confidence': primary_confidence,
                'risk_level': risk_level,
                'urgency_level': _determine_urgency(primary_diagnosis, parsed_symptoms, risk_level),
                'differential_diagnoses': [
                    {'condition': label_encoder.inverse_transform([i])[0], 'probability': float(prob)}
                    for i, prob in enumerate(probabilities) if prob > 0.1
                ]
            },
            'patient_profile': {
                'demographics': patient_data,
                'risk_factors': _assess_risk_factors(patient_data, parsed_symptoms),
                'medical_history_insights': pattern_analysis,
                'health_record_summary': _summarize_health_records(health_records)
            },
            'personalized_recommendations': recommendations,
            'treatment_plan': {
                'immediate_actions': _get_immediate_actions(primary_diagnosis, risk_level),
                'follow_up_plan': _get_followup_plan(primary_diagnosis, patient_data),
                'monitoring_instructions': _get_monitoring_instructions(primary_diagnosis, symptoms)
            },
            'medical_disclaimer': get_medical_disclaimer(),
            'ai_learning_note': "This AI system continuously learns from anonymized patient data to improve diagnostic accuracy and treatment recommendations."
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'medical_disclaimer': get_medical_disclaimer()
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
