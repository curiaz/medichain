#!/usr/bin/env python3
"""
Comprehensive AI Diagnosis System with Enhanced Confidence
Core AI diagnosis logic for MediChain with confidence boosting
"""

import pickle
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import re
import logging
from datetime import datetime
import json
from medication_recommendations import MedicationRecommendations

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveAIDiagnosis:
    """Enhanced AI diagnosis system with confidence boosting mechanisms"""
    
    def __init__(self, model_path='final_comprehensive_model.pkl', 
                 encoder_path='final_comprehensive_encoder.pkl',
                 features_path='final_comprehensive_features.pkl'):
        """Initialize the comprehensive AI diagnosis system"""
        
        try:
            # Load model components
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(encoder_path, 'rb') as f:
                self.label_encoder = pickle.load(f)
            with open(features_path, 'rb') as f:
                self.feature_names = pickle.load(f)
            
            logger.info(f"Model loaded successfully")
            logger.info(f"Features: {len(self.feature_names)}")
            logger.info(f"Supported diagnoses: {len(self.label_encoder.classes_)}")
            
            # Initialize symptom parser
            self.symptom_parser = EnhancedSymptomParser()
            
            # Initialize medication recommendations
            self.medication_recommendations = MedicationRecommendations()
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def diagnose(self, symptoms_text: str, duration_text: str = "", 
                intensity_text: str = "") -> Dict:
        """
        Comprehensive diagnosis with natural language processing and confidence boosting
        
        Args:
            symptoms_text: Natural language description of symptoms
            duration_text: Duration information (optional)
            intensity_text: Intensity information (optional)
        
        Returns:
            Dictionary with diagnosis results and enhanced confidence
        """
        try:
            # Parse symptoms and extract features
            parsed_result = self.symptom_parser.parse_comprehensive(
                symptoms_text, duration_text, intensity_text
            )
            
            # Create feature vector
            feature_vector = self._create_feature_vector(parsed_result)
            
            # Make prediction
            prediction = self.model.predict([feature_vector])[0]
            probabilities = self.model.predict_proba([feature_vector])[0]
            
            # Get base confidence
            base_confidence = float(probabilities[prediction])
            
            # Apply confidence boosting
            boosted_confidence = self._apply_confidence_boosting(
                base_confidence, parsed_result, feature_vector
            )
            
            # Get diagnosis name
            diagnosis = self.label_encoder.inverse_transform([prediction])[0]
            
            # Get top 3 predictions with boosted confidence
            top_indices = np.argsort(probabilities)[-3:][::-1]
            top_predictions = []
            
            for idx in top_indices:
                pred_diagnosis = self.label_encoder.inverse_transform([idx])[0]
                pred_confidence = float(probabilities[idx]) * 100  # Convert to percentage
                
                # Apply boosting to primary prediction
                if idx == prediction:
                    pred_confidence = boosted_confidence * 100  # Convert to percentage
                
                # Get medication recommendations for this diagnosis
                med_recommendations = self.medication_recommendations.get_recommendations(pred_diagnosis)
                
                top_predictions.append({
                    'diagnosis': pred_diagnosis,
                    'confidence': pred_confidence,
                    'medications': med_recommendations['medications'][:3],  # Top 3 medications
                    'dosage': med_recommendations['dosage'],
                    'duration': med_recommendations['duration'],
                    'instructions': med_recommendations['instructions']
                })
            
            # Get comprehensive medication recommendations for all top predictions
            medication_summary = self.medication_recommendations.get_multiple_recommendations(top_predictions)
            
            result = {
                'primary_diagnosis': diagnosis,
                'confidence': boosted_confidence * 100,  # Convert to percentage
                'base_confidence': base_confidence * 100,  # Convert to percentage
                'top_predictions': top_predictions,
                'medication_recommendations': medication_summary,
                'parsed_symptoms': parsed_result['symptoms'],
                'duration_days': parsed_result['duration_days'],
                'intensity': parsed_result['intensity'],
                'feature_vector': dict(zip(self.feature_names, feature_vector)),
                'confidence_level': self._get_confidence_level(boosted_confidence),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Diagnosis: {diagnosis} (confidence: {boosted_confidence:.3f})")
            return result
            
        except Exception as e:
            logger.error(f"Error in diagnosis: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _create_feature_vector(self, parsed_result: Dict) -> List[float]:
        """Create feature vector from parsed symptoms"""
        
        # Define expected symptom features (matching model training)
        expected_symptoms = [
            'fever', 'cough', 'fatigue', 'shortness_of_breath', 'headache', 
            'sore_throat', 'nausea', 'dizziness', 'body_aches', 'runny_nose', 
            'chest_pain', 'diarrhea', 'loss_of_taste', 'loss_of_smell'
        ]
        
        # Create symptom vector
        symptom_vector = []
        for symptom in expected_symptoms:
            if symptom in parsed_result['symptoms']:
                symptom_vector.append(1.0)
            else:
                symptom_vector.append(0.0)
        
        # Add duration (numeric)
        duration_days = float(parsed_result.get('duration_days', 7))  # Default 7 days
        symptom_vector.append(duration_days)
        
        # Add intensity (numeric)
        intensity_mapping = {
            'mild': 1.0,
            'moderate': 2.0,
            'severe': 3.0
        }
        intensity_numeric = intensity_mapping.get(
            parsed_result.get('intensity', 'moderate'), 2.0
        )
        symptom_vector.append(intensity_numeric)
        
        return symptom_vector
    
    def _apply_confidence_boosting(self, base_confidence: float, 
                                 parsed_result: Dict, feature_vector: List[float]) -> float:
        """Apply confidence boosting based on various factors"""
        
        boosted_confidence = base_confidence
        
        # 1. High symptom count boost (more symptoms = higher confidence)
        symptom_count = sum(feature_vector[:14])  # First 14 are symptom features
        if symptom_count >= 4:
            boosted_confidence *= 1.20  # 20% boost for 4+ symptoms
        elif symptom_count >= 3:
            boosted_confidence *= 1.10  # 10% boost for 3 symptoms
        
        # 2. Duration specificity boost
        duration_days = parsed_result.get('duration_days', 7)
        if duration_days != 7:  # Not default value
            boosted_confidence *= 1.08  # 8% boost for specified duration
        
        # 3. Intensity specificity boost
        intensity = parsed_result.get('intensity', 'moderate')
        if intensity != 'moderate':  # Not default value
            boosted_confidence *= 1.06  # 6% boost for specified intensity
        
        # 4. Symptom combination patterns boost
        symptoms = parsed_result['symptoms']
        confident_combinations = [
            ['fever', 'cough', 'fatigue'],                    # Flu-like
            ['headache', 'nausea', 'dizziness'],             # Migraine
            ['chest_pain', 'shortness_of_breath'],           # Respiratory
            ['loss_of_taste', 'loss_of_smell'],              # COVID-like
            ['sore_throat', 'fever', 'body_aches'],          # Strep-like
        ]
        
        for combo in confident_combinations:
            if all(symptom in symptoms for symptom in combo):
                boosted_confidence *= 1.15  # 15% boost for known patterns
                break
        
        # Cap confidence at 0.95 (never 100% certain in medical diagnosis)
        boosted_confidence = min(boosted_confidence, 0.95)
        
        return boosted_confidence
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get human-readable confidence level"""
        if confidence >= 0.85:
            return "Very High"
        elif confidence >= 0.75:
            return "High" 
        elif confidence >= 0.60:
            return "Medium"
        elif confidence >= 0.45:
            return "Moderate"
        else:
            return "Low"

class EnhancedSymptomParser:
    """Enhanced symptom parser with comprehensive natural language processing"""
    
    def __init__(self):
        # Comprehensive symptom keywords
        self.symptom_keywords = {
            'fever': [
                'fever', 'temperature', 'hot', 'burning up', 'feverish', 
                'high temp', 'pyrexia', 'febrile', 'warm', 'overheated',
                'elevated temperature', 'running a fever'
            ],
            'cough': [
                'cough', 'coughing', 'hack', 'dry cough', 'wet cough', 
                'productive cough', 'persistent cough', 'hacking', 'barking cough',
                'chronic cough', 'whooping', 'tickle in throat'
            ],
            'fatigue': [
                'tired', 'fatigue', 'exhausted', 'weakness', 'weary', 
                'drained', 'lethargic', 'sleepy', 'worn out', 'depleted',
                'energy loss', 'run down', 'beat', 'wiped out'
            ],
            'shortness_of_breath': [
                'shortness of breath', 'breathless', 'difficulty breathing', 
                'hard to breathe', 'winded', 'dyspnea', 'suffocating', 'gasping',
                'out of breath', 'breathing problems', 'air hunger'
            ],
            'headache': [
                'headache', 'head pain', 'migraine', 'head hurts', 
                'skull pain', 'cranial pain', 'temple pain', 'forehead pain',
                'tension headache', 'cluster headache', 'throbbing head'
            ],
            'sore_throat': [
                'sore throat', 'throat pain', 'scratchy throat', 'throat hurts', 
                'pharyngitis', 'swollen throat', 'raw throat', 'burning throat',
                'irritated throat', 'throat inflammation'
            ],
            'nausea': [
                'nausea', 'nauseous', 'queasy', 'sick to stomach', 
                'feeling sick', 'want to vomit', 'motion sickness', 'car sick',
                'upset stomach', 'stomach churning', 'feel like throwing up'
            ],
            'dizziness': [
                'dizzy', 'dizziness', 'lightheaded', 'vertigo', 'spinning', 
                'unsteady', 'balance problems', 'wobbly', 'off balance',
                'room spinning', 'head spinning', 'faint feeling'
            ],
            'body_aches': [
                'body aches', 'muscle aches', 'joint pain', 'aching', 
                'soreness', 'stiffness', 'muscle pain', 'joint aches', 'myalgia',
                'all over pain', 'generalized pain', 'muscle soreness'
            ],
            'runny_nose': [
                'runny nose', 'nasal discharge', 'stuffy nose', 'congestion', 
                'blocked nose', 'rhinorrhea', 'sniffles', 'post nasal drip',
                'nasal congestion', 'stuffed up', 'nose running'
            ],
            'chest_pain': [
                'chest pain', 'chest discomfort', 'chest tightness', 
                'heart pain', 'sternum pain', 'ribcage pain', 'breathing pain',
                'chest pressure', 'chest burning', 'sharp chest pain'
            ],
            'diarrhea': [
                'diarrhea', 'loose stools', 'watery stools', 'frequent bowel', 
                'runny stools', 'liquid stool', 'bowel problems', 'stomach runs',
                'loose bowel movements', 'frequent bathroom trips'
            ],
            'loss_of_taste': [
                'loss of taste', 'can\'t taste', 'no taste', 'taste gone', 
                'taste loss', 'ageusia', 'taste buds not working', 'food tasteless',
                'metallic taste', 'altered taste'
            ],
            'loss_of_smell': [
                'loss of smell', 'can\'t smell', 'no smell', 'smell gone',
                'smell loss', 'anosmia', 'nose not working', 'odor loss'
            ]
        }
        
        # Enhanced duration patterns
        self.duration_patterns = [
            (r'(\d+)\s*(day|days)', lambda m: int(m.group(1))),
            (r'(\d+)\s*(week|weeks)', lambda m: int(m.group(1)) * 7),
            (r'(\d+)\s*(month|months)', lambda m: int(m.group(1)) * 30),
            (r'since\s+(\d+)\s*(day|days)\s+ago', lambda m: int(m.group(1))),
            (r'for\s+(\d+)\s*(day|days)', lambda m: int(m.group(1))),
            (r'about\s+(\d+)\s*(day|days)', lambda m: int(m.group(1))),
            (r'yesterday', lambda m: 1),
            (r'today', lambda m: 1),
            (r'few days', lambda m: 3),
            (r'several days', lambda m: 5),
            (r'last week', lambda m: 7),
            (r'this week', lambda m: 3),
            (r'two weeks', lambda m: 14),
            (r'last month', lambda m: 30)
        ]
        
        # Enhanced intensity patterns
        self.intensity_patterns = {
            'mild': [
                'mild', 'slight', 'minor', 'light', 'gentle', 'low', 
                'barely', 'little bit', 'somewhat', 'not too bad'
            ],
            'moderate': [
                'moderate', 'medium', 'average', 'normal', 'typical', 
                'noticeable', 'considerable', 'fair', 'decent'
            ],
            'severe': [
                'severe', 'intense', 'extreme', 'terrible', 'awful', 
                'excruciating', 'unbearable', 'very', 'really bad', 'horrible'
            ]
        }
    
    def parse_comprehensive(self, symptoms_text: str, duration_text: str = "", 
                          intensity_text: str = "") -> Dict:
        """Parse comprehensive symptom information with enhanced NLP"""
        
        # Combine all text for parsing
        full_text = f"{symptoms_text} {duration_text} {intensity_text}".lower()
        
        # Extract symptoms
        detected_symptoms = self._extract_symptoms(full_text)
        
        # Extract duration
        duration_days = self._extract_duration(full_text)
        
        # Extract intensity
        intensity = self._extract_intensity(full_text)
        
        return {
            'symptoms': detected_symptoms,
            'duration_days': duration_days,
            'intensity': intensity,
            'raw_text': symptoms_text
        }
    
    def _extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms from text using comprehensive keyword matching"""
        detected = []
        
        for symptom, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    detected.append(symptom)
                    break
        
        return detected
    
    def _extract_duration(self, text: str) -> int:
        """Extract duration in days from text"""
        
        for pattern, converter in self.duration_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return converter(match)
                except:
                    continue
        
        # Default to 7 days if no duration found
        return 7
    
    def _extract_intensity(self, text: str) -> str:
        """Extract intensity from text using enhanced pattern matching"""
        
        # Score-based approach for better accuracy
        intensity_scores = {'mild': 0, 'moderate': 0, 'severe': 0}
        
        for intensity, keywords in self.intensity_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    intensity_scores[intensity] += 1
        
        # Return intensity with highest score
        if max(intensity_scores.values()) > 0:
            return max(intensity_scores.items(), key=lambda x: x[1])[0]
        
        return 'moderate'  # Default
    
    def _was_duration_detected(self, text: str) -> bool:
        """Check if duration was actually detected from text"""
        text = text.lower()
        for pattern, _ in self.duration_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _was_intensity_detected(self, text: str) -> bool:
        """Check if intensity was actually detected from text"""
        text = text.lower()
        for keywords in self.intensity_patterns.values():
            for keyword in keywords:
                if keyword in text:
                    return True
        return False

# Example usage and testing
def test_comprehensive_diagnosis():
    """Test the comprehensive diagnosis system"""
    
    print("🧪 Testing Comprehensive AI Diagnosis System")
    print("="*60)
    
    try:
        # Initialize diagnosis system
        ai_diagnosis = ComprehensiveAIDiagnosis()
        
        # Test cases
        test_cases = [
            {
                'symptoms': "severe headache and fever for 3 days, feeling very tired",
                'duration': "3 days",
                'intensity': "severe"
            },
            {
                'symptoms': "mild cough and runny nose since yesterday, sore throat",
                'duration': "1 day", 
                'intensity': "mild"
            },
            {
                'symptoms': "chest pain, shortness of breath, very intense for about a week",
                'duration': "1 week",
                'intensity': "severe"
            }
        ]
        
        for i, case in enumerate(test_cases):
            print(f"\n--- Test Case {i+1} ---")
            print(f"Input: {case['symptoms']}")
            
            result = ai_diagnosis.diagnose(
                case['symptoms'], 
                case['duration'], 
                case['intensity']
            )
            
            if 'error' not in result:
                print(f"Diagnosis: {result['primary_diagnosis']}")
                print(f"Confidence: {result['confidence']:.3f} ({result['confidence_level']})")
                print(f"Base Confidence: {result['base_confidence']:.3f}")
                print(f"Duration: {result['duration_days']} days")
                print(f"Intensity: {result['intensity']}")
                print(f"Symptoms: {result['parsed_symptoms']}")
            else:
                print(f"Error: {result['error']}")
        
        print("\n✅ Testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")

if __name__ == "__main__":
    test_comprehensive_diagnosis()
