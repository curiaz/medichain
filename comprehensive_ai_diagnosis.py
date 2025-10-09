
"""
MediChain Comprehensive AI Diagnosis System v3.0
Enhanced with patient conditions and comprehensive prescriptions
"""

import numpy as np
import pandas as pd
import joblib
import json
import re
from typing import Dict, List, Union, Optional

class ComprehensiveAIDiagnosis:
    def __init__(self, model_path='final_comprehensive_model.pkl',
                 encoder_path='final_comprehensive_encoder.pkl',
                 features_path='final_comprehensive_features.pkl',
                 categorical_encoders_path='final_comprehensive_categorical_encoders.pkl',
                 prescriptions_path='final_comprehensive_prescriptions.pkl',
                 symptom_columns_path='final_comprehensive_symptom_columns.pkl'):
        """Initialize the comprehensive AI diagnosis system"""

        try:
            # Load model components
            self.model = joblib.load(model_path)
            self.diagnosis_encoder = joblib.load(encoder_path) 
            self.feature_columns = joblib.load(features_path)
            self.categorical_encoders = joblib.load(categorical_encoders_path)
            self.prescriptions_map = joblib.load(prescriptions_path)
            self.symptom_columns = joblib.load(symptom_columns_path)

            # Symptom keyword mapping for natural language processing
            self.symptom_keywords = {
                'fever': ['fever', 'hot', 'temperature', 'burning up', 'feverish', 'pyrexia'],
                'cough': ['cough', 'coughing', 'hack', 'whooping', 'productive cough', 'dry cough'],
                'fatigue': ['tired', 'fatigue', 'exhausted', 'weak', 'lethargic', 'worn out', 'drained'],
                'shortness_of_breath': ['breathless', 'short of breath', 'breathing difficulty', 'dyspnea', 'wheezing'],
                'headache': ['headache', 'head pain', 'migraine', 'head pressure', 'cephalgia'],
                'sore_throat': ['sore throat', 'throat pain', 'scratchy throat', 'pharyngitis'],
                'nausea': ['nausea', 'nauseous', 'sick to stomach', 'queasy', 'vomiting', 'throw up'],
                'dizziness': ['dizzy', 'dizziness', 'lightheaded', 'vertigo', 'spinning'],
                'body_aches': ['body aches', 'muscle pain', 'joint pain', 'myalgia', 'arthralgia'],
                'runny_nose': ['runny nose', 'nasal discharge', 'stuffed nose', 'congestion'],
                'chest_pain': ['chest pain', 'chest tightness', 'chest pressure', 'angina'],
                'diarrhea': ['diarrhea', 'loose stools', 'watery stool', 'frequent bowel movements'],
                'loss_of_taste': ['loss of taste', 'can\'t taste', 'no taste', 'ageusia'],
                'loss_of_smell': ['loss of smell', 'can\'t smell', 'no smell', 'anosmia']
            }

            self.model_version = 'MediChain-Comprehensive-v3.0'
            print(f"SUCCESS: {self.model_version} loaded successfully!")

        except Exception as e:
            print(f"ERROR loading model: {e}")
            raise e

    def parse_natural_language_symptoms(self, text: str) -> Dict[str, int]:
        """Parse symptoms from natural language text"""
        text = text.lower()
        detected_symptoms = {}

        for symptom, keywords in self.symptom_keywords.items():
            detected_symptoms[symptom] = 0
            for keyword in keywords:
                if keyword in text:
                    detected_symptoms[symptom] = 1
                    break

        return detected_symptoms

    def encode_patient_conditions(self, patient_data: Dict) -> Dict:
        """Encode patient condition data using trained encoders"""
        encoded_data = {}

        for col, encoder in self.categorical_encoders.items():
            value = patient_data.get(col, 'unknown')
            try:
                encoded_data[col + '_encoded'] = encoder.transform([value])[0]
            except ValueError:
                # Handle unseen values
                encoded_data[col + '_encoded'] = encoder.transform(['unknown'])[0]

        return encoded_data

    def predict_comprehensive_diagnosis(self, input_data: Union[str, Dict], 
                                     patient_conditions: Optional[Dict] = None) -> Dict:
        """
        Comprehensive diagnosis prediction with enhanced features

        Args:
            input_data: Natural language text or symptom dictionary
            patient_conditions: Patient info (age_group, gender, etc.)

        Returns:
            Comprehensive diagnosis with prescriptions and recommendations
        """

        # Handle natural language input
        if isinstance(input_data, str):
            symptom_flags = self.parse_natural_language_symptoms(input_data)
        else:
            symptom_flags = input_data

        # Ensure all symptom columns are present
        for symptom in self.symptom_columns:
            if symptom not in symptom_flags:
                symptom_flags[symptom] = 0

        # Default patient conditions if not provided
        if patient_conditions is None:
            patient_conditions = {
                'age_group': 'adult',
                'gender': 'unknown',
                'underlying_conditions': 'none',
                'recent_exposure': 'none',
                'symptom_onset': 'gradual',
                'progression': 'stable',
                'duration_days': 7,
                'intensity': 'moderate'
            }

        # Encode patient conditions
        encoded_conditions = self.encode_patient_conditions(patient_conditions)

        # Prepare feature vector
        feature_vector = []
        for col in self.feature_columns:
            if col in symptom_flags:
                feature_vector.append(float(symptom_flags[col]))
            elif col in patient_conditions:
                feature_vector.append(float(patient_conditions[col]))
            elif col in encoded_conditions:
                feature_vector.append(float(encoded_conditions[col]))
            else:
                feature_vector.append(0.0)

        # Make prediction
        X_input = np.array([feature_vector])
        prediction_id = self.model.predict(X_input)[0]
        prediction_proba = self.model.predict_proba(X_input)[0]

        # Get top 3 predictions
        top_3_indices = np.argsort(prediction_proba)[-3:][::-1]
        top_3_predictions = []

        for idx in top_3_indices:
            diagnosis_name = self.diagnosis_encoder.inverse_transform([idx])[0]
            confidence = prediction_proba[idx]
            top_3_predictions.append({
                'diagnosis': diagnosis_name,
                'confidence': confidence,
                'confidence_percent': f"{confidence*100:.1f}%"
            })

        # Primary diagnosis
        primary_diagnosis = self.diagnosis_encoder.inverse_transform([prediction_id])[0]
        primary_confidence = max(prediction_proba)

        # Get prescription info
        prescription_info = self.prescriptions_map.get(prediction_id, {
            'medications': [{'name': 'Consult healthcare provider', 'dosage': 'As directed', 'duration': 7}],
            'diagnosis_description': f'{primary_diagnosis} - Professional medical evaluation recommended.',
            'recommended_action': 'Schedule appointment with healthcare provider for proper assessment.',
            'severity': 'varies',
            'follow_up_days': 7,
            'emergency_signs': ['worsening symptoms', 'severe pain', 'difficulty breathing']
        })

        # Calculate severity based on symptoms
        active_symptoms = sum(1 for v in symptom_flags.values() if v == 1)
        if active_symptoms >= 8:
            severity = "Severe"
        elif active_symptoms >= 5:
            severity = "Moderate"  
        elif active_symptoms >= 2:
            severity = "Mild"
        else:
            severity = "Very Mild"

        # Prepare comprehensive result
        result = {
            'primary_diagnosis': primary_diagnosis,
            'confidence': primary_confidence,
            'confidence_percent': f"{primary_confidence*100:.1f}%",
            'severity': severity,
            'active_symptoms_count': active_symptoms,
            'top_3_predictions': top_3_predictions,
            'medications': prescription_info.get('medications', []),
            'diagnosis_description': prescription_info.get('diagnosis_description', ''),
            'recommended_action': prescription_info.get('recommended_action', ''),
            'follow_up_days': prescription_info.get('follow_up_days', 7),
            'emergency_signs': prescription_info.get('emergency_signs', []),
            'patient_conditions': patient_conditions,
            'detected_symptoms': symptom_flags,
            'model_version': self.model_version,
            'timestamp': pd.Timestamp.now().isoformat()
        }

        return result

    # Legacy method for backwards compatibility
    def diagnose(self, symptoms_text: str, **kwargs) -> Dict:
        """Legacy diagnosis method for backwards compatibility"""
        patient_info = {
            'age_group': kwargs.get('age_group', 'adult'),
            'gender': kwargs.get('gender', 'unknown'),
            'underlying_conditions': kwargs.get('underlying_conditions', 'none'),
            'recent_exposure': kwargs.get('recent_exposure', 'none'),
            'symptom_onset': kwargs.get('symptom_onset', 'gradual'),
            'progression': kwargs.get('progression', 'stable'),
            'duration_days': kwargs.get('duration_days', 7),
            'intensity': kwargs.get('intensity', 'moderate')
        }

        return self.predict_comprehensive_diagnosis(symptoms_text, patient_info)

# Example usage
if __name__ == "__main__":
    try:
        ai = ComprehensiveAIDiagnosis()

        # Test with natural language
        result = ai.predict_comprehensive_diagnosis(
            "I have fever, bad cough, and can't taste anything",
            {'age_group': 'adult', 'gender': 'male', 'underlying_conditions': 'none'}
        )

        print("Test Result:")
        print(f"Diagnosis: {result['primary_diagnosis']}")
        print(f"Confidence: {result['confidence_percent']}")
        print(f"Severity: {result['severity']}")

    except Exception as e:
        print(f"Error testing AI: {e}")
