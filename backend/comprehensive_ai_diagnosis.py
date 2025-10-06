
"""
MediChain Comprehensive AI Diagnosis System v3.0
Enhanced with patient conditions and comprehensive prescriptions
"""

import numpy as np
import pandas as pd
import joblib
import json
import os
import re
from typing import Dict, List, Union, Optional

class ComprehensiveAIDiagnosis:
    def __init__(self, model_path=None,
                 encoder_path=None,
                 features_path=None,
                 categorical_encoders_path=None,
                 prescriptions_path=None,
                 symptom_columns_path=None,
                 enhanced_database_path=None):
        """Initialize the comprehensive AI diagnosis system"""

        # Set default paths relative to the backend directory
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        
        if model_path is None:
            model_path = os.path.join(backend_dir, 'final_comprehensive_model.pkl')
        if encoder_path is None:
            encoder_path = os.path.join(backend_dir, 'final_comprehensive_encoder.pkl')
        if features_path is None:
            features_path = os.path.join(backend_dir, 'final_comprehensive_features.pkl')
        if categorical_encoders_path is None:
            categorical_encoders_path = os.path.join(backend_dir, 'final_comprehensive_categorical_encoders.pkl')
        if prescriptions_path is None:
            prescriptions_path = os.path.join(backend_dir, 'final_comprehensive_prescriptions.pkl')
        if symptom_columns_path is None:
            symptom_columns_path = os.path.join(backend_dir, 'final_comprehensive_symptom_columns.pkl')
        if enhanced_database_path is None:
            enhanced_database_path = os.path.join(backend_dir, 'enhanced_conditions_database.json')

        try:
            # Load model components
            self.model = joblib.load(model_path)
            self.diagnosis_encoder = joblib.load(encoder_path) 
            self.feature_columns = joblib.load(features_path)
            self.categorical_encoders = joblib.load(categorical_encoders_path)
            self.prescriptions_map = joblib.load(prescriptions_path)
            self.symptom_columns = joblib.load(symptom_columns_path)

            # Load enhanced conditions database with medications
            try:
                with open(enhanced_database_path, 'r', encoding='utf-8') as f:
                    self.enhanced_conditions = json.load(f)
                print(f"✅ Enhanced conditions database loaded: {len(self.enhanced_conditions)} conditions")
            except FileNotFoundError:
                print("⚠️ Enhanced conditions database not found, using fallback")
                self.enhanced_conditions = {}

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

            self.model_version = 'MediChain-Comprehensive-v3.0-NLP'
            print(f"SUCCESS: {self.model_version} loaded successfully!")
            
            # Load NLP condition extraction patterns
            self.condition_patterns = self._load_condition_patterns()

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
    
    def _load_condition_patterns(self):
        """Load condition keyword patterns for NLP extraction"""
        return {
            'Common Cold': ['cold', 'runny nose', 'sneezing', 'congestion', 'nasal discharge'],
            'Flu': ['flu', 'influenza', 'fever', 'body aches', 'chills', 'muscle pain'],
            'COVID-19': ['covid', 'coronavirus', 'loss of taste', 'loss of smell', 'dry cough'],
            'Pneumonia': ['pneumonia', 'chest infection', 'productive cough', 'lung infection'],
            'Bronchitis': ['bronchitis', 'persistent cough', 'phlegm', 'chest congestion'],
            'Asthma': ['asthma', 'wheezing', 'breathing problems', 'shortness of breath'],
            'Allergies': ['allergies', 'sneezing', 'itchy eyes', 'seasonal', 'hay fever'],
            'Sinusitis': ['sinus', 'facial pressure', 'nasal congestion', 'sinus pressure'],
            'Migraine': ['migraine', 'severe headache', 'light sensitivity', 'photophobia'],
            'Tension Headache': ['tension headache', 'pressure headache', 'stress headache'],
            'Gastroenteritis': ['stomach bug', 'food poisoning', 'stomach flu', 'gastroenteritis'],
            'UTI': ['urinary', 'burning urination', 'frequent urination', 'bladder infection'],
            'Strep Throat': ['strep', 'severe sore throat', 'throat infection', 'strep throat'],
            'Ear Infection': ['ear infection', 'ear pain', 'hearing problems', 'earache'],
            'Hypertension': ['high blood pressure', 'hypertension', 'elevated bp', 'blood pressure'],
            'Diabetes': ['diabetes', 'high blood sugar', 'frequent urination', 'excessive thirst'],
            'Anxiety': ['anxiety', 'panic', 'worry', 'nervousness', 'anxious'],
            'Depression': ['depression', 'sadness', 'low mood', 'hopelessness', 'depressed'],
            'Arthritis': ['arthritis', 'joint pain', 'stiffness', 'joint swelling'],
            'Back Pain': ['back pain', 'lower back', 'spine pain', 'backache'],
            'Heart Attack': ['chest pain', 'heart attack', 'cardiac', 'crushing chest pain'],
            'Appendicitis': ['appendix', 'lower right pain', 'abdominal pain', 'appendicitis'],
            'Kidney Stones': ['kidney stones', 'flank pain', 'kidney pain', 'severe side pain'],
            'Food Poisoning': ['food poisoning', 'vomiting', 'diarrhea', 'stomach cramps'],
            'Dehydration': ['dehydration', 'thirsty', 'dry mouth', 'lightheaded']
        }
    
    def extract_conditions_from_text(self, user_input):
        """Extract possible conditions from user input using NLP and keyword matching"""
        
        user_text = user_input.lower()
        possible_conditions = []
        
        # Extract conditions based on keyword matching
        for condition, keywords in self.condition_patterns.items():
            matches = []
            for keyword in keywords:
                if keyword in user_text:
                    matches.append(keyword)
            
            if matches:
                possible_conditions.append({
                    'condition': condition,
                    'matched_keywords': matches,
                    'reasoning': f"Detected: {', '.join(matches)}",
                    'relevance': 'High' if len(matches) >= 2 else 'Medium'
                })
        
        # Sort by number of matched keywords (most relevant first)
        possible_conditions.sort(key=lambda x: len(x['matched_keywords']), reverse=True)
        
        return possible_conditions[:3]  # Return top 3 matches

    def convert_age_to_group(self, age):
        """Convert numeric age to age group"""
        if age is None:
            return 'adult'
        
        if isinstance(age, str):
            # If it's already an age group string, return as is
            if age.lower() in ['child', 'teen', 'adult', 'senior']:
                return age.lower()
            # Try to convert to number
            try:
                age = int(age)
            except ValueError:
                return 'adult'
        
        if age < 13:
            return 'child'
        elif age < 20:
            return 'teen'
        elif age < 65:
            return 'adult'
        else:
            return 'senior'
    
    def encode_patient_conditions(self, patient_data: Dict) -> Dict:
        """Encode patient condition data using trained encoders"""
        encoded_data = {}
        
        for col, encoder in self.categorical_encoders.items():
            value = patient_data.get(col, 'none')  # Default to 'none' instead of 'unknown'
            try:
                encoded_data[col + '_encoded'] = encoder.transform([value])[0]
            except ValueError:
                # Handle unseen values by using the first class (index 0)
                encoded_data[col + '_encoded'] = 0
        
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
                'gender': 'male',  # Use valid gender instead of 'unknown'
                'underlying_conditions': 'none',
                'recent_exposure': 'none',
                'symptom_onset': 'gradual',
                'progression': 'stable',
                'duration_days': 7,
                'intensity': 'moderate'
            }

        # Encode patient conditions
        encoded_conditions = self.encode_patient_conditions(patient_conditions)

        # Prepare feature vector with proper column names
        feature_data = {}
        for col in self.feature_columns:
            if col in symptom_flags:
                feature_data[col] = float(symptom_flags[col])
            elif col in patient_conditions:
                feature_data[col] = float(patient_conditions[col])
            elif col in encoded_conditions:
                feature_data[col] = float(encoded_conditions[col])
            else:
                feature_data[col] = 0.0

        # Create DataFrame with proper feature names to avoid sklearn warnings
        X_input = pd.DataFrame([feature_data], columns=self.feature_columns)
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

    def get_enhanced_condition_info(self, condition_name: str) -> Dict:
        """Get detailed information about a medical condition from enhanced database"""
        if condition_name in self.enhanced_conditions:
            return self.enhanced_conditions[condition_name]
        else:
            return {
                "description": f"Medical condition: {condition_name}",
                "medications": [{"name": "Consult healthcare provider", "dosage": "As prescribed", "purpose": "Professional guidance needed"}],
                "recommended_actions": ["Seek medical evaluation", "Follow prescribed treatment plan"],
                "when_to_see_doctor": "For proper diagnosis and treatment plan",
                "severity": "Consult doctor",
                "duration": "Variable"
            }

    def predict_enhanced_diagnosis(self, input_data: Union[str, Dict],
                                 patient_conditions: Optional[Dict] = None) -> Dict:
        """
        Enhanced diagnosis prediction with detailed medications and recommendations
        
        Returns comprehensive diagnosis with:
        - Detailed medical description
        - Over-the-counter medications with dosages
        - Recommended home care actions  
        - Severity and duration information
        - When to see a doctor guidelines
        """
        
        # Get basic diagnosis first
        basic_result = self.predict_comprehensive_diagnosis(input_data, patient_conditions)
        
        # Get enhanced condition information
        condition_info = self.get_enhanced_condition_info(basic_result['primary_diagnosis'])
        
        # Create enhanced result with all information
        enhanced_result = {
            # Basic diagnosis info
            'diagnosis': basic_result['primary_diagnosis'],
            'confidence': basic_result['confidence'],
            'confidence_percent': basic_result['confidence_percent'],
            'top_predictions': basic_result['top_3_predictions'],
            
            # Enhanced condition details
            'description': condition_info.get('description', ''),
            'severity': condition_info.get('severity', basic_result['severity']),
            'duration': condition_info.get('duration', 'Variable'),
            
            # Medications and treatment
            'medications': condition_info.get('medications', []),
            'recommended_actions': condition_info.get('recommended_actions', []),
            'when_to_see_doctor': condition_info.get('when_to_see_doctor', 'If symptoms persist or worsen'),
            
            # Additional info
            'active_symptoms_count': basic_result['active_symptoms_count'],
            'detected_symptoms': basic_result['detected_symptoms'],
            'patient_conditions': basic_result['patient_conditions'],
            
            # System info
            'model_version': f"{self.model_version}-Enhanced",
            'timestamp': basic_result['timestamp'],
            'disclaimer': "This is for informational purposes only. Always consult healthcare professionals for medical advice."
        }
        
        return enhanced_result

    def predict_nlp_diagnosis(self, input_data: Union[str, Dict],
                             patient_conditions: Optional[Dict] = None) -> Dict:
        """
        NLP-based diagnosis prediction without confidence levels
        
        Uses natural language processing to extract possible conditions
        based on keyword matching from the dataset patterns.
        
        Returns:
        - Possible conditions based on NLP extraction
        - Matched keywords and reasoning
        - Enhanced condition information
        - No confidence scores or percentages
        """
        
        # Extract conditions using NLP
        if isinstance(input_data, str):
            nlp_conditions = self.extract_conditions_from_text(input_data)
            symptom_flags = self.parse_natural_language_symptoms(input_data)
        else:
            # Handle dictionary input (convert to string first for NLP)
            symptom_text = ', '.join([k.replace('_', ' ') for k, v in input_data.items() if v == 1])
            nlp_conditions = self.extract_conditions_from_text(symptom_text)
            symptom_flags = input_data
        
        # Default patient conditions if not provided
        if patient_conditions is None:
            patient_conditions = {
                'age_group': 'adult',
                'gender': 'male',
                'underlying_conditions': 'none'
            }
        
        # Calculate severity based on symptoms (without confidence)
        active_symptoms = sum(1 for v in symptom_flags.values() if v == 1)
        if active_symptoms >= 8:
            severity = "Severe"
        elif active_symptoms >= 5:
            severity = "Moderate"  
        elif active_symptoms >= 2:
            severity = "Mild"
        else:
            severity = "Very Mild"
        
        # Prepare result without confidence levels
        if nlp_conditions:
            primary_condition = nlp_conditions[0]
            primary_diagnosis = primary_condition['condition']
            
            # Get enhanced condition information
            condition_info = self.get_enhanced_condition_info(primary_diagnosis)
            
            # Format alternative conditions without confidence
            alternative_conditions = []
            for i, cond in enumerate(nlp_conditions[1:3], 1):  # Get up to 2 alternatives
                alternative_conditions.append({
                    'diagnosis': cond['condition'],
                    'reasoning': cond['reasoning'],
                    'relevance': cond['relevance']
                })
            
            result = {
                # Primary diagnosis (no confidence)
                'diagnosis': primary_diagnosis,
                'primary_diagnosis': primary_diagnosis,
                'reasoning': primary_condition['reasoning'],
                'relevance': primary_condition['relevance'],
                
                # Enhanced condition details
                'description': condition_info.get('description', ''),
                'severity': condition_info.get('severity', severity),
                'duration': condition_info.get('duration', 'Variable'),
                
                # Alternative conditions (no confidence)
                'top_predictions': alternative_conditions,
                'alternative_conditions': alternative_conditions,
                
                # Medications and treatment
                'medications': condition_info.get('medications', []),
                'recommended_actions': condition_info.get('recommended_actions', []),
                'when_to_see_doctor': condition_info.get('when_to_see_doctor', 'If symptoms persist or worsen'),
                
                # Symptom information
                'active_symptoms_count': active_symptoms,
                'detected_symptoms': symptom_flags,
                'matched_keywords': primary_condition['matched_keywords'],
                
                # System info
                'model_version': f"{self.model_version}-NLP",
                'timestamp': pd.Timestamp.now().isoformat(),
                'method': 'NLP Keyword Matching',
                'disclaimer': "This analysis is based on keyword matching. Always consult healthcare professionals for medical advice."
            }
        else:
            # No conditions matched - provide general response
            result = {
                'diagnosis': 'General Health Assessment',
                'primary_diagnosis': 'General Health Assessment',
                'reasoning': 'No specific condition patterns detected',
                'relevance': 'Low',
                'description': 'Your symptoms do not clearly match common condition patterns.',
                'severity': severity,
                'medications': [{'name': 'Consult healthcare provider', 'dosage': 'As directed', 'purpose': 'Professional evaluation needed'}],
                'recommended_actions': ['Monitor symptoms', 'Stay hydrated', 'Get adequate rest', 'Consult a healthcare professional'],
                'when_to_see_doctor': 'If symptoms persist or worsen',
                'active_symptoms_count': active_symptoms,
                'detected_symptoms': symptom_flags,
                'matched_keywords': [],
                'top_predictions': [],
                'alternative_conditions': [],
                'model_version': f"{self.model_version}-NLP",
                'timestamp': pd.Timestamp.now().isoformat(),
                'method': 'NLP Keyword Matching',
                'disclaimer': "No specific patterns detected. Consult healthcare professionals for proper evaluation."
            }
        
        return result

    # Legacy method for backwards compatibility
    def diagnose(self, symptoms_text: str, **kwargs) -> Dict:
        """Legacy diagnosis method for backwards compatibility"""
        patient_info = {
            'age_group': kwargs.get('age_group', 'adult'),
            'gender': kwargs.get('gender', 'male'),  # Use valid gender
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
