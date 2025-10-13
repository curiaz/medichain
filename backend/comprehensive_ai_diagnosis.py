
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
import csv
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
            
            # Load realistic medical dataset
            self.load_medical_dataset()
            
            # Load condition reason mapping
            self.load_condition_reasons()
            
            # Load enhanced diagnosis dataset
            self.load_enhanced_diagnosis_dataset()
            
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
    
    def _is_medically_relevant_prediction(self, diagnosis: str, input_symptoms: str) -> bool:
        """Check if a diagnosis prediction is medically relevant to the input symptoms"""
        if isinstance(input_symptoms, dict):
            # Convert symptom flags back to text for analysis
            active_symptoms = [symptom for symptom, value in input_symptoms.items() if value == 1]
            symptoms_text = " ".join(active_symptoms).lower()
        else:
            symptoms_text = str(input_symptoms).lower()
        
        # Get condition patterns for this diagnosis
        condition_keywords = self.condition_patterns.get(diagnosis, [])
        
        # If no patterns defined, allow the prediction (benefit of doubt)
        if not condition_keywords:
            return True
            
        # Check if any condition keyword matches the input symptoms
        for keyword in condition_keywords:
            if keyword.lower() in symptoms_text:
                return True
                
        # Enhanced symptom overlaps for better matching
        symptom_overlaps = {
            'Migraine': ['headache', 'head pain', 'dizzy', 'dizziness', 'nausea', 'light sensitivity'],
            'Sinusitis': ['headache', 'runny nose', 'nasal', 'congestion', 'pressure', 'facial pressure'],
            'Common Cold': ['runny nose', 'congestion', 'headache', 'tired', 'fatigue', 'sneezing'],
            'Tension Headache': ['headache', 'head pain', 'stress', 'tired', 'dizzy', 'pressure'],
            'Allergies': ['runny nose', 'congestion', 'sneezing', 'itchy', 'seasonal'],
            'Seasonal Allergies': ['runny nose', 'congestion', 'sneezing', 'itchy', 'seasonal'],
            'Vertigo': ['dizzy', 'dizziness', 'spinning', 'balance'],
            'Flu': ['fever', 'cough', 'tired', 'body aches', 'chills', 'sore throat'],
            'COVID-19': ['fever', 'cough', 'sore throat', 'loss of taste', 'loss of smell'],
            'Strep Throat': ['sore throat', 'throat pain', 'fever', 'swollen'],
            'Bronchitis': ['cough', 'chest', 'breathing', 'phlegm'],
            'Asthma': ['breathing', 'wheez', 'shortness of breath', 'chest'],
            'Pneumonia': ['cough', 'fever', 'chest pain', 'breathing'],
            'Kidney Stones': ['flank pain', 'side pain', 'kidney pain', 'blood in urine', 'severe pain', 'sharp pain'],
            'Lyme Disease': ['joint pain', 'rash', 'tick bite', 'bull', 'fatigue', 'fever'],
            'Heart Attack': ['chest pain', 'crushing', 'pressure', 'heart', 'cardiac']
        }
        
        overlap_keywords = symptom_overlaps.get(diagnosis, [])
        for keyword in overlap_keywords:
            if keyword in symptoms_text:
                return True
        
        # Special filtering for clearly inappropriate predictions
        clearly_inappropriate = {
            'Kidney Stones': ['runny nose', 'congestion', 'sneezing', 'itchy eyes', 'seasonal'],
            'Lyme Disease': ['runny nose', 'congestion', 'sneezing', 'seasonal allergy'],
            'Eczema': ['fever', 'cough', 'sore throat', 'chest pain', 'breathing']
        }
        
        inappropriate_keywords = clearly_inappropriate.get(diagnosis, [])
        for keyword in inappropriate_keywords:
            if keyword in symptoms_text and not any(ok in symptoms_text for ok in overlap_keywords):
                print(f"🚫 Filtered out clearly inappropriate prediction: {diagnosis} for symptoms: {symptoms_text[:50]}")
                return False
                
        # Default: allow prediction if no clear mismatch found
        return True
    
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
            'Kidney Stones': ['kidney stones', 'flank pain', 'kidney pain', 'severe side pain', 'blood in urine', 'sharp pain'],
            'Food Poisoning': ['food poisoning', 'vomiting', 'diarrhea', 'stomach cramps'],
            'Dehydration': ['dehydration', 'thirsty', 'dry mouth', 'lightheaded'],
            'Lyme Disease': ['lyme disease', 'tick bite', 'bull\'s eye rash', 'joint pain', 'bull eye rash', 'rash'],
            'Vertigo': ['vertigo', 'spinning', 'balance problems', 'dizzy', 'dizziness'],
            'Eczema': ['eczema', 'itchy skin', 'rash', 'dry skin', 'skin irritation'],
            'Tuberculosis': ['tuberculosis', 'persistent cough', 'night sweats', 'weight loss', 'bloody cough']
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

        # Get top 3 predictions with medical relevance filtering
        top_3_indices = np.argsort(prediction_proba)[-3:][::-1]
        top_3_predictions = []

        for idx in top_3_indices:
            diagnosis_name = self.diagnosis_encoder.inverse_transform([idx])[0]
            confidence = prediction_proba[idx]
            
            # Check if this prediction makes medical sense given the input symptoms
            if self._is_medically_relevant_prediction(diagnosis_name, input_data):
                top_3_predictions.append({
                    'diagnosis': diagnosis_name,
                    'confidence': confidence,
                    'confidence_percent': f"{confidence*100:.1f}%"
                })

        # If we filtered out predictions, get more candidates
        if len(top_3_predictions) < 3:
            # Get top 10 predictions and filter them
            top_10_indices = np.argsort(prediction_proba)[-10:][::-1]
            for idx in top_10_indices:
                if len(top_3_predictions) >= 3:
                    break
                diagnosis_name = self.diagnosis_encoder.inverse_transform([idx])[0]
                confidence = prediction_proba[idx]
                
                # Check if we already have this diagnosis
                if not any(pred['diagnosis'] == diagnosis_name for pred in top_3_predictions):
                    if self._is_medically_relevant_prediction(diagnosis_name, input_data):
                        top_3_predictions.append({
                            'diagnosis': diagnosis_name,
                            'confidence': confidence,
                            'confidence_percent': f"{confidence*100:.1f}%"
                        })

        # Primary diagnosis (validate it too)
        primary_diagnosis = self.diagnosis_encoder.inverse_transform([prediction_id])[0]
        if not self._is_medically_relevant_prediction(primary_diagnosis, input_data) and top_3_predictions:
            # Use the first valid prediction as primary
            primary_diagnosis = top_3_predictions[0]['diagnosis']
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
        
        Uses CSV data for accurate symptom-to-diagnosis matching
        
        Returns comprehensive diagnosis with:
        - Detailed medical description
        - Over-the-counter medications with dosages
        - Recommended home care actions  
        - Severity and duration information
        - When to see a doctor guidelines
        """
        
        # Parse input symptoms
        if isinstance(input_data, str):
            symptoms_text = input_data
            detected_symptoms = self.parse_natural_language_symptoms(input_data)
        else:
            symptoms_text = ', '.join([k.replace('_', ' ') for k, v in input_data.items() if v == 1])
            detected_symptoms = input_data
        
        # Get predictions from CSV data instead of hardcoded patterns
        csv_predictions = self.get_enhanced_predictions(symptoms_text, 3)
        
        # If no CSV predictions, fall back to basic diagnosis
        if not csv_predictions:
            basic_result = self.predict_comprehensive_diagnosis(input_data, patient_conditions)
            primary_diagnosis = basic_result['primary_diagnosis']
            top_3_predictions = basic_result['top_3_predictions']
        else:
            primary_diagnosis = csv_predictions[0]['diagnosis']
            top_3_predictions = [
                {
                    'diagnosis': pred['diagnosis'],
                    'confidence': min(90.0, pred['score'] * 15.0),  # Convert score to realistic confidence
                    'matched_symptoms': pred['matched_symptoms']
                }
                for pred in csv_predictions
            ]
        
        # Get enhanced condition information
        condition_info = self.get_enhanced_condition_info(primary_diagnosis)
        
        # Calculate severity based on symptoms
        active_symptoms = sum(1 for v in detected_symptoms.values() if v == 1)
        if active_symptoms >= 8:
            severity = "Severe"
        elif active_symptoms >= 5:
            severity = "Moderate"  
        elif active_symptoms >= 2:
            severity = "Mild"
        else:
            severity = "Very Mild"
        
        # Create enhanced result with all information
        enhanced_result = {
            # Basic diagnosis info
            'diagnosis': primary_diagnosis,
            'primary_diagnosis': primary_diagnosis,
            'confidence': top_3_predictions[0]['confidence'] if top_3_predictions else 75.0,
            'confidence_percent': f"{top_3_predictions[0]['confidence']:.1f}%" if top_3_predictions else "75.0%",
            'top_3_predictions': top_3_predictions,
            
            # Enhanced condition details
            'description': condition_info.get('description', ''),
            'severity': condition_info.get('severity', severity),
            'duration': condition_info.get('duration', 'Variable'),
            
            # Medications and treatment
            'medications': condition_info.get('medications', []),
            'recommended_actions': condition_info.get('recommended_actions', []),
            'when_to_see_doctor': condition_info.get('when_to_see_doctor', 'If symptoms persist or worsen'),
            
            # Additional info
            'active_symptoms_count': active_symptoms,
            'detected_symptoms': detected_symptoms,
            'patient_conditions': patient_conditions or {},
            
            # System info
            'model_version': f"{self.model_version}-Enhanced-CSV",
            'timestamp': pd.Timestamp.now().isoformat(),
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

    def load_medical_dataset(self):
        """Load the realistic medical dataset for recommended actions and medications"""
        import csv
        csv_path = os.path.join(os.path.dirname(__file__), 'realistic_medical_dataset.csv')
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.medical_dataset = list(reader)
                print(f"✅ Medical dataset loaded: {len(self.medical_dataset)} realistic medical records")
        except Exception as e:
            print(f"❌ Error loading medical dataset: {e}")
            self.medical_dataset = []

    def get_recommended_action_from_dataset(self, diagnosis):
        """Get recommended action for a diagnosis from the medical dataset with improved condition mapping"""
        if not hasattr(self, 'medical_dataset') or not self.medical_dataset:
            print(f"❌ No medical_dataset available for diagnosis: {diagnosis}")
            return None
        
        print(f"🔍 Looking up recommended action for: '{diagnosis}' (dataset size: {len(self.medical_dataset)})")
        print(f"🔍 Available conditions in dataset: {[record.get('diagnosis', '') for record in self.medical_dataset[:5]]}")  # Show first 5
        
        # Enhanced condition mapping for better integration
        condition_mappings = {
            'seasonal allergies': 'allergic rhinitis',
            'allergies': 'allergic rhinitis',
            'allergy': 'allergic rhinitis',
            'hay fever': 'allergic rhinitis',
            'heart condition': 'hypertension',
            'heart attack': 'hypertension',  # Emergency -> follow up care
            'kidney stones': 'migraine',  # Similar pain management approach
            'gastroenteritis': 'food poisoning',
            'strep throat': 'tonsillitis', 
            'anxiety disorder': 'tension headache',  # Similar stress-related management
            'anxiety': 'tension headache',
            'depression': 'tension headache',  # Similar supportive care approach
            'severe sinus infection': 'sinusitis',
            'skin allergy': 'allergic rhinitis',
            'stomach flu': 'food poisoning',
            'ear infection': 'sinusitis',  # Similar approach for infections
            'upper respiratory infection': 'common cold',
            'viral infection': 'common cold',
            'tuberculosis': 'pneumonia',  # Similar respiratory infection approach
            'eczema': 'allergic rhinitis',  # Similar allergic/inflammatory approach
            'conjunctivitis': 'sinusitis',  # Similar infection management
            'laryngitis': 'tonsillitis',  # Similar throat/upper respiratory approach
            'whooping cough': 'bronchitis',  # Similar respiratory approach
            'appendicitis': 'gastritis',  # Similar abdominal pain management principles
            'arthritis': 'migraine',  # Similar pain management approach
            'back pain': 'migraine',  # Similar pain management
            'osteoarthritis': 'migraine',  # Similar pain management
            'gout': 'migraine',  # Similar pain management
            'anemia': 'hypertension',  # Similar monitoring and management
            'diabetes': 'hypertension',  # Similar chronic condition management
            'thyroid disorder': 'hypertension',  # Similar chronic monitoring
            'insomnia': 'tension headache',  # Similar stress/lifestyle management
            'panic attack': 'tension headache',  # Similar anxiety management
            'chronic fatigue': 'tension headache',  # Similar symptom management
            'constipation': 'gastritis',  # Similar digestive management
            'diarrhea': 'food poisoning',  # Similar digestive management
            'dehydration': 'flu',  # Similar supportive care
            'fever': 'flu',  # Similar symptomatic treatment
            'hemorrhoids': 'gastritis',  # Similar supportive care approach
            'heat exhaustion': 'flu',  # Similar rest and hydration approach
            'hypoglycemia': 'hypertension',  # Similar monitoring approach
            'hypertension crisis': 'hypertension',
            'lyme disease': 'flu',  # Similar systemic symptoms approach
            'malaria': 'flu',  # Similar fever and systemic symptoms
            'dengue': 'flu',  # Similar viral fever approach
            'pregnancy': 'gastritis',  # Similar supportive care approach
            'severe infection': 'pneumonia',  # Similar serious infection approach
            'uti': 'sinusitis',  # Similar infection management
            'urinary tract infection': 'sinusitis',  # Similar infection management
            'vertigo': 'migraine',  # Similar symptom management
            'covid variant': 'covid-19',
            'gerd': 'acid reflux'
        }
        
        diagnosis_lower = diagnosis.lower().strip()
        
        # Try exact match first
        for record in self.medical_dataset:
            record_diagnosis = record.get('diagnosis', '').lower().strip()
            if record_diagnosis == diagnosis_lower:
                action = record.get('recommended_action', '').strip()
                if action and action != 'nan':
                    print(f"✅ Found exact match: '{diagnosis}' -> '{action[:50]}...'")
                    return action
        
        # Try condition mapping
        if diagnosis_lower in condition_mappings:
            mapped_condition = condition_mappings[diagnosis_lower]
            print(f"🔄 Trying condition mapping: '{diagnosis}' -> '{mapped_condition}'")
            for record in self.medical_dataset:
                if record.get('diagnosis', '').lower().strip() == mapped_condition:
                    action = record.get('recommended_action', '').strip()
                    if action and action != 'nan':
                        print(f"✅ Found mapped match: '{diagnosis}' -> '{mapped_condition}' -> '{action[:50]}...'")
                        return f"{action} (Treatment approach for {diagnosis})"
        
        # Try partial match for similar conditions
        print(f"⚠️ No exact or mapped match for '{diagnosis}', trying partial matches...")
        for record in self.medical_dataset:
            record_diagnosis = record.get('diagnosis', '').lower().strip()
            if diagnosis_lower in record_diagnosis or record_diagnosis in diagnosis_lower:
                action = record.get('recommended_action', '').strip()
                if action and action != 'nan':
                    print(f"⚠️ Found partial match: '{diagnosis}' matched with '{record_diagnosis}' -> '{action[:50]}...'")
                    return action
        
        # Fallback recommendations based on condition type
        if any(word in diagnosis_lower for word in ['allergy', 'allergic']):
            return "Identify and avoid allergens. Use antihistamines as needed. Consult healthcare provider if symptoms persist."
        elif any(word in diagnosis_lower for word in ['infection', 'bacterial', 'viral']):
            return "Rest, stay hydrated, and monitor symptoms. Seek medical attention if condition worsens."
        elif any(word in diagnosis_lower for word in ['pain', 'ache', 'headache']):
            return "Apply appropriate pain relief measures. Rest and avoid triggers. Consult healthcare provider if severe."
        else:
            return f"Consult healthcare provider for proper evaluation and treatment of {diagnosis}."

    def get_medications_from_dataset(self, diagnosis, age_group='adult'):
        """Get medications for a diagnosis from the medical dataset with improved condition mapping"""
        if not hasattr(self, 'medical_dataset') or not self.medical_dataset:
            return []
        
        # Enhanced condition mapping (same as in get_recommended_action_from_dataset)
        condition_mappings = {
            'seasonal allergies': 'allergic rhinitis',
            'allergies': 'allergic rhinitis',
            'allergy': 'allergic rhinitis',
            'hay fever': 'allergic rhinitis',
            'heart condition': 'hypertension',
            'heart attack': 'hypertension',  # Emergency -> follow up care
            'kidney stones': 'migraine',  # Similar pain management approach
            'gastroenteritis': 'food poisoning',
            'strep throat': 'tonsillitis', 
            'anxiety disorder': 'tension headache',  # Similar stress-related management
            'anxiety': 'tension headache',
            'depression': 'tension headache',  # Similar supportive care approach
            'severe sinus infection': 'sinusitis',
            'skin allergy': 'allergic rhinitis',
            'stomach flu': 'food poisoning',
            'ear infection': 'sinusitis',  # Similar approach for infections
            'upper respiratory infection': 'common cold',
            'viral infection': 'common cold',
            'tuberculosis': 'pneumonia',  # Similar respiratory infection approach
            'eczema': 'allergic rhinitis',  # Similar allergic/inflammatory approach
            'conjunctivitis': 'sinusitis',  # Similar infection management
            'laryngitis': 'tonsillitis',  # Similar throat/upper respiratory approach
            'whooping cough': 'bronchitis',  # Similar respiratory approach
            'appendicitis': 'gastritis',  # Similar abdominal pain management principles
            'arthritis': 'migraine',  # Similar pain management approach
            'back pain': 'migraine',  # Similar pain management
            'osteoarthritis': 'migraine',  # Similar pain management
            'gout': 'migraine',  # Similar pain management
            'anemia': 'hypertension',  # Similar monitoring and management
            'diabetes': 'hypertension',  # Similar chronic condition management
            'thyroid disorder': 'hypertension',  # Similar chronic monitoring
            'insomnia': 'tension headache',  # Similar stress/lifestyle management
            'panic attack': 'tension headache',  # Similar anxiety management
            'chronic fatigue': 'tension headache',  # Similar symptom management
            'constipation': 'gastritis',  # Similar digestive management
            'diarrhea': 'food poisoning',  # Similar digestive management
            'dehydration': 'flu',  # Similar supportive care
            'fever': 'flu',  # Similar symptomatic treatment
            'hemorrhoids': 'gastritis',  # Similar supportive care approach
            'heat exhaustion': 'flu',  # Similar rest and hydration approach
            'hypoglycemia': 'hypertension',  # Similar monitoring approach
            'hypertension crisis': 'hypertension',
            'lyme disease': 'flu',  # Similar systemic symptoms approach
            'malaria': 'flu',  # Similar fever and systemic symptoms
            'dengue': 'flu',  # Similar viral fever approach
            'pregnancy': 'gastritis',  # Similar supportive care approach
            'severe infection': 'pneumonia',  # Similar serious infection approach
            'uti': 'sinusitis',  # Similar infection management
            'urinary tract infection': 'sinusitis',  # Similar infection management
            'vertigo': 'migraine',  # Similar symptom management
            'covid variant': 'covid-19',
            'gerd': 'acid reflux'
        }
        
        diagnosis_lower = diagnosis.lower().strip()
        medications = []
        
        def extract_medication_info(record):
            medicine = record.get('medicine', '').strip()
            adult_dose = record.get('adult_dose', '').strip()
            child_dose = record.get('child_dose', '').strip()
            max_daily = record.get('max_daily_dose', '').strip()
            notes = record.get('notes', '').strip()
            
            if medicine:
                medication_info = f"• {medicine}"
                
                # Add dosage information
                if age_group == 'child' and child_dose:
                    medication_info += f"\n  Dosage: {child_dose}"
                elif adult_dose:
                    medication_info += f"\n  Dosage: {adult_dose}"
                
                # Add maximum daily dose
                if max_daily:
                    medication_info += f"\n  Maximum daily: {max_daily}"
                
                # Add notes
                if notes:
                    medication_info += f"\n  Note: {notes}"
                
                medications.append(medication_info)
        
        # Try exact match first
        for record in self.medical_dataset:
            if record.get('diagnosis', '').lower().strip() == diagnosis_lower:
                extract_medication_info(record)
        
        # Try condition mapping if no exact match
        if not medications and diagnosis_lower in condition_mappings:
            mapped_condition = condition_mappings[diagnosis_lower]
            for record in self.medical_dataset:
                if record.get('diagnosis', '').lower().strip() == mapped_condition:
                    extract_medication_info(record)
        
        # Try partial match if still no results
        if not medications:
            for record in self.medical_dataset:
                record_diagnosis = record.get('diagnosis', '').lower().strip()
                if diagnosis_lower in record_diagnosis or record_diagnosis in diagnosis_lower:
                    extract_medication_info(record)
        
        return medications

    def load_condition_reasons(self):
        """Load condition reasons from the mapping CSV"""
        import csv
        csv_path = os.path.join(os.path.dirname(__file__), 'condition_reason_mapping_clean.csv')
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.condition_reasons = {}
                for row in reader:
                    condition_name = row['condition_name'].strip()
                    reason = row['reason'].strip()
                    self.condition_reasons[condition_name.lower()] = reason
                print(f"✅ Condition reasons loaded: {len(self.condition_reasons)} conditions")
        except Exception as e:
            print(f"❌ Error loading condition reasons: {e}")
            self.condition_reasons = {}

    def load_enhanced_diagnosis_dataset(self):
        """Load the enhanced diagnosis dataset for condition predictions"""
        import csv
        csv_path = os.path.join(os.path.dirname(__file__), 'final_enhanced_dataset_corrected.csv')
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.enhanced_diagnosis_dataset = list(reader)
                
                # Get unique diagnoses for better prediction variety
                unique_diagnoses = set()
                for row in self.enhanced_diagnosis_dataset:
                    diagnosis = row.get('diagnosis', '').strip()
                    if diagnosis:
                        unique_diagnoses.add(diagnosis)
                
                self.available_diagnoses = list(unique_diagnoses)
                print(f"✅ Enhanced diagnosis dataset loaded: {len(self.enhanced_diagnosis_dataset)} records, {len(self.available_diagnoses)} unique diagnoses")
        except Exception as e:
            print(f"❌ Error loading enhanced diagnosis dataset: {e}")
            self.enhanced_diagnosis_dataset = []
            self.available_diagnoses = []

    def get_condition_reason(self, diagnosis):
        """Get the reason explanation for a specific diagnosis"""
        if not hasattr(self, 'condition_reasons') or not self.condition_reasons:
            return f"Medical condition that commonly presents with the reported symptom pattern."
        
        # Try exact match first
        diagnosis_lower = diagnosis.lower().strip()
        if diagnosis_lower in self.condition_reasons:
            return self.condition_reasons[diagnosis_lower]
        
        # Try partial matching for similar conditions
        for condition, reason in self.condition_reasons.items():
            if diagnosis_lower in condition or condition in diagnosis_lower:
                return reason
        
        # Default fallback
        return f"Medical condition that commonly presents with the reported symptom pattern based on clinical literature."

    def get_enhanced_predictions(self, symptoms_text, num_predictions=3):
        """Get enhanced predictions from the enhanced diagnosis dataset using CSV data"""
        if not hasattr(self, 'enhanced_diagnosis_dataset') or not self.enhanced_diagnosis_dataset:
            return []
        
        # Parse symptoms from text
        symptoms_lower = symptoms_text.lower()
        detected_symptoms = self.parse_natural_language_symptoms(symptoms_text)
        
        # Calculate match scores for each unique diagnosis
        diagnosis_scores = {}
        diagnosis_symptom_matches = {}
        
        for row in self.enhanced_diagnosis_dataset:
            diagnosis = row.get('diagnosis', '').strip()
            if not diagnosis:
                continue
                
            score = 0
            matched_symptoms = []
            
            # Check each symptom column in the CSV
            for symptom_col, symptom_value in row.items():
                if symptom_col in ['diagnosis'] or not symptom_value:
                    continue
                
                # Convert symptom column name to match our detected symptoms
                symptom_key = symptom_col.replace(' ', '_').lower()
                
                # If this symptom is present in the CSV row (value = 1) and user mentioned it
                if str(symptom_value).strip() == '1' and detected_symptoms.get(symptom_key, 0) == 1:
                    score += 1
                    matched_symptoms.append(symptom_col.replace('_', ' ').title())
            
            # Only include diagnoses that have at least one symptom match
            if score > 0:
                if diagnosis not in diagnosis_scores or score > diagnosis_scores[diagnosis]:
                    diagnosis_scores[diagnosis] = score
                    diagnosis_symptom_matches[diagnosis] = matched_symptoms
        
        # Sort by score and get top predictions
        sorted_diagnoses = sorted(diagnosis_scores.items(), key=lambda x: x[1], reverse=True)
        
        predictions = []
        for i, (diagnosis, score) in enumerate(sorted_diagnoses[:num_predictions]):
            predictions.append({
                'diagnosis': diagnosis,
                'score': score,
                'matched_symptoms': diagnosis_symptom_matches.get(diagnosis, []),
                'rank': i + 1
            })
        
        return predictions

# Example usage

    def format_diagnosis_response(self, result, symptoms):
        """Format diagnosis response for 4-slide slideshow structure"""
        
        # Extract information from the result dict
        diagnosis = result.get('primary_diagnosis', 'Unknown')
        confidence = result.get('confidence_percent', 0.0)
        alternatives = result.get('alternative_conditions', [])
        
        # Format symptoms list using detected/parsed symptoms instead of raw input
        detected_symptoms = result.get('detected_symptoms', {})
        if detected_symptoms:
            # Use only the symptoms that were actually detected (value = 1)
            symptoms_list = [f"• {symptom.replace('_', ' ').title()}" 
                           for symptom, value in detected_symptoms.items() 
                           if value == 1]
        elif isinstance(symptoms, str):
            # Fallback: Split by commas and clean up
            symptoms_list = [f"• {s.strip().title()}" for s in symptoms.split(',') if s.strip()]
        elif isinstance(symptoms, list):
            symptoms_list = [f"• {s.replace('_', ' ').title()}" for s in symptoms]
        else:
            symptoms_list = ["• No specific symptoms detected"]
        
        # Get recommended action from training dataset
        recommended_action = self.get_recommended_action_from_dataset(diagnosis)
        if not recommended_action:
            recommended_action = "Consult with a healthcare professional for proper evaluation and treatment."
        
        # Format possible conditions with descriptions using top 3 predictions
        conditions_list = []
        top_3_predictions = result.get('top_3_predictions', [])
        
        if top_3_predictions:
            for i, prediction in enumerate(top_3_predictions[:3]):
                diag_name = prediction.get('diagnosis', '').replace('_', ' ').title()
                confidence_pct = prediction.get('confidence_percent', '0%')
                desc = f"Confidence: {confidence_pct} - Medical condition requiring professional evaluation."
                
                conditions_list.append({
                    'name': diag_name,
                    'description': desc
                })
        else:
            # Fallback to old method if top_3_predictions not available
            all_diagnoses = [{'diagnosis': diagnosis, 'likelihood': confidence}]
            all_diagnoses.extend(alternatives[:2])  # Take top 2 alternatives
            
            for i, diag_item in enumerate(all_diagnoses[:3], 1):
                diag_name = diag_item.get('diagnosis', '').replace('_', ' ').title()
                desc = f"Medical condition requiring professional evaluation."
                
                conditions_list.append({
                    'name': diag_name,
                    'description': desc
                })
        
        # Ensure we have at least 3 conditions
        while len(conditions_list) < 3:
            conditions_list.append({
                'name': 'Unknown Condition', 
                'description': 'Medical condition requiring professional evaluation.'
            })
        
        # Get medications from training dataset
        medications = self.get_medications_from_dataset(diagnosis, 'adult')
        if not medications:
            medications = [f"• Consult healthcare provider for appropriate medication recommendations for {diagnosis}"]
        
        # Create structured response for slideshow format
        response_text = f"""**SLIDE_1_SYMPTOMS**
{chr(10).join(symptoms_list)}

**SLIDE_2_CONDITIONS**
1. {conditions_list[0]['name']}

{conditions_list[0]['description']}

2. {conditions_list[1]['name']}

{conditions_list[1]['description']}

3. {conditions_list[2]['name']}

{conditions_list[2]['description']}

**SLIDE_3_RECOMMENDED_ACTION**
{recommended_action}

**SLIDE_4_MEDICATIONS**
{chr(10).join(medications)}"""
        
        return response_text



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
