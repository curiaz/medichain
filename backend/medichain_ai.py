
"""
MediChain Custom AI System - Completely Self-Contained
No external APIs, no internet required, no API keys needed!

Created by: MediChain Development Team
Version: 2.0
Date: August 2025

Usage in Flask:
    from medichain_ai import MediChainAI

    ai = MediChainAI()
    result = ai.diagnose(user_input="I have fever and cough")
    print(result['primary_diagnosis'])
"""

import os
import numpy as np
import pandas as pd
import joblib
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class MediChainAI:
    """
    Completely self-contained AI diagnosis system for MediChain
    No external APIs required - everything built from scratch using scikit-learn!
    Now with conversational diagnosis capabilities!
    """

    def __init__(self, model_path: str = "."):
        """Initialize the AI system with model files"""
        self.model_path = model_path
        self.model = None
        self.label_encoder = None
        self.feature_names = None
        self.prescriptions_map = None
        
        # Conversational state
        self.conversation_history = []
        self.gathered_symptoms = {}
        self.follow_up_questions = []
        
        # Question templates for different scenarios (removed duration questions - extracted from text instead)
        self.question_templates = {
            'fever_severity': {
                'question': 'How high is your fever?',
                'options': ['Low grade (99-100°F)', 'Moderate (101-102°F)', 'High (103°F+)', "I don't know"],
                'follow_up': 'additional_symptoms'
            },
            'cough_type': {
                'question': 'What type of cough do you have?',
                'options': ['Dry cough', 'Wet/productive cough', 'Cough with blood', 'Barking cough', "I don't know"],
                'follow_up': 'additional_symptoms'
            },
            'pain_location': {
                'question': 'Where exactly is the pain located?',
                'options': ['Head/forehead', 'Behind eyes', 'Temples', 'Back of head', 'All over head', "I can't pinpoint it"],
                'follow_up': 'pain_severity'
            },
            'pain_severity': {
                'question': 'How severe is the pain on a scale of 1-10?',
                'options': ['1-3 (mild)', '4-6 (moderate)', '7-8 (severe)', '9-10 (unbearable)', "I don't know"],
                'follow_up': 'additional_symptoms'
            },
            'breathing_difficulty': {
                'question': 'When do you experience breathing difficulty?',
                'options': ['At rest', 'During activity', 'When lying down', 'All the time', "I'm not sure"],
                'follow_up': 'additional_symptoms'
            },
            'nausea_triggers': {
                'question': 'What seems to trigger your nausea?',
                'options': ['Eating', 'Moving around', 'Strong smells', 'Stress', 'No specific trigger', "I don't know"],
                'follow_up': 'additional_symptoms'
            },
            'additional_symptoms': {
                'question': 'Do you have any other symptoms not mentioned?',
                'options': ['Chills', 'Sweating', 'Loss of appetite', 'Fatigue', 'None', "I can't remember"],
                'follow_up': None
            }
        }

        # Our enhanced symptom keyword database - no external NLP needed!
        self.symptom_keywords = {
            'fever': ['fever', 'hot', 'temperature', 'burning up', 'chills', 'feverish', 'high temp', 'pyrexia', 'febrile'],
            'cough': ['cough', 'coughing', 'hack', 'wheeze', 'phlegm', 'mucus', 'chest congestion', 'productive cough', 'dry cough'],
            'fatigue': ['tired', 'fatigue', 'exhausted', 'weak', 'weary', 'drained', 'lethargic', 'sleepy', 'worn out', 'energy'],
            'shortness_of_breath': ['breathless', 'short of breath', 'breathing difficulty', 'wheezing', 'gasping', 'chest tight', 'dyspnea', 'winded'],
            'headache': ['headache', 'head pain', 'migraine', 'head pressure', 'skull pain', 'temple pain', 'cephalgia', 'head ache'],
            'sore_throat': ['sore throat', 'throat pain', 'scratchy throat', 'swollen throat', 'throat irritation', 'pharyngitis', 'throat ache'],
            'nausea': ['nausea', 'nauseous', 'sick', 'queasy', 'stomach upset', 'feel like vomiting', 'want to throw up', 'motion sickness'],
            'dizziness': ['dizzy', 'dizziness', 'lightheaded', 'vertigo', 'spinning', 'balance problems', 'unsteady', 'wobbly'],
            'body_aches': ['body aches', 'muscle pain', 'joint pain', 'soreness', 'stiffness', 'aching muscles', 'myalgia', 'muscle soreness'],
            'runny_nose': ['runny nose', 'stuffy nose', 'nasal congestion', 'sniffles', 'blocked nose', 'nose running', 'rhinorrhea'],
            'chest_pain': ['chest pain', 'chest pressure', 'heart pain', 'chest tightness', 'chest discomfort', 'angina', 'chest ache'],
            'diarrhea': ['diarrhea', 'loose stools', 'watery stools', 'frequent bowel movements', 'stomach runs', 'digestive issues'],
            'loss_of_taste': ['loss of taste', 'cant taste', 'no taste', 'taste gone', 'ageusia', 'taste buds not working'],
            'loss_of_smell': ['loss of smell', 'cant smell', 'no smell', 'smell gone', 'anosmia', 'nose cant smell']
        }

        self.load_model()

    def load_model(self):
        """Load our custom trained AI model and components - prioritize enhanced model"""
        try:
            # Try to load enhanced model first (newest with 56 diagnoses)
            self.model = joblib.load(os.path.join(self.model_path, "enhanced_diagnosis_model.pkl"))
            self.label_encoder = joblib.load(os.path.join(self.model_path, "enhanced_label_encoder.pkl"))
            self.feature_names = joblib.load(os.path.join(self.model_path, "enhanced_feature_names.pkl"))
            self.prescriptions_map = joblib.load(os.path.join(self.model_path, "enhanced_prescriptions_map.pkl"))
            print(f"Loaded enhanced model successfully! ({len(self.label_encoder.classes_)} diagnoses available)")
            return True
        except Exception as e:
            print(f"Enhanced model not found, trying conversational model: {e}")
            try:
                # Fallback to conversational model if enhanced doesn't exist
                self.model = joblib.load(os.path.join(self.model_path, "conversational_diagnosis_model.pkl"))
                self.label_encoder = joblib.load(os.path.join(self.model_path, "conversational_label_encoder.pkl"))
                self.feature_names = joblib.load(os.path.join(self.model_path, "conversational_feature_names.pkl"))
                self.prescriptions_map = joblib.load(os.path.join(self.model_path, "conversational_prescriptions_map.pkl"))
                print("Loaded conversational model successfully!")
                return True
            except Exception as e2:
                print(f"Error loading MediChain AI model: {e2}")
                return False

    def parse_symptoms_from_text(self, text: str) -> Dict[str, int]:
        """
        Parse natural language text to detect symptoms
        Returns basic symptom presence for the model
        """
        text = text.lower()
        detected_symptoms = {}

        # Initialize symptom detection - only basic symptoms for the model
        for symptom, keywords in self.symptom_keywords.items():
            detected_symptoms[symptom] = 0
            
            for keyword in keywords:
                if keyword in text:
                    detected_symptoms[symptom] = 1
                    break

        return detected_symptoms

    def extract_duration_info(self, text: str) -> Dict[str, str]:
        """
        Extract duration information from user's natural text input
        Returns readable duration information
        """
        import re
        
        text = text.lower()
        duration_info = {}

        # Duration patterns to extract temporal information from natural language
        duration_patterns = [
            r'(\w+)\s+for\s+(\d+)\s+(day|days|hour|hours|week|weeks|month|months)',
            r'(\d+)\s+(day|days|hour|hours|week|weeks|month|months)\s+of\s+(\w+)',
            r'(\w+)\s+since\s+(\d+)\s+(day|days|hour|hours|week|weeks|month|months)',
            r'(\w+)\s+lasting\s+(\d+)\s+(day|days|hour|hours|week|weeks|month|months)',
            r'(\w+)\s+\((\d+)\s+(day|days|hour|hours|week|weeks|month|months)\)',
            r'have\s+had\s+(\w+)\s+for\s+(\d+)\s+(day|days|hour|hours|week|weeks|month|months)',
            r'(\w+)\s+started\s+(\d+)\s+(day|days|hour|hours|week|weeks|month|months)\s+ago'
        ]

        # Look for duration patterns in the text
        for symptom, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    # Try to extract duration for this symptom
                    for pattern in duration_patterns:
                        matches = re.finditer(pattern, text)
                        for match in matches:
                            groups = match.groups()
                            
                            # Check if the symptom keyword matches the found pattern
                            if len(groups) >= 3:
                                if (groups[0] in keyword or keyword in groups[0] or 
                                    (len(groups) > 2 and (groups[2] in keyword or keyword in groups[2]))):
                                    duration_info[symptom] = f"{groups[1]} {groups[2]}"

        return duration_info

    def calculate_confidence_score(self, probabilities: np.ndarray) -> float:
        """Calculate our own custom confidence scoring algorithm"""
        max_prob = max(probabilities)
        second_max = sorted(probabilities)[-2] if len(probabilities) > 1 else 0
        confidence_gap = max_prob - second_max

        # Our proprietary confidence calculation
        adjusted_confidence = max_prob + (confidence_gap * 0.3)
        return min(adjusted_confidence, 1.0)

    def assess_severity(self, symptoms: Dict[str, int]) -> Tuple[str, float]:
        """Simplified severity assessment without duration consideration"""
        active_symptoms = sum(symptoms.values())
        total_symptoms = len(symptoms)

        # Base severity scoring
        severity_score = active_symptoms / total_symptoms if total_symptoms > 0 else 0

        # Additional weight for critical symptoms
        critical_symptoms = ['fever', 'shortness_of_breath', 'chest_pain', 'dizziness']
        critical_count = sum(1 for sym in critical_symptoms if symptoms.get(sym, 0) == 1)
        severity_score += critical_count * 0.15
        
        # Ensure score is within range
        severity_score = min(severity_score, 1.0)

        # Severity classification
        if severity_score <= 0.2:
            return "Mild", severity_score
        elif severity_score <= 0.4:
            return "Moderate", severity_score
        elif severity_score <= 0.7:
            return "Severe", severity_score
        else:
            return "Critical", severity_score

    def get_alternative_diagnoses(self, probabilities: np.ndarray, top_k: int = 3) -> List[Dict]:
        """Get top alternative diagnoses with our own ranking system"""
        top_indices = np.argsort(probabilities)[-top_k:][::-1]
        alternatives = []

        for idx in top_indices:
            diagnosis_name = self.label_encoder.inverse_transform([idx])[0]
            confidence = float(probabilities[idx])
            alternatives.append({
                "diagnosis": diagnosis_name,
                "confidence": confidence,
                "diagnosis_id": int(idx)
            })

        return alternatives

    def diagnose(self, user_input: str = None, symptoms: Dict[str, int] = None) -> Dict:
        """
        Main diagnosis function - completely self-contained AI!

        Args:
            user_input: Natural language description of symptoms
            symptoms: Dict with symptom flags {symptom_name: 0/1}

        Returns:
            Complete diagnosis result with prescriptions and recommendations
        """
        if not self.model:
            return {"error": "AI model not loaded properly"}

        # Parse symptoms from text or use provided symptoms
        if user_input:
            detected_symptoms = self.parse_symptoms_from_text(user_input)
            duration_info = self.extract_duration_info(user_input)
            input_method = "natural_language"
        elif symptoms:
            detected_symptoms = symptoms
            # Use stored duration_info from conversation if available
            duration_info = getattr(self, 'duration_info', {})
            input_method = "structured_input"
        else:
            return {"error": "No input provided"}

        # Convert to our model's input format (only basic symptoms)
        feature_vector = np.array([[float(detected_symptoms.get(f, 0)) for f in self.feature_names]])

        # Make prediction with our custom trained model
        prediction = self.model.predict(feature_vector)[0]
        probabilities = self.model.predict_proba(feature_vector)[0]

        # Handle both string labels and numeric predictions
        if isinstance(prediction, str):
            primary_diagnosis = prediction
        else:
            # Get primary diagnosis using our label encoder
            primary_diagnosis = self.label_encoder.inverse_transform([prediction])[0]

        # Calculate confidence with our custom algorithm
        confidence = self.calculate_confidence_score(probabilities)

        # Get alternative diagnoses
        alternatives = self.get_alternative_diagnoses(probabilities)

        # Assess severity with our custom algorithm
        severity, severity_score = self.assess_severity(detected_symptoms)

        # Get prescriptions from our database
        prescriptions = self.prescriptions_map.get(primary_diagnosis, {})
        
        # Generate duration insights from extracted duration info
        duration_insights = self._generate_duration_insights(duration_info, primary_diagnosis)

        # Build comprehensive result
        result = {
            "success": True,
            "primary_diagnosis": primary_diagnosis,
            "confidence": round(confidence * 100, 1),
            "confidence_raw": float(confidence),
            "severity": severity,
            "severity_score": round(severity_score, 3),
            "active_symptoms": sum(detected_symptoms.values()),
            "detected_symptoms": detected_symptoms,
            "duration_info": duration_info,
            "duration_insights": duration_insights,
            "alternative_diagnoses": alternatives,
            "prescriptions": prescriptions,
            "input_method": input_method,
            "ai_system": "MediChain AI v4.0 - Conversational with Natural Duration Detection",
            "recommendations": {
                "immediate_care": self._get_immediate_care_advice(severity, detected_symptoms),
                "follow_up": self._get_followup_advice(primary_diagnosis),
                "emergency_signs": self._get_emergency_signs()
            }
        }

        return result

    def _generate_duration_insights(self, duration_info: Dict[str, str], diagnosis: str) -> Dict:
        """Generate insights based on symptom durations from natural language"""
        insights = {
            "duration_analysis": [],
            "urgency_indicators": [],
            "duration_summary": "",
            "recommendations": []
        }
        
        if not duration_info:
            insights["duration_summary"] = "No specific duration information mentioned"
            return insights
        
        # Analyze each symptom duration
        duration_parts = []
        for symptom, duration_text in duration_info.items():
            symptom_display = symptom.replace('_', ' ').title()
            duration_parts.append(f"{symptom_display}: {duration_text}")
            
            # Parse for analysis
            if 'day' in duration_text:
                days = int(''.join(filter(str.isdigit, duration_text)))
                if days <= 3:
                    insights["duration_analysis"].append(f"{symptom_display}: Recent onset ({duration_text})")
                elif days <= 7:
                    insights["duration_analysis"].append(f"{symptom_display}: Short-term ({duration_text})")
                elif days <= 14:
                    insights["duration_analysis"].append(f"{symptom_display}: Extended duration ({duration_text})")
                    insights["urgency_indicators"].append(f"{symptom_display} persisting over 1 week")
                else:
                    insights["duration_analysis"].append(f"{symptom_display}: Persistent condition ({duration_text})")
                    insights["urgency_indicators"].append(f"{symptom_display} persisting over 2 weeks - medical evaluation recommended")
            
            elif 'week' in duration_text:
                weeks = int(''.join(filter(str.isdigit, duration_text)))
                if weeks >= 2:
                    insights["urgency_indicators"].append(f"{symptom_display} persisting for weeks - medical evaluation recommended")
            
            elif 'month' in duration_text:
                insights["urgency_indicators"].append(f"{symptom_display} chronic condition - ongoing medical care needed")
        
        # Create summary
        if duration_parts:
            insights["duration_summary"] = "Duration information: " + ", ".join(duration_parts)
        
        # Add recommendations based on duration
        if insights["urgency_indicators"]:
            insights["recommendations"].append("Consider medical evaluation due to symptom duration")
        else:
            insights["recommendations"].append("Monitor symptoms and seek care if they worsen or persist")
            
        return insights

    def _get_immediate_care_advice(self, severity: str, symptoms: Dict[str, int]) -> str:
        """Generate immediate care advice based on severity"""
        if severity == "Critical":
            return "Seek immediate emergency medical attention. Critical symptoms detected."
        elif severity == "Severe":
            return "Seek urgent medical attention. Severe symptoms require evaluation."
        elif severity == "Moderate":
            return "Consider consulting a healthcare provider soon. Monitor symptoms closely."
        else:
            return "Rest, stay hydrated, and monitor symptoms. Seek care if worsening or persisting."

    def _get_followup_advice(self, diagnosis: str) -> str:
        """Generate follow-up advice based on diagnosis"""
        if "infection" in diagnosis.lower():
            return "Follow up if symptoms persist beyond expected duration or worsen."
        else:
            return "Monitor symptoms and follow prescribed treatment plan."

    def _get_emergency_signs(self) -> List[str]:
        """Emergency warning signs from our medical knowledge base"""
        return [
            "Difficulty breathing or shortness of breath",
            "High fever >103°F (39.4°C)",
            "Chest pain or pressure",
            "Severe dehydration",
            "Persistent vomiting",
            "Signs of serious infection"
        ]

    def get_system_info(self) -> Dict:
        """Get information about our custom AI system"""
        return {
            "system_name": "MediChain Conversational AI",
            "version": "4.0",
            "model_type": "Custom Random Forest Classifier (Conversational-Optimized)",
            "total_conditions": len(self.label_encoder.classes_) if self.label_encoder else 0,
            "symptom_features": len(self.feature_names) if self.feature_names else 0,
            "prescription_database": len(self.prescriptions_map) if self.prescriptions_map else 0,
            "external_dependencies": "None - 100% Self-Contained!",
            "capabilities": [
                "Conversational diagnosis with follow-up questions",
                "Natural language symptom parsing", 
                "Duration extraction from text",
                "Multi-class medical diagnosis",
                "Custom confidence scoring",
                "Severity assessment",
                "Prescription recommendations",
                "Alternative diagnosis suggestions",
                "Uncertainty handling (I don't know responses)",
                "Progressive information gathering"
            ]
        }

    # Conversational Diagnosis Methods
    def start_conversation(self, initial_symptoms: str) -> Dict:
        """Start a conversational diagnosis session"""
        self.conversation_history = []
        self.gathered_symptoms = {}
        self.follow_up_questions = []
        
        # Parse initial symptoms and extract duration info
        detected_symptoms = self.parse_symptoms_from_text(initial_symptoms)
        self.gathered_symptoms.update(detected_symptoms)
        
        # Extract duration information from initial input
        self.duration_info = self.extract_duration_info(initial_symptoms)
        
        # Add to conversation history
        self.conversation_history.append({
            'type': 'user_input',
            'content': initial_symptoms,
            'symptoms_detected': list(detected_symptoms.keys())
        })
        
        # Generate follow-up questions based on detected symptoms
        next_question = self._generate_next_question()
        
        return {
            'conversation_id': len(self.conversation_history),
            'detected_symptoms': detected_symptoms,
            'duration_info': self.duration_info,
            'next_question': next_question,
            'conversation_stage': 'gathering_info',
            'progress': self._calculate_conversation_progress()
        }
    
    def continue_conversation(self, user_response: str, question_id: str = None) -> Dict:
        """Continue the conversation with user response"""
        # Process the response
        processed_response = self._process_user_response(user_response, question_id)
        
        # Add to conversation history
        self.conversation_history.append({
            'type': 'user_response',
            'content': user_response,
            'question_id': question_id,
            'processed_info': processed_response
        })
        
        # Update gathered symptoms/info
        if processed_response.get('symptoms'):
            self.gathered_symptoms.update(processed_response['symptoms'])
        
        # Check if we have enough information for diagnosis
        if self._has_sufficient_info():
            # Provide final diagnosis
            diagnosis_result = self.diagnose(symptoms=self.gathered_symptoms)
            diagnosis_result['conversation_stage'] = 'diagnosis_complete'
            diagnosis_result['conversation_history'] = self.conversation_history
            diagnosis_result['duration_info'] = getattr(self, 'duration_info', {})
            return diagnosis_result
        else:
            # Generate next question
            next_question = self._generate_next_question()
            return {
                'conversation_id': len(self.conversation_history),
                'next_question': next_question,
                'conversation_stage': 'gathering_info',
                'progress': self._calculate_conversation_progress(),
                'gathered_info': self.gathered_symptoms,
                'duration_info': getattr(self, 'duration_info', {})
            }
    
    def _generate_next_question(self) -> Dict:
        """Generate the next appropriate question based on current symptoms"""
        # Check what symptoms we have and what questions we need to ask
        detected_symptom_names = [k for k, v in self.gathered_symptoms.items() if v == 1]
        
        # Priority order for questions (removed duration questions - duration extracted from text)
        question_priority = [
            ('fever', 'fever_severity'),
            ('cough', 'cough_type'),
            ('headache', 'pain_location'),
            ('shortness_of_breath', 'breathing_difficulty'),
            ('nausea', 'nausea_triggers')
        ]
        
        # Find the first appropriate question to ask
        for symptom, question_key in question_priority:
            if symptom in detected_symptom_names and question_key not in self.follow_up_questions:
                self.follow_up_questions.append(question_key)
                question_data = self.question_templates[question_key].copy()
                question_data['question_id'] = question_key
                return question_data
        
        # If no specific questions, ask about additional symptoms
        if 'additional_symptoms' not in self.follow_up_questions:
            self.follow_up_questions.append('additional_symptoms')
            question_data = self.question_templates['additional_symptoms'].copy()
            question_data['question_id'] = 'additional_symptoms'
            return question_data
        
        # No more questions needed
        return None
    
    def _process_user_response(self, response: str, question_id: str) -> Dict:
        """Process user response and extract relevant information"""
        response_lower = response.lower()
        processed = {'symptoms': {}, 'details': {}}
        
        # Handle "I don't know" or similar responses
        if any(phrase in response_lower for phrase in ["i don't know", "i can't remember", "not sure", "i'm not sure", "don't remember"]):
            processed['details']['uncertainty'] = True
            processed['details']['response_type'] = 'uncertain'
            return processed
        
        # Process based on question type
        if question_id and question_id in self.question_templates:
            template = self.question_templates[question_id]
            
            # Check if response matches any of the options
            for option in template['options']:
                if option.lower() in response_lower:
                    processed['details']['selected_option'] = option
                    break
            
            # Extract specific information based on question type
            if 'fever' in question_id:
                if 'high' in response_lower or '103' in response_lower:
                    processed['details']['fever_severity'] = 'high'
                elif 'moderate' in response_lower or '101' in response_lower or '102' in response_lower:
                    processed['details']['fever_severity'] = 'moderate'
                elif 'low' in response_lower or '99' in response_lower or '100' in response_lower:
                    processed['details']['fever_severity'] = 'low'
                    
            elif 'cough' in question_id:
                if 'dry' in response_lower:
                    processed['details']['cough_type'] = 'dry'
                elif 'wet' in response_lower or 'productive' in response_lower:
                    processed['details']['cough_type'] = 'productive'
                elif 'blood' in response_lower:
                    processed['details']['cough_type'] = 'blood'
                    processed['details']['severity_flag'] = 'high'
                    
            elif 'pain' in question_id:
                if any(num in response_lower for num in ['7', '8', '9', '10']):
                    processed['details']['pain_severity'] = 'severe'
                elif any(num in response_lower for num in ['4', '5', '6']):
                    processed['details']['pain_severity'] = 'moderate'
                elif any(num in response_lower for num in ['1', '2', '3']):
                    processed['details']['pain_severity'] = 'mild'
        
        # Also try to detect any new symptoms mentioned
        new_symptoms = self.parse_symptoms_from_text(response)
        processed['symptoms'].update(new_symptoms)
        
        return processed
    
    def _has_sufficient_info(self) -> bool:
        """Check if we have enough information to make a diagnosis"""
        # Need at least 2 symptoms or have asked 2+ questions
        symptom_count = sum(self.gathered_symptoms.values())
        question_count = len(self.follow_up_questions)
        
        # If we have multiple symptoms or have asked several questions, we can proceed
        return symptom_count >= 2 or question_count >= 2
    
    def _calculate_conversation_progress(self) -> int:
        """Calculate how much information we've gathered (0-100%)"""
        symptom_count = sum(self.gathered_symptoms.values())
        question_count = len(self.follow_up_questions)
        
        # Simple progress calculation
        progress = min(100, (symptom_count * 20) + (question_count * 15))
        return progress

# Quick test function for Flask integration
def quick_test():
    """Quick test of the AI system"""
    ai = MediChainAI()
    result = ai.diagnose(user_input="I have fever and cough")
    return result

if __name__ == "__main__":
    # Test the system when run directly
    print("Testing MediChain Custom AI...")
    result = quick_test()
    if "error" not in result:
        print(f"✅ AI Test Successful!")
        print(f"Diagnosis: {result['primary_diagnosis']}")
        print(f"Confidence: {result['confidence']}%")
    else:
        print(f"❌ Test Failed: {result['error']}")
