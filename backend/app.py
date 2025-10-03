
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import os
import csv
import re
import pickle
import numpy as np
from collections import Counter
from datetime import datetime

# Load environment variables
load_dotenv()

# Enhanced AI Diagnosis Engine - ML-powered with CSV data and text understanding
class EnhancedAIEngine:
    def __init__(self):
        self.dataset = []
        self.symptom_columns = []
        self.diagnoses = set()
        self.ml_model = None
        self.encoder = None
        self.features = None
        self.feature_mappings = None
        self.diagnosis_info = {}
        self.load_dataset()
        self.load_ml_components()
        self.load_diagnosis_information()
    
    def load_dataset(self):
        """Load the CSV dataset for diagnosis"""
        csv_path = os.path.join(os.path.dirname(__file__), 'final_enhanced_dataset.csv')
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.dataset = list(reader)
                
                if self.dataset:
                    # Get symptom columns (exclude non-symptom fields)
                    all_columns = set(self.dataset[0].keys())
                    exclude_columns = {'diagnosis', 'duration_days', 'intensity'}
                    self.symptom_columns = list(all_columns - exclude_columns)
                    
                    # Get all unique diagnoses
                    self.diagnoses = set(row['diagnosis'] for row in self.dataset)
                    
                    print(f"✅ AI: Loaded {len(self.dataset)} medical records")
                    print(f"📋 AI: Symptoms tracked: {', '.join(self.symptom_columns[:5])}..." if len(self.symptom_columns) > 5 else f"📋 AI: Symptoms tracked: {', '.join(self.symptom_columns)}")
                    print(f"🏥 AI: Available diagnoses: {len(self.diagnoses)} conditions")
                else:
                    print("⚠️ AI: Dataset is empty")
                    
        except Exception as e:
            print(f"❌ AI: Failed to load dataset: {e}")
            self.dataset = []
            self.symptom_columns = []
            self.diagnoses = set()
    
    def load_ml_components(self):
        """Load ML model, encoder, and features for enhanced diagnosis"""
        try:
            # Try to load the trained ML model
            model_path = os.path.join(os.path.dirname(__file__), 'final_comprehensive_model.pkl')
            encoder_path = os.path.join(os.path.dirname(__file__), 'final_comprehensive_encoder.pkl')
            features_path = os.path.join(os.path.dirname(__file__), 'final_comprehensive_features.pkl')
            mappings_path = os.path.join(os.path.dirname(__file__), 'feature_mappings.pkl')
            
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    self.ml_model = pickle.load(f)
                print("✅ AI: ML model loaded successfully")
            
            if os.path.exists(encoder_path):
                with open(encoder_path, 'rb') as f:
                    self.encoder = pickle.load(f)
                print("✅ AI: Encoder loaded successfully")
            
            if os.path.exists(features_path):
                with open(features_path, 'rb') as f:
                    self.features = pickle.load(f)
                print("✅ AI: Feature set loaded successfully")
            
            # Load feature mappings for proper encoding
            if os.path.exists(mappings_path):
                with open(mappings_path, 'rb') as f:
                    self.feature_mappings = pickle.load(f)
                print("✅ AI: Feature mappings loaded successfully")
            else:
                self.feature_mappings = None
                
            if self.ml_model and self.encoder and self.features and self.feature_mappings:
                print("🧠 AI: Enhanced ML mode activated")
            else:
                print("📊 AI: Using CSV-only mode (ML components not available)")
                
        except Exception as e:
            print(f"⚠️ AI: ML components loading failed: {e}")
            print("📊 AI: Fallback to CSV-only mode")
            self.ml_model = None
            self.encoder = None
            self.features = None
            self.feature_mappings = None
    
    def load_diagnosis_information(self):
        """Load enhanced diagnosis information with descriptions and recommendations"""
        import json
        try:
            diagnosis_info_path = os.path.join(os.path.dirname(__file__), 'diagnosis_information.json')
            if os.path.exists(diagnosis_info_path):
                with open(diagnosis_info_path, 'r', encoding='utf-8') as f:
                    self.diagnosis_info = json.load(f)
                print(f"✅ AI: Loaded detailed information for {len(self.diagnosis_info)} diagnoses")
            else:
                print("📋 AI: Using basic diagnosis information")
                self.diagnosis_info = {}
        except Exception as e:
            print(f"⚠️ AI: Failed to load diagnosis information: {e}")
            self.diagnosis_info = {}
    
    def extract_age_gender_from_text(self, text):
        """Extract age and gender from natural language text using ML-enhanced parsing"""
        age = None
        gender = None
        
        # Convert to lowercase for processing
        text_lower = text.lower()
        
        # Extract age using regex patterns
        age_patterns = [
            r'(?:i am|i\'m|age|aged|years old)\s*(\d{1,3})',
            r'(\d{1,3})\s*(?:years old|year old|yo|y/o)',
            r'(\d{1,3})\s*(?:male|female|m|f)',
            r'age\s*:?\s*(\d{1,3})',
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text_lower)
            if match:
                potential_age = int(match.group(1))
                if 1 <= potential_age <= 120:  # Reasonable age range
                    age = potential_age
                    break
        
        # Extract gender using multiple approaches
        gender_patterns = [
            r'(?:i\'m|i am)\s*(?:a\s*)?(\d+)\s*(?:year\s*old\s*)?(male|female|man|woman|boy|girl)',
            r'(\d+)\s*(?:year\s*old\s*)?(male|female|man|woman|boy|girl)',
            r'(male|female|man|woman|boy|girl)(?:\s*\d+)?',
            r'gender\s*:?\s*(male|female|m|f)'
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, text_lower)
            if match:
                # Get the last captured group that contains gender info
                groups = match.groups()
                gender_text = None
                for group in reversed(groups):
                    if group and group.lower() in ['male', 'female', 'm', 'f', 'man', 'woman', 'boy', 'girl']:
                        gender_text = group.lower()
                        break
                
                if gender_text:
                    if gender_text in ['male', 'm', 'man', 'boy']:
                        gender = 'male'
                    elif gender_text in ['female', 'f', 'woman', 'girl']:
                        gender = 'female'
                    break
        
        # Alternative gender detection from context
        if not gender:
            if any(word in text_lower for word in ['pregnant', 'menstrual', 'period', 'menopause']):
                gender = 'female'
            elif any(word in text_lower for word in ['prostate', 'testicular']):
                gender = 'male'
        
        return age, gender
    
    def convert_age_to_group(self, age):
        """Convert numeric age to age group"""
        if age is None:
            return None
        
        if isinstance(age, str):
            # If it's already an age group string, return as is
            if age.lower() in ['child', 'teen', 'adult', 'senior']:
                return age.lower()
            # Try to convert to number
            try:
                age = int(age)
            except ValueError:
                return None
        
        if isinstance(age, (int, float)):
            age_num = int(age)  # Ensure it's an integer for comparison
            if 0 <= age_num <= 12:
                return 'child'
            elif 13 <= age_num <= 19:
                return 'teen'
            elif 20 <= age_num <= 59:
                return 'adult'
            elif age_num >= 60:
                return 'senior'
        
        return None
    
    def convert_age_to_numeric(self, age):
        """Convert age group or string to numeric age"""
        if age is None:
            return None
            
        if isinstance(age, (int, float)):
            return int(age)
            
        if isinstance(age, str):
            age_lower = age.lower()
            if 'child' in age_lower:
                return 8
            elif 'teen' in age_lower:
                return 16
            elif 'adult' in age_lower:
                return 35
            elif 'senior' in age_lower:
                return 70
            else:
                try:
                    return int(age)
                except ValueError:
                    return None
        
        return None
    
    def extract_duration_from_text(self, text):
        """Extract duration information from text like 'for 3 days', 'since 2 weeks'"""
        import re
        text_lower = text.lower()
        
        # Pattern for duration extraction
        duration_patterns = [
            r'for\s+(\d+)\s+(day|days|week|weeks|month|months)',
            r'(\d+)\s+(day|days|week|weeks|month|months)\s+ago',
            r'since\s+(\d+)\s+(day|days|week|weeks|month|months)',
            r'last\s+(\d+)\s+(day|days|week|weeks|month|months)',
            r'past\s+(\d+)\s+(day|days|week|weeks|month|months)',
            r'(\d+)\s+(day|days|week|weeks|month|months)'
        ]
        
        extracted_duration = None
        duration_context = {}
        
        for pattern in duration_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                number = int(match.group(1))
                unit = match.group(2)
                
                # Convert to days
                if 'week' in unit:
                    days = number * 7
                elif 'month' in unit:
                    days = number * 30
                else:  # days
                    days = number
                
                # Look for symptom context around the duration
                start = max(0, match.start() - 50)
                end = min(len(text_lower), match.end() + 50)
                context = text_lower[start:end]
                
                # Find which symptom this duration refers to
                symptom_keywords = {
                    'headache': ['headache', 'head pain', 'migraine'],
                    'fever': ['fever', 'temperature', 'hot'],
                    'cough': ['cough', 'coughing'],
                    'fatigue': ['tired', 'exhausted', 'fatigue', 'weak'],
                    'shortness_of_breath': ['shortness of breath', 'breathless', 'breathing'],
                    'nausea': ['nausea', 'sick', 'vomiting'],
                    'dizziness': ['dizzy', 'dizziness']
                }
                
                for symptom, keywords in symptom_keywords.items():
                    if any(keyword in context for keyword in keywords):
                        duration_context[symptom] = days
                        break
                
                if not extracted_duration:
                    extracted_duration = days
        
        return extracted_duration, duration_context

    def advanced_symptom_extraction(self, text):
        """Extract symptoms from natural language using ML-enhanced understanding"""
        symptoms = []
        user_mentioned_terms = []  # Keep track of original user terms
        text_lower = text.lower()
        
        # Extract duration information
        duration, duration_context = self.extract_duration_from_text(text)
        
        # Enhanced symptom mappings with context - improved shortness of breath detection
        symptom_mappings = {
            'fever': ['fever', 'high temperature', 'temp', 'hot', 'burning up', 'feverish'],
            'cough': ['cough', 'coughing', 'hacking', 'dry cough', 'wet cough', 'persistent cough'],
            'fatigue': ['tired', 'exhausted', 'fatigue', 'weak', 'weakness', 'lethargic', 'drowsy', 'sleepy'],
            'shortness_of_breath': [
                'shortness of breath', 'short of breath', 'breathless', 'breathing problems', 
                'difficulty breathing', 'cant breathe', 'can\'t breathe', 'cannot breathe',
                'winded', 'out of breath', 'trouble breathing', 'hard to breathe',
                'breathing difficulty', 'respiratory problems', 'breath shortness'
            ],
            'headache': ['headache', 'head pain', 'migraine', 'head hurts', 'head ache', 'throbbing head'],
            'sore_throat': ['sore throat', 'throat pain', 'throat hurts', 'scratchy throat', 'throat ache'],
            'nausea': ['nausea', 'sick', 'vomiting', 'throw up', 'queasy', 'stomach sick', 'feel sick'],
            'dizziness': ['dizzy', 'dizziness', 'light headed', 'lightheaded', 'vertigo', 'spinning'],
            'body_aches': ['body aches', 'muscle pain', 'aches', 'sore muscles', 'body pain', 'joint pain'],
            'runny_nose': ['runny nose', 'stuffy nose', 'nasal congestion', 'blocked nose', 'congested'],
            'chest_pain': ['chest pain', 'chest hurts', 'tight chest', 'chest pressure'],
            'diarrhea': ['diarrhea', 'loose stools', 'upset stomach', 'stomach problems', 'bowel problems'],
            'loss_of_taste': ['loss of taste', 'cant taste', 'no taste', 'taste gone'],
            'loss_of_smell': ['loss of smell', 'cant smell', 'no smell', 'smell gone']
        }
        
        # Check each symptom category and capture user's original terms
        for symptom_key, keywords in symptom_mappings.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if symptom_key not in symptoms:
                        symptoms.append(symptom_key)
                        # Capitalize the user's original term properly
                        user_mentioned_terms.append(keyword.title())
                    break
        
        # Additional context-based detection
        pain_locations = {
            'head': 'headache',
            'throat': 'sore_throat', 
            'chest': 'chest_pain',
            'stomach': 'nausea'
        }
        
        for location, symptom in pain_locations.items():
            pain_phrase = f"{location} pain"
            hurts_phrase = f"{location} hurts"
            if pain_phrase in text_lower:
                if symptom not in symptoms:
                    symptoms.append(symptom)
                    user_mentioned_terms.append(pain_phrase.title())
            elif hurts_phrase in text_lower:
                if symptom not in symptoms:
                    symptoms.append(symptom)
                    user_mentioned_terms.append(hurts_phrase.title())
        
        # Return symptoms with duration context and user's original terms
        return {
            'symptoms': symptoms,
            'user_mentioned_terms': user_mentioned_terms,
            'duration': duration,
            'duration_context': duration_context
        }
    
    def normalize_symptom_name(self, symptom):
        """Normalize user symptom input to match CSV columns"""
        symptom = symptom.lower().strip()
        
        # Enhanced symptom mappings - improved shortness of breath detection
        mappings = {
            'fever': 'fever', 'temperature': 'fever', 'high temperature': 'fever',
            'cough': 'cough', 'coughing': 'cough',
            'tired': 'fatigue', 'tiredness': 'fatigue', 'exhausted': 'fatigue', 'fatigue': 'fatigue',
            'breathless': 'shortness_of_breath', 'short of breath': 'shortness_of_breath',
            'shortness of breath': 'shortness_of_breath', 'breathing problems': 'shortness_of_breath', 
            'difficulty breathing': 'shortness_of_breath', 'shortness_of_breath': 'shortness_of_breath',
            'cant breathe': 'shortness_of_breath', 'can\'t breathe': 'shortness_of_breath',
            'cannot breathe': 'shortness_of_breath', 'out of breath': 'shortness_of_breath',
            'trouble breathing': 'shortness_of_breath', 'hard to breathe': 'shortness_of_breath',
            'head pain': 'headache', 'headache': 'headache', 'migraine': 'headache',
            'throat pain': 'sore_throat', 'sore throat': 'sore_throat', 'sore_throat': 'sore_throat',
            'nausea': 'nausea', 'sick': 'nausea', 'vomiting': 'nausea',
            'dizzy': 'dizziness', 'dizziness': 'dizziness', 'light headed': 'dizziness', 'lightheaded': 'dizziness',
            'body pain': 'body_aches', 'body aches': 'body_aches', 'muscle pain': 'body_aches',
            'aches': 'body_aches', 'body_aches': 'body_aches',
            'runny nose': 'runny_nose', 'stuffy nose': 'runny_nose', 'nasal congestion': 'runny_nose',
            'runny_nose': 'runny_nose',
            'chest pain': 'chest_pain', 'chest_pain': 'chest_pain',
            'diarrhea': 'diarrhea', 'loose stools': 'diarrhea', 'upset stomach': 'diarrhea',
            'loss of taste': 'loss_of_taste', 'loss_of_taste': 'loss_of_taste', 'no taste': 'loss_of_taste',
            'loss of smell': 'loss_of_smell', 'loss_of_smell': 'loss_of_smell', 'no smell': 'loss_of_smell'
        }
        
        return mappings.get(symptom, None)
    
    def diagnose(self, input_text, symptoms=None, age=None, gender=None):
        """Enhanced diagnosis using ML + CSV data with text understanding"""
        if not self.dataset:
            return {
                'diagnosis': 'Unable to diagnose',
                'confidence': 0.0,
                'error': 'Medical dataset not available'
            }
        
        # Extract age and gender from input text if not provided
        if input_text and (age is None or gender is None):
            extracted_age, extracted_gender = self.extract_age_gender_from_text(input_text)
            age = age or extracted_age
            gender = gender or extracted_gender
        
        # Convert age to age group if it's numeric
        age_group = self.convert_age_to_group(age) if age is not None else None
        
        # Extract symptoms from text if not provided as array
        duration = None
        duration_context = {}
        
        # Always use advanced_symptom_extraction for text input
        user_original_terms = []
        if input_text:
            symptom_data = self.advanced_symptom_extraction(input_text)
            extracted_symptoms = symptom_data['symptoms']
            user_original_terms = symptom_data.get('user_mentioned_terms', [])
            duration = symptom_data.get('duration')
            duration_context = symptom_data.get('duration_context', {})
            print(f"🔍 Extracted symptoms from text: {extracted_symptoms}")
            print(f"🔍 User's original terms: {user_original_terms}")
            
            # If symptoms was provided as a list, merge with extracted symptoms
            if symptoms and isinstance(symptoms, list):
                all_symptoms = list(set(symptoms + extracted_symptoms))
                symptoms = all_symptoms
            else:
                # Use extracted symptoms
                symptoms = extracted_symptoms
        
        # Process symptoms for both CSV and ML approaches
        matched_symptoms = []
        symptom_vector = {col: False for col in self.symptom_columns}
        
        # Normalize and match symptoms
        if symptoms:
            print(f"🔍 Processing symptoms: {symptoms}")
            for symptom in symptoms:
                if isinstance(symptom, str):
                    normalized = self.normalize_symptom_name(symptom)
                    print(f"   '{symptom}' -> '{normalized}' (in dataset: {normalized in symptom_vector if normalized else False})")
                    if normalized and normalized in symptom_vector:
                        symptom_vector[normalized] = True
                        matched_symptoms.append(normalized)
                else:
                    # Symptom is already normalized
                    if symptom in symptom_vector:
                        symptom_vector[symptom] = True
                        matched_symptoms.append(symptom)
            print(f"✅ Final matched symptoms: {matched_symptoms}")
        
        if not matched_symptoms:
            # If no exact matches, find the most common conditions in dataset
            common_conditions = Counter(row['diagnosis'] for row in self.dataset).most_common(3)
            top_condition = common_conditions[0][0] if common_conditions else 'General Medical Condition'
            
            return {
                'diagnosis': top_condition,
                'confidence': 0.2,
                'message': 'Symptoms require professional medical evaluation',
                'available_symptoms': self.symptom_columns[:10],
                'extracted_info': {'age': age, 'gender': gender}
            }
        
        # Try ML prediction first if available
        ml_result = None
        if self.ml_model and self.encoder and self.features:
            try:
                # Prepare ML prediction kwargs with duration information
                ml_kwargs = {}
                if duration:
                    ml_kwargs['duration_days'] = duration
                
                # Add specific symptom durations if available
                for symptom, days in duration_context.items():
                    if symptom in matched_symptoms:
                        ml_kwargs['duration_days'] = days  # Use specific duration for that symptom
                        break
                
                ml_result = self.ml_predict(matched_symptoms, age_group or age, gender, **ml_kwargs)
            except Exception as e:
                print(f"ML prediction failed: {e}")
        
        # CSV-based approach as backup or primary
        csv_result = self.csv_diagnose(matched_symptoms, age_group or age, gender)
        
        # Combine ML and CSV results for better accuracy
        final_result = self.combine_predictions(ml_result, csv_result, matched_symptoms, age_group or age, gender, user_original_terms)
        
        return final_result
    
    def ml_predict(self, symptoms, age=None, gender=None, **kwargs):
        """Use ML model for prediction with all 26 features"""
        if not self.ml_model or not self.encoder or not self.features or not self.feature_mappings:
            return None
        
        try:
            # Get feature mappings
            symptom_columns = self.feature_mappings['symptom_columns']
            intensity_map = self.feature_mappings['intensity_map']
            age_group_map = self.feature_mappings['age_group_map']
            gender_map = self.feature_mappings['gender_map']
            conditions_map = self.feature_mappings['conditions_map']
            exposure_map = self.feature_mappings['exposure_map']
            onset_map = self.feature_mappings['onset_map']
            progression_map = self.feature_mappings['progression_map']
            treatment_map = self.feature_mappings['treatment_map']
            risk_map = self.feature_mappings['risk_map']
            
            # Create feature vector matching the trained model
            feature_vector = []
            
            # Add symptom features (14 binary features)
            for symptom in symptom_columns:
                feature_vector.append(1 if symptom in symptoms else 0)
            
            # Add duration_days (default 7 if not provided)
            duration = kwargs.get('duration_days', 7)
            feature_vector.append(float(duration))
            
            # Add intensity (default moderate=2 if not provided)
            intensity = kwargs.get('intensity', 'moderate')
            feature_vector.append(intensity_map.get(intensity, 2))
            
            # Add age_group (convert age to age group if numeric)
            age_group = self.convert_age_to_group(age) if age is not None else 'adult'
            feature_vector.append(age_group_map.get(age_group, 3))
            
            # Add gender
            feature_vector.append(gender_map.get(gender, 3))
            
            # Add underlying_conditions (default none=0)
            conditions = kwargs.get('underlying_conditions', 'none')
            feature_vector.append(conditions_map.get(conditions, 0))
            
            # Add recent_exposure (default none=0)
            exposure = kwargs.get('recent_exposure', 'none')
            feature_vector.append(exposure_map.get(exposure, 0))
            
            # Add symptom_onset (default gradual=1)
            onset = kwargs.get('symptom_onset', 'gradual')
            feature_vector.append(onset_map.get(onset, 1))
            
            # Add progression (default stable=2)
            progression = kwargs.get('progression', 'stable')
            feature_vector.append(progression_map.get(progression, 2))
            
            # Add treatment_received (default none=0)
            treatment = kwargs.get('treatment_received', 'none')
            feature_vector.append(treatment_map.get(treatment, 0))
            
            # Add hospital_visit_required (default no=0)
            hospital_visit = kwargs.get('hospital_visit_required', 'no')
            feature_vector.append(1 if hospital_visit == 'yes' else 0)
            
            # Add recovery_time_days (default 14)
            recovery_time = kwargs.get('recovery_time_days', 14)
            feature_vector.append(float(recovery_time))
            
            # Add complications_risk (default medium=2)
            risk = kwargs.get('complications_risk', 'medium')
            feature_vector.append(risk_map.get(risk, 2))
            
            # Make prediction
            feature_vector = np.array(feature_vector).reshape(1, -1)
            
            # Verify feature count (should be 26 for the comprehensive model)
            expected_features = 26
            if len(feature_vector[0]) != expected_features:
                print(f"Feature count mismatch: got {len(feature_vector[0])}, expected {expected_features}")
                return None
            
            # Get prediction probabilities
            probabilities = self.ml_model.predict_proba(feature_vector)[0]
            prediction = self.ml_model.predict(feature_vector)[0]
            
            # Get diagnosis name
            diagnosis = self.encoder.inverse_transform([prediction])[0]
            confidence = max(probabilities)
            
            # Get alternative predictions
            classes = self.ml_model.classes_
            pred_probs = list(zip(classes, probabilities))
            pred_probs.sort(key=lambda x: x[1], reverse=True)
            
            return {
                'method': 'Enhanced ML Model',
                'diagnosis': diagnosis,
                'confidence': float(confidence),
                'feature_count': len(feature_vector[0]),
                'alternatives': [
                    {'diagnosis': self.encoder.inverse_transform([diag])[0], 'probability': float(prob)}
                    for diag, prob in pred_probs[1:4]  # Top 3 alternatives
                ]
            }
            
        except Exception as e:
            print(f"ML prediction error: {e}")
            return None
    
    def csv_diagnose(self, matched_symptoms, age=None, gender=None):
        """CSV-based diagnosis with age/gender consideration"""
        scores = []
        
        # Convert age to age group if it's numeric
        age_group = self.convert_age_to_group(age) if age is not None else None
        
        for row in self.dataset:
            # Calculate Jaccard similarity
            user_symptoms = set(matched_symptoms)
            row_symptoms = set([col for col in self.symptom_columns if row.get(col) == '1'])
            
            if len(user_symptoms) == 0 or len(row_symptoms) == 0:
                similarity = 0
            else:
                intersection = len(user_symptoms.intersection(row_symptoms))
                union = len(user_symptoms.union(row_symptoms))
                similarity = intersection / union if union > 0 else 0
            
            # Adjust similarity based on age group and gender if available
            demographic_bonus = 0
            
            # Age group matching bonus
            if age_group is not None and row.get('age_group'):
                if age_group == row['age_group']:
                    demographic_bonus += 0.15  # Higher bonus for exact age group match
            
            # Gender matching bonus
            if gender is not None and row.get('gender'):
                if gender.lower() == row['gender'].lower():
                    demographic_bonus += 0.1  # Bonus for gender match
            
            # Age-specific condition adjustments
            if age_group:
                if age_group == 'child' and row['diagnosis'] in ['Common Cold', 'Flu', 'Allergies']:
                    demographic_bonus += 0.05
                elif age_group == 'senior' and row['diagnosis'] in ['Pneumonia', 'Heart Condition', 'Hypertension']:
                    demographic_bonus += 0.05
                elif age_group == 'adult' and row['diagnosis'] in ['Migraine', 'Anxiety', 'Gastritis']:
                    demographic_bonus += 0.05
                elif age_group == 'teen' and row['diagnosis'] in ['Anxiety', 'Allergies', 'Acne']:
                    demographic_bonus += 0.05
            
            final_similarity = min(similarity + demographic_bonus, 1.0)
            
            scores.append({
                'similarity': final_similarity,
                'diagnosis': row['diagnosis'],
                'intensity': row.get('intensity', 'moderate'),
                'duration': row.get('duration_days', 'unknown'),
                'age_group': row.get('age_group', 'unknown'),
                'gender': row.get('gender', 'unknown')
            })
        
        # Sort by similarity and calculate weighted diagnosis
        scores.sort(key=lambda x: x['similarity'], reverse=True)
        
        diagnosis_weights = {}
        for match in scores[:20]:  # Top 20 matches
            if match['similarity'] > 0:
                diag = match['diagnosis']
                weight = match['similarity']
                diagnosis_weights[diag] = diagnosis_weights.get(diag, 0) + weight
        
        if not diagnosis_weights:
            return None
        
        best_diagnosis = max(diagnosis_weights.items(), key=lambda x: x[1])
        confidence = min(best_diagnosis[1], 1.0)
        
        # Ensure we have a valid primary diagnosis
        primary_diagnosis = best_diagnosis[0]
        if not primary_diagnosis or primary_diagnosis.strip() == '':
            # Find first non-empty diagnosis as fallback
            for diag, weight in sorted(diagnosis_weights.items(), key=lambda x: x[1], reverse=True):
                if diag and diag.strip():
                    primary_diagnosis = diag
                    confidence = min(weight, 1.0)
                    break
            else:
                primary_diagnosis = 'Unspecified Condition'
                confidence = 0.1
        
        return {
            'method': 'CSV',
            'diagnosis': primary_diagnosis,
            'confidence': confidence,
            'alternatives': [
                {'diagnosis': diag, 'likelihood': weight/best_diagnosis[1]}
                for diag, weight in sorted(diagnosis_weights.items(), key=lambda x: x[1], reverse=True)[1:3]
            ]
        }
    
    def combine_predictions(self, ml_result, csv_result, symptoms, age, gender, user_original_terms=None):
        """Combine ML and CSV predictions for optimal accuracy"""
        if ml_result and csv_result:
            # Both methods available - use weighted combination
            ml_weight = 0.7 if ml_result['confidence'] > 0.8 else 0.5
            csv_weight = 1.0 - ml_weight
            
            # If both agree, increase confidence
            if ml_result['diagnosis'] == csv_result['diagnosis']:
                final_confidence = min(
                    ml_result['confidence'] * ml_weight + csv_result['confidence'] * csv_weight + 0.1,
                    1.0
                )
                diagnosis = ml_result['diagnosis']
                method = 'ML+CSV (Agreement)'
            else:
                # They disagree - use the one with higher confidence
                if ml_result['confidence'] > csv_result['confidence']:
                    diagnosis = ml_result['diagnosis']
                    final_confidence = ml_result['confidence'] * 0.9  # Slightly reduce due to disagreement
                    method = 'ML (Primary)'
                else:
                    diagnosis = csv_result['diagnosis']
                    final_confidence = csv_result['confidence'] * 0.9
                    method = 'CSV (Primary)'
                
                # If primary diagnosis is empty, use best alternative
                if not diagnosis or diagnosis.strip() == '':
                    all_alternatives = []
                    if ml_result.get('alternatives'):
                        all_alternatives.extend([
                            {'diagnosis': alt['diagnosis'], 'likelihood': alt['probability']}
                            for alt in ml_result['alternatives']
                        ])
                    if csv_result.get('alternatives'):
                        all_alternatives.extend(csv_result['alternatives'])
                    
                    if all_alternatives:
                        best_alt = max(all_alternatives, key=lambda x: x.get('likelihood', 0))
                        diagnosis = best_alt['diagnosis']
                        final_confidence = best_alt['likelihood']
                        method += ' (Best Alternative)'
            
            # Combine alternatives
            alternatives = []
            if ml_result.get('alternatives'):
                alternatives.extend([
                    {'diagnosis': alt['diagnosis'], 'likelihood': alt['probability']}
                    for alt in ml_result['alternatives']
                ])
            if csv_result.get('alternatives'):
                alternatives.extend(csv_result['alternatives'])
            
            # Remove duplicates and sort
            alt_dict = {}
            for alt in alternatives:
                if alt['diagnosis'] in alt_dict:
                    alt_dict[alt['diagnosis']] = max(alt_dict[alt['diagnosis']], alt.get('likelihood', alt.get('probability', 0)))
                else:
                    alt_dict[alt['diagnosis']] = alt.get('likelihood', alt.get('probability', 0))
            
            final_alternatives = [
                {'diagnosis': diag, 'likelihood': round(score, 2)}
                for diag, score in sorted(alt_dict.items(), key=lambda x: x[1], reverse=True)[:3]
            ]
            
            # Ensure we have at least 3 alternatives (pad if needed)
            while len(final_alternatives) < 3:
                final_alternatives.append({
                    'diagnosis': f'Condition {len(final_alternatives) + 1}',
                    'likelihood': 0.1
                })
            
        elif ml_result:
            diagnosis = ml_result['diagnosis']
            final_confidence = ml_result['confidence']
            method = 'ML Only'
            final_alternatives = [
                {'diagnosis': alt['diagnosis'], 'likelihood': round(alt['probability'], 2)}
                for alt in ml_result.get('alternatives', [])
            ]
        elif csv_result:
            diagnosis = csv_result['diagnosis']
            final_confidence = csv_result['confidence']
            method = 'CSV Only'
            final_alternatives = csv_result.get('alternatives', [])
            
            # If primary diagnosis is empty but we have alternatives, use the best alternative
            if not diagnosis or diagnosis.strip() == '':
                if final_alternatives:
                    best_alt = max(final_alternatives, key=lambda x: x.get('likelihood', 0))
                    diagnosis = best_alt['diagnosis']
                    final_confidence = best_alt['likelihood']
                    # Remove the used alternative from the list
                    final_alternatives = [alt for alt in final_alternatives if alt['diagnosis'] != diagnosis]
        else:
            return {
                'diagnosis': 'Unable to diagnose',
                'confidence': 0.0,
                'error': 'No prediction method succeeded'
            }
        
        # Get recommendations
        recommendations = self.get_recommendations(diagnosis, final_confidence)
        
        # Add age/gender specific recommendations
        if age is not None or gender is not None:
            # Ensure age is numeric for demographic recommendations
            numeric_age = age
            if isinstance(age, str):
                numeric_age = self.convert_age_to_numeric(age)
            recommendations = self.add_demographic_recommendations(recommendations, diagnosis, numeric_age, gender)
        
        # Format response in the requested style
        formatted_response = self.format_diagnosis_response(
            diagnosis, 
            final_confidence, 
            symptoms, 
            final_alternatives, 
            recommendations, 
            age, 
            gender,
            method,
            user_original_terms
        )
        
        return formatted_response
    
    def format_diagnosis_response(self, diagnosis, confidence, symptoms, alternatives, recommendations, age, gender, method='Enhanced AI Analysis', user_original_terms=None):
        """Format diagnosis response for 4-slide slideshow structure"""
        
        # Format symptoms list - prioritize user's original terms
        symptoms_text = ""
        if user_original_terms:
            # Use the user's original mentioned terms
            symptoms_list = [f"• {term.title()}" for term in user_original_terms]
        elif symptoms:
            # Fallback to normalized symptoms if no original terms available
            symptoms_list = [f"• {symptom.replace('_', ' ').title()}" for symptom in symptoms]
        else:
            symptoms_list = ["• No specific symptoms detected"]
        
        # Get severity assessment with detailed information
        severity_info = self.get_detailed_severity_assessment(diagnosis, confidence, symptoms)
        
        # Ensure we have exactly 3 diagnoses total (1 primary + 2 alternatives)
        all_diagnoses = [{'diagnosis': diagnosis, 'likelihood': confidence}]
        
        # Add alternatives that are different from primary diagnosis
        unique_alternatives = []
        for alt in alternatives:
            if alt['diagnosis'] != diagnosis and alt['diagnosis'] not in [d['diagnosis'] for d in unique_alternatives]:
                unique_alternatives.append(alt)
                if len(unique_alternatives) >= 2:
                    break
        
        all_diagnoses.extend(unique_alternatives[:2])
        
        # Format possible conditions with detailed descriptions
        conditions_list = []
        valid_diagnoses = []
        
        for diag_item in all_diagnoses:
            diag_name = diag_item.get('diagnosis', '')
            if diag_name and diag_name.strip() and diag_name != 'Unknown Condition':
                valid_diagnoses.append(diag_item)
        
        # Create exactly 3 conditions for the slideshow
        for i, diag_item in enumerate(valid_diagnoses[:3], 1):
            diag_name = diag_item.get('diagnosis', '').replace('_', ' ').title()
            desc = self.get_condition_description(diag_item.get('diagnosis', ''))
            
            if not desc:
                desc = "Medical condition requiring professional evaluation."
            
            # Clean description of markdown asterisks
            clean_desc = desc.replace('*', '').strip()
            conditions_list.append({
                'name': diag_name,
                'description': clean_desc
            })
        
        # Ensure we have at least 3 conditions (fill with generic if needed)
        while len(conditions_list) < 3:
            conditions_list.append({
                'name': 'Unknown Condition', 
                'description': 'Medical condition requiring professional evaluation.'
            })
        
        # Format recommendations with detailed actions
        action_recommendations = self.format_detailed_recommendations(diagnosis, confidence, symptoms)
        
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

**SLIDE_3_SEVERITY**
{severity_info}

**SLIDE_4_RECOMMENDATIONS**
{action_recommendations}"""

        # Determine the proper method name for display
        if method == 'ML Only':
            display_method = 'Enhanced ML Model'
        elif 'ML+CSV' in method:
            display_method = 'Enhanced ML Model (Verified)'
        elif method == 'ML (Primary)':
            display_method = 'Enhanced ML Model'
        elif method == 'CSV (Primary)':
            display_method = 'Enhanced AI Analysis (CSV)'
        else:
            display_method = method or 'Enhanced AI Analysis'

        return {
            'diagnosis': diagnosis,
            'formatted_response': response_text,
            'method': display_method,
            'matched_symptoms': symptoms,
            'alternative_diagnoses': alternatives,
            'severity_level': self.get_severity_level(confidence, symptoms),
            'extracted_info': {
                'age': age,
                'gender': gender,
                'symptoms_detected': len(symptoms)
            }
        }
    
    def get_condition_description(self, condition):
        """Get accurate medical descriptions from the enhanced dataset CSV"""
        # First try to get description from CSV data
        for row in self.dataset:
            if row.get('diagnosis', '').strip() == condition.strip():
                desc = row.get('diagnosis_description', '').strip()
                if desc:
                    return desc
        
        # Fallback to hardcoded descriptions for conditions not in CSV
        descriptions = {
            # Respiratory Conditions
            'Common Cold': 'Viral upper respiratory infection with nasal congestion, runny nose, mild fever, and fatigue. Usually resolves in 7-10 days with rest and supportive care.',
            'Flu': 'Influenza viral infection causing high fever, severe body aches, headache, cough, and fatigue. More severe than a cold and can last 1-2 weeks.',
            'Pneumonia': 'Serious lung infection causing fever, cough with phlegm, shortness of breath, and chest pain. Requires immediate medical attention and antibiotic treatment.',
            'Bronchitis': 'Inflammation of bronchial tubes causing persistent productive cough, chest congestion, and mild fever. Can be acute or chronic.',
            'Asthma': 'Chronic respiratory condition causing wheezing, shortness of breath, chest tightness, and coughing, especially at night or with triggers.',
            'COVID-19': 'Coronavirus infection affecting respiratory system with fever, cough, shortness of breath, loss of taste/smell, and fatigue.',
            'COVID Variant': 'Variant strain of SARS-CoV-2 with similar symptoms to COVID-19 but potentially different transmission rates or severity.',
            'Upper Respiratory Infection': 'Infection of nose, throat, and upper airways causing congestion, sore throat, cough, and mild fever.',
            'Sinusitis': 'Inflammation of sinus cavities causing facial pressure, nasal congestion, thick discharge, and headache.',
            'Strep Throat': 'Bacterial throat infection causing severe sore throat, fever, swollen lymph nodes, and difficulty swallowing.',
            'Tonsillitis': 'Inflammation of tonsils causing sore throat, difficulty swallowing, fever, and swollen neck glands.',
            
            # Cardiovascular Conditions  
            'Hypertension': 'High blood pressure often causing headaches, dizziness, shortness of breath, and chest discomfort. Requires ongoing management.',
            'Heart Condition': 'Cardiac disorder that may cause chest pain, shortness of breath, fatigue, and irregular heartbeat. Needs medical evaluation.',
            
            # Neurological Conditions
            'Migraine': 'Severe recurring headache often with nausea, light sensitivity, and visual disturbances. Can last hours to days.',
            'Tension Headache': 'Common headache type causing dull, aching pain around the head, often related to stress or muscle tension.',
            'Panic Attack': 'Sudden episode of intense fear with rapid heartbeat, sweating, trembling, shortness of breath, and feeling of doom.',
            
            # Gastrointestinal Conditions
            'Gastroenteritis': 'Stomach and intestinal inflammation causing nausea, vomiting, diarrhea, abdominal pain, and dehydration.',
            'Food Poisoning': 'Foodborne illness causing rapid onset of nausea, vomiting, diarrhea, and stomach cramps after eating contaminated food.',
            'Gastritis': 'Stomach lining inflammation causing burning stomach pain, nausea, bloating, and loss of appetite.',
            'Acid Reflux': 'Stomach acid backing up into esophagus causing heartburn, chest pain, regurgitation, and sour taste.',
            'Stomach Flu': 'Viral gastroenteritis causing nausea, vomiting, diarrhea, stomach pain, and low-grade fever.',
            
            # Metabolic/Endocrine Conditions
            'Diabetes': 'Blood sugar disorder causing excessive thirst, frequent urination, unexplained weight loss, and fatigue.',
            'Dehydration': 'Insufficient body fluid levels causing weakness, dizziness, dry mouth, decreased urination, and fatigue.',
            'Heat Exhaustion': 'Heat-related illness with heavy sweating, weakness, nausea, headache, and elevated body temperature.',
            
            # Blood/Immune Conditions
            'Anemia': 'Low red blood cell count causing fatigue, weakness, pale skin, shortness of breath, and cold hands/feet.',
            'Allergies': 'Immune system reaction to allergens causing sneezing, runny nose, itchy eyes, skin rash, or breathing difficulty.',
            'Seasonal Allergies': 'Allergic reaction to seasonal pollens causing sneezing, runny nose, itchy watery eyes, and nasal congestion.',
            
            # Mental Health Conditions
            'Anxiety Disorder': 'Mental health condition causing excessive worry, restlessness, fatigue, difficulty concentrating, and physical symptoms.',
            'Chronic Fatigue': 'Persistent unexplained fatigue lasting more than 6 months, not relieved by rest and affecting daily activities.',
            
            # Infectious Conditions
            'Tuberculosis': 'Bacterial lung infection causing persistent cough, chest pain, weight loss, night sweats, and fever.',
            'Severe Infection': 'Serious bacterial or viral infection causing high fever, severe symptoms, and requiring immediate medical attention.',
            'Severe Sinus Infection': 'Acute sinusitis with severe facial pain, high fever, thick nasal discharge, and potential complications.',
            
            # General/Other
            'Fever': 'Elevated body temperature often indicating infection or illness, commonly accompanied by other symptoms.',
        }
        
        # Return the specific description or a generic one
        return descriptions.get(condition, f'{condition} is a medical condition requiring professional evaluation for proper diagnosis and treatment.')
    
    def assess_severity(self, diagnosis, confidence, symptoms):
        """Assess severity based on diagnosis and symptoms"""
        high_severity_conditions = ['Pneumonia', 'Heart Attack', 'Stroke', 'Severe Allergic Reaction']
        urgent_symptoms = ['chest_pain', 'shortness_of_breath', 'severe_headache']
        
        if diagnosis in high_severity_conditions:
            return "• This condition requires immediate medical attention.\n• Seek emergency care or call 911 without delay."
        
        if any(symptom in symptoms for symptom in urgent_symptoms):
            return "• Your symptoms include potential warning signs.\n• This is moderate to severe and needs medical attention."
        
        if confidence < 0.5:
            return "• The symptoms are unclear or atypical.\n• Medical evaluation recommended for proper diagnosis."
        
        return "• Your symptoms appear to be mild to moderate.\n• Monitor symptoms and seek care if they worsen."
    
    def format_action_recommendations(self, diagnosis, confidence, symptoms):
        """Format enhanced action recommendations based on diagnosis"""
        
        # Condition-specific action recommendations
        action_recommendations = {
            # Emergency/Urgent Conditions
            'Pneumonia': "• Seek immediate medical attention for antibiotic treatment.\n• Monitor breathing closely and go to ER if shortness of breath worsens.\n• Rest, stay hydrated, and avoid strenuous activities.",
            'Heart Condition': "• Seek urgent medical evaluation for cardiac assessment.\n• Avoid physical exertion and monitor for chest pain or breathing difficulty.\n• Call emergency services if symptoms worsen rapidly.",
            'Severe Infection': "• Seek immediate medical attention for proper diagnosis and treatment.\n• Monitor temperature and watch for worsening symptoms.\n• Stay hydrated and get plenty of rest.",
            'Tuberculosis': "• Seek immediate medical evaluation for TB testing and treatment.\n• Isolate yourself to prevent transmission until cleared by doctor.\n• Follow prescribed medication regimen completely.",
            
            # Respiratory Conditions
            'Flu': "• Rest at home and stay hydrated with plenty of fluids.\n• Take fever reducers as needed and avoid contact with others.\n• See a doctor if symptoms worsen or last more than 10 days.",
            'Common Cold': "• Rest, drink plenty of fluids, and use saline nasal rinses.\n• Take over-the-counter medications for symptom relief as needed.\n• See a doctor if symptoms persist beyond 10 days.",
            'Bronchitis': "• Rest your voice, stay hydrated, and use a humidifier.\n• Avoid smoking and lung irritants.\n• See a doctor if cough persists more than 3 weeks or produces blood.",
            'Asthma': "• Use prescribed inhaler medications as directed.\n• Avoid known triggers and monitor peak flow if available.\n• Seek emergency care if breathing becomes severely difficult.",
            'COVID-19': "• Isolate at home and monitor symptoms closely.\n• Stay hydrated, rest, and take fever reducers as needed.\n• Seek medical care if breathing difficulty develops.",
            'Sinusitis': "• Use saline nasal rinses and apply warm compresses to face.\n• Stay hydrated and consider decongestants for symptom relief.\n• See a doctor if symptoms worsen or persist beyond 10 days.",
            'Strep Throat': "• See a doctor for antibiotic treatment.\n• Rest, drink warm fluids, and gargle with salt water.\n• Complete the full course of prescribed antibiotics.",
            
            # Gastrointestinal Conditions
            'Gastroenteritis': "• Stay hydrated with clear fluids and electrolyte solutions.\n• Follow BRAT diet (bananas, rice, applesauce, toast) when able.\n• See a doctor if unable to keep fluids down or severe dehydration occurs.",
            'Food Poisoning': "• Stay hydrated and rest until symptoms subside.\n• Avoid solid foods initially, then gradually reintroduce bland foods.\n• Seek medical care if symptoms are severe or persist beyond 3 days.",
            'Gastritis': "• Avoid spicy, acidic, and fatty foods that irritate the stomach.\n• Eat smaller, more frequent meals and consider antacids.\n• See a doctor for proper diagnosis and treatment plan.",
            
            # Mental Health Conditions
            'Panic Attack': "• Practice deep breathing and grounding techniques.\n• Remove yourself from triggers if possible and seek a calm environment.\n• Consider counseling or therapy for ongoing panic disorder management.",
            'Anxiety Disorder': "• Practice relaxation techniques and regular exercise.\n• Consider counseling, therapy, or support groups.\n• Speak with a healthcare provider about treatment options.",
            
            # Metabolic Conditions
            'Diabetes': "• Monitor blood sugar levels regularly and follow prescribed diet.\n• Take medications as prescribed and maintain regular exercise.\n• Schedule regular check-ups with your healthcare provider.",
            'Dehydration': "• Drink plenty of fluids, preferably water or electrolyte solutions.\n• Rest in a cool environment and avoid excessive heat.\n• Seek medical care if symptoms are severe or persistent.",
            
            # Allergic Conditions
            'Allergies': "• Identify and avoid known allergens when possible.\n• Take antihistamines as needed for symptom relief.\n• Consider allergy testing and immunotherapy for severe cases.",
            
            # Headache Conditions
            'Migraine': "• Rest in a dark, quiet room and apply cold compress to head.\n• Take prescribed migraine medications at onset of symptoms.\n• Track triggers and discuss prevention strategies with your doctor.",
            'Tension Headache': "• Apply heat or cold to head/neck and practice stress management.\n• Take over-the-counter pain relievers as needed.\n• Consider massage therapy and regular sleep schedule.",
        }
        
        # Get specific recommendation or use generic ones
        specific_action = action_recommendations.get(diagnosis)
        if specific_action:
            return specific_action
        
        # Fallback recommendations based on severity and symptoms
        urgent_conditions = ['Pneumonia', 'Heart Condition', 'Severe Infection', 'Tuberculosis']
        urgent_symptoms = ['chest_pain', 'shortness_of_breath', 'severe_headache']
        
        if diagnosis in urgent_conditions or any(symptom in symptoms for symptom in urgent_symptoms):
            return """• If symptoms are worsening or severe, seek urgent care or ER immediately.
• If mild but persistent, book a doctor's appointment soon for proper evaluation.
• Monitor closely for any changes in breathing, chest pain, or severe worsening.
• Stay hydrated, rest, and avoid strenuous activities."""
        
        if confidence < 0.5:
            return """• Schedule a doctor's appointment for proper diagnosis and testing.
• Keep a symptom diary to track changes and patterns.
• Stay hydrated, get adequate rest, and maintain good nutrition.
• Seek immediate care if symptoms suddenly worsen."""
        
        return """• Monitor symptoms for the next few days.
• If symptoms persist beyond expected timeframe or worsen, consult a healthcare provider.
• Stay hydrated, get adequate rest, and follow general wellness practices.
• Seek medical care if new or concerning symptoms develop."""
    
    def get_severity_level(self, confidence, symptoms):
        """Get severity level for frontend display"""
        urgent_symptoms = ['chest_pain', 'shortness_of_breath', 'severe_headache']
        
        if any(symptom in symptoms for symptom in urgent_symptoms):
            return 'HIGH'
        elif confidence < 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'

    def get_detailed_severity_assessment(self, diagnosis, confidence, symptoms):
        """Get detailed severity assessment for slideshow format"""
        urgent_conditions = ['Pneumonia', 'Heart Attack', 'Stroke', 'Severe Infection', 'Tuberculosis']
        urgent_symptoms = ['chest_pain', 'shortness_of_breath', 'severe_headache', 'loss_of_consciousness']
        warning_symptoms = ['fever', 'fatigue', 'dizziness', 'nausea']
        
        assessment_parts = []
        
        # Check for urgent indicators
        if diagnosis in urgent_conditions or any(symptom in symptoms for symptom in urgent_symptoms):
            assessment_parts.append("• Your symptoms include potential warning signs.")
            assessment_parts.append("• This is moderate to severe and needs medical attention.")
            severity_level = "HIGH"
        elif any(symptom in symptoms for symptom in warning_symptoms) and confidence > 0.7:
            assessment_parts.append("• Your symptoms suggest a moderate condition.")
            assessment_parts.append("• Medical evaluation is recommended for proper care.")
            severity_level = "MEDIUM"
        else:
            assessment_parts.append("• Your symptoms appear to be mild to moderate.")
            assessment_parts.append("• Monitor closely and seek care if worsening.")
            severity_level = "LOW"
        
        return "\n".join(assessment_parts)

    def format_detailed_recommendations(self, diagnosis, confidence, symptoms):
        """Format detailed recommendations for slideshow format using CSV data"""
        # First try to get recommendations from CSV data
        csv_recommendation = None
        for row in self.dataset:
            if row.get('diagnosis', '').strip() == diagnosis.strip():
                rec = row.get('recommended_action', '').strip()
                if rec:
                    csv_recommendation = rec
                    break
        
        recommendations = []
        
        if csv_recommendation:
            # Use CSV recommendation as primary source
            recommendations.append(f"• {csv_recommendation}")
        
        # Add additional context-based recommendations
        urgent_conditions = ['Pneumonia', 'Heart Attack', 'Stroke', 'Severe Infection', 'Tuberculosis']
        urgent_symptoms = ['chest_pain', 'shortness_of_breath', 'severe_headache']
        
        # Add general care recommendations
        if diagnosis in urgent_conditions or any(symptom in symptoms for symptom in urgent_symptoms):
            if not csv_recommendation:
                recommendations.append("• If symptoms are worsening or severe, seek urgent care or ER immediately.")
            recommendations.append("• Monitor closely for any changes in breathing, chest pain, or severe worsening.")
            recommendations.append("• Stay hydrated, rest, and avoid strenuous activities.")
        else:
            if not csv_recommendation:
                recommendations.append("• Monitor symptoms for the next few days.")
                recommendations.append("• If symptoms persist beyond expected timeframe or worsen, consult a healthcare provider.")
            recommendations.append("• Stay hydrated, get adequate rest, and follow general wellness practices.")
            recommendations.append("• Seek medical care if new or concerning symptoms develop.")
        
        return "\n".join(recommendations)

    def get_recommendations(self, diagnosis, confidence):
        """Get treatment recommendations based on diagnosis"""
        recommendations_map = {
            'Flu': [
                'Get plenty of rest (7-9 hours of sleep)',
                'Drink lots of fluids (water, herbal teas, broths)',
                'Take fever reducers like acetaminophen or ibuprofen if needed',
                'Stay home to avoid spreading illness',
                'Seek medical care if symptoms worsen or persist beyond 10 days'
            ],
            'Common Cold': [
                'Rest and sleep adequately',
                'Drink warm liquids (tea, warm water with honey)',
                'Use throat lozenges or gargle with salt water',
                'Consider over-the-counter cold medicines for symptom relief',
                'Symptoms usually resolve in 7-10 days'
            ],
            'Pneumonia': [
                '⚠️ SEEK IMMEDIATE MEDICAL ATTENTION',
                'This condition requires professional medical treatment',
                'Do not delay seeking medical care',
                'May require antibiotics or hospitalization',
                'Monitor breathing and seek emergency care if it worsens'
            ],
            'COVID-19': [
                'Isolate immediately to prevent spread',
                'Get tested for COVID-19',
                'Monitor oxygen levels if possible',
                'Seek medical care if breathing difficulties develop',
                'Follow current CDC guidelines for isolation'
            ],
            'Allergic Reaction': [
                'Identify and avoid known allergens',
                'Consider antihistamines for mild reactions',
                'Use cool compresses for skin reactions',
                'Seek emergency care for severe reactions (difficulty breathing, swelling)'
            ],
            'Migraine': [
                'Rest in a quiet, dark room',
                'Apply cold or warm compress to head/neck',
                'Stay hydrated',
                'Consider over-the-counter pain relievers',
                'Track triggers and consult doctor for frequent migraines'
            ]
        }
        
        base_recommendations = recommendations_map.get(diagnosis, [
            'Monitor symptoms closely',
            'Consult healthcare provider if symptoms persist or worsen',
            'Rest and stay hydrated',
            'Seek emergency care if symptoms worsen rapidly'
        ])
        
        if confidence < 0.5:
            base_recommendations.insert(0, '⚠️ Low confidence diagnosis - strongly recommend consulting a healthcare professional')
        
        return base_recommendations
    
    def add_demographic_recommendations(self, base_recommendations, diagnosis, age, gender):
        """Add age and gender-specific recommendations"""
        enhanced_recommendations = base_recommendations.copy()
        
        # Age-specific recommendations (handle both age groups and numeric ages)
        if age is not None:
            # Convert to age group if it's numeric
            if isinstance(age, (int, float)):
                age_group = self.convert_age_to_group(age)
            else:
                age_group = age.lower() if isinstance(age, str) else None
            
            if age_group == 'child' or (isinstance(age, (int, float)) and int(age) < 18):
                enhanced_recommendations.insert(0, '👶 For children: Consult pediatrician for proper dosing and treatment')
                if diagnosis in ['Flu', 'Common Cold']:
                    enhanced_recommendations.append('Ensure adequate fluid intake and monitor temperature closely')
            elif age_group == 'senior' or (isinstance(age, (int, float)) and int(age) > 65):
                enhanced_recommendations.insert(0, '👴 For elderly patients: Monitor symptoms closely and seek medical care sooner')
                if diagnosis == 'Pneumonia':
                    enhanced_recommendations.insert(1, '🚨 Elderly pneumonia requires immediate medical attention')
                enhanced_recommendations.append('Consider medication interactions with existing prescriptions')
            
        # Gender-specific recommendations  
        if gender == 'female':
            if diagnosis in ['Migraine', 'Headache']:
                enhanced_recommendations.append('Track symptoms with menstrual cycle - hormonal migraines are common')
            if age and isinstance(age, (int, float)) and 15 <= age <= 50:
                enhanced_recommendations.append('Consider pregnancy if applicable - some medications not recommended')
        elif gender == 'male':
            if diagnosis in ['Heart Disease', 'Chest Pain'] and age and isinstance(age, (int, float)) and age > 40:
                enhanced_recommendations.insert(1, '♂️ Men over 40: Chest pain requires immediate cardiac evaluation')
        
        return enhanced_recommendations

# Initialize the enhanced AI engine
ai_diagnosis_engine = EnhancedAIEngine()

# Import our services
from auth.firebase_auth_routes import auth_firebase_bp
from auth.auth_routes import auth_bp
from medical_routes import medical_bp
from appointment_routes import appointments_bp
from contact_routes import contact_bp
from profile_routes import profile_bp
from profile_management import profile_mgmt_bp
from patient_profile_routes import patient_profile_bp
from doctor_verification import doctor_verification_bp
from db.supabase_client import SupabaseClient

# Import new healthcare system routes
from healthcare_routes import (
    healthcare_auth_bp,
    healthcare_medical_bp, 
    healthcare_appointments_bp,
    healthcare_system_bp
)

# Test auth endpoints removed during cleanup

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:3002", "http://127.0.0.1:3002"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure Flask
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# Register blueprints
app.register_blueprint(auth_firebase_bp)
app.register_blueprint(auth_bp)  # Password reset and auth functionality
app.register_blueprint(medical_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(profile_mgmt_bp)
app.register_blueprint(patient_profile_bp)
app.register_blueprint(doctor_verification_bp)  # Doctor signup and verification

# Register new healthcare system blueprints
app.register_blueprint(healthcare_auth_bp)
app.register_blueprint(healthcare_medical_bp)
app.register_blueprint(healthcare_appointments_bp)
app.register_blueprint(healthcare_system_bp)

# Test auth blueprint registration removed during cleanup

# Initialize Supabase client (lazy loading to avoid startup issues)
supabase = None

def get_supabase_client():
    """Lazy initialization of Supabase client"""
    global supabase
    if supabase is None:
        supabase = SupabaseClient()
    return supabase

@app.route('/')
def index():
    """Health check endpoint"""
    return {
        'status': 'MediChain Backend is running!',
        'version': '1.1.0',
        'services': {
            'firebase_auth': 'configured',
            'supabase_storage': 'configured',
            'medical_records': 'available',
            'appointments': 'available',
            'profile_management': 'available',
            'ai_diagnosis': 'available' if ai_diagnosis_engine.dataset else 'unavailable'
        },
        'endpoints': {
            'auth': '/api/auth/*',
            'medical': '/api/medical/*',
            'appointments': '/api/appointments/*',
            'profile': '/api/profile/*',
            'contact': '/api/contact/*',
            'ai_diagnosis': '/api/ai/*'
        },
        'ai_info': {
            'total_records': len(ai_diagnosis_engine.dataset),
            'available_conditions': len(ai_diagnosis_engine.diagnoses)
        }
    }


@app.route('/api/health')
def health_check():
    """Detailed health check"""
    try:
        # Test Supabase connection
        supabase_status = 'connected' if supabase.client else 'disconnected'
        
        return {
            'status': 'healthy',
            'services': {
                'supabase': supabase_status,
                'firebase': 'configured',  # Firebase is initialized in the auth service
                'ai_diagnosis': 'loaded' if ai_diagnosis_engine.dataset else 'unavailable'
            },
            'ai_info': {
                'dataset_loaded': len(ai_diagnosis_engine.dataset) > 0,
                'total_records': len(ai_diagnosis_engine.dataset),
                'available_diagnoses': len(ai_diagnosis_engine.diagnoses)
            }
        }
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500


# AI Diagnosis Routes
@app.route('/api/ai/health', methods=['GET'])
def ai_health():
    """AI system health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'AI diagnosis system is running',
        'dataset_loaded': len(ai_diagnosis_engine.dataset) > 0,
        'total_records': len(ai_diagnosis_engine.dataset),
        'available_diagnoses': len(ai_diagnosis_engine.diagnoses),
        'supported_symptoms': len(ai_diagnosis_engine.symptom_columns)
    })


@app.route('/api/ai/diagnose', methods=['POST'])
def ai_diagnose():
    """Enhanced AI diagnosis endpoint with ML and text understanding"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get input data - handle both old and new formats
        symptoms = data.get('symptoms', [])
        
        # Handle patient_data format (new frontend)
        patient_data = data.get('patient_data', {})
        age_raw = data.get('age') or patient_data.get('age')
        gender = data.get('gender') or patient_data.get('gender')
        
        # Handle symptoms as text description (new format)
        input_text = data.get('text', '') or data.get('symptoms', '') if isinstance(data.get('symptoms'), str) else ''
        description = data.get('description', '')
        
        # Convert age group to numeric if needed
        age = None
        if age_raw:
            if isinstance(age_raw, str):
                # Handle age group selections like "Teenager (13 - 19 years)"
                age_mapping = {
                    'child': 8,
                    'teen': 16, 
                    'teenager': 16,
                    'adult': 35,
                    'senior': 70
                }
                
                age_lower = age_raw.lower()
                if 'child' in age_lower:
                    age = 8
                elif 'teen' in age_lower:
                    age = 16
                elif 'adult' in age_lower:
                    age = 35
                elif 'senior' in age_lower:
                    age = 70
                else:
                    try:
                        age = int(age_raw)
                    except ValueError:
                        age = None
            else:
                age = age_raw
        
        # Combine text inputs
        full_text = f"{input_text} {description}".strip()
        
        # Check if we have either symptoms or text
        if not symptoms and not full_text:
            return jsonify({'error': 'No symptoms or description provided'}), 400
        
        print(f"🩺 Processing diagnosis request:")
        print(f"   📝 Symptoms: {symptoms}")
        print(f"   📄 Text: {full_text}")
        print(f"   👤 Age: {age}, Gender: {gender}")
        
        # Get diagnosis from enhanced AI engine
        result = ai_diagnosis_engine.diagnose(
            input_text=full_text,
            symptoms=symptoms, 
            age=age, 
            gender=gender
        )
        
        # Add processing metadata
        result['processing_info'] = {
            'text_processed': bool(full_text),
            'symptoms_provided': len(symptoms) if symptoms else 0,
            'age_provided': age is not None,
            'gender_provided': gender is not None,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(result)
        
    except Exception as e:
        print(f"AI Diagnosis Error: {e}")
        return jsonify({
            'error': f'Diagnosis failed: {str(e)}',
            'diagnosis': 'Error in diagnosis',
            'confidence': 0.0,
            'method': 'Error'
        }), 500


@app.route('/api/ai/learning-stats', methods=['GET'])
def ai_learning_stats():
    """Get AI model statistics and information"""
    dataset_info = {}
    if ai_diagnosis_engine.dataset:
        # Calculate diagnosis distribution
        diagnosis_counts = Counter(row['diagnosis'] for row in ai_diagnosis_engine.dataset)
        dataset_info = {
            'total_records': len(ai_diagnosis_engine.dataset),
            'unique_diagnoses': len(ai_diagnosis_engine.diagnoses),
            'most_common_diagnosis': diagnosis_counts.most_common(1)[0][0] if diagnosis_counts else 'None',
            'symptom_features': len(ai_diagnosis_engine.symptom_columns),
            'available_diagnoses': list(ai_diagnosis_engine.diagnoses)[:10]  # Top 10
        }
    
    return jsonify({
        'model_info': {
            'name': 'MediChain-CSV-AI',
            'type': 'Symptom-based CSV diagnosis engine',
            'accuracy': 'Variable based on symptom match quality',
            'total_features': dataset_info.get('symptom_features', 0),
            'last_updated': '2025-10-02',
            'supported_conditions': dataset_info.get('unique_diagnoses', 0),
            'dataset_size': dataset_info.get('total_records', 0)
        },
        'learning_progress': {
            'total_cases': dataset_info.get('total_records', 0),
            'diagnosis_distribution': dict(Counter(row['diagnosis'] for row in ai_diagnosis_engine.dataset).most_common(5)) if ai_diagnosis_engine.dataset else {},
            'available_symptoms': ai_diagnosis_engine.symptom_columns[:10] if ai_diagnosis_engine.symptom_columns else []
        }
    })


@app.route('/api/ai/submit-feedback', methods=['POST'])
def ai_submit_feedback():
    """Submit feedback for AI diagnosis (for future improvements)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No feedback data provided'}), 400
        
        # For now, just acknowledge the feedback
        # In a production system, this would be stored for model improvement
        feedback_type = data.get('feedback', 'general')
        rating = data.get('rating')
        comments = data.get('comments', '')
        
        # Log the feedback (in production, store in database)
        print(f"📝 AI Feedback received: {feedback_type} (Rating: {rating}) - {comments}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback received successfully. Thank you for helping improve our AI system!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to submit feedback: {str(e)}'
        }), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])