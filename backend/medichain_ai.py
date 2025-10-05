
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
    """

    def __init__(self, model_path: str = "."):
        """Initialize the AI system with model files"""
        self.model_path = model_path
        self.model = None
        self.label_encoder = None
        self.feature_names = None
        self.prescriptions_map = None

        # Our custom symptom keyword database - no external NLP needed!
        self.symptom_keywords = {
            'fever': ['fever', 'hot', 'temperature', 'burning up', 'chills', 'feverish', 'high temp', 'pyrexia', 'febrile'],
            'cough': ['cough', 'coughing', 'hack', 'wheeze', 'phlegm', 'mucus', 'chest congestion', 'productive cough', 'dry cough'],
            'fatigue': ['tired', 'fatigue', 'exhausted', 'weak', 'weary', 'drained', 'lethargic', 'sleepy', 'worn out', 'energy'],
            'shortness_of_breath': ['breathless', 'short of breath', 'breathing difficulty', 'wheezing', 'gasping', 'chest tight', 'dyspnea', 'winded'],
            'headache': ['headache', 'head pain', 'migraine', 'head pressure', 'skull pain', 'temple pain', 'cephalgia', 'head ache'],
            'sore_throat': ['sore throat', 'throat pain', 'scratchy throat', 'swollen throat', 'throat irritation', 'pharyngitis', 'throat ache']
        }

        self.load_model()

    def load_model(self):
        """Load our custom trained AI model and components"""
        try:
            self.model = joblib.load(os.path.join(self.model_path, "enhanced_diagnosis_model.pkl"))
            self.label_encoder = joblib.load(os.path.join(self.model_path, "enhanced_label_encoder.pkl"))
            self.feature_names = joblib.load(os.path.join(self.model_path, "enhanced_feature_names.pkl"))
            self.prescriptions_map = joblib.load(os.path.join(self.model_path, "enhanced_prescriptions_map.pkl"))
            return True
        except Exception as e:
            print(f"Error loading MediChain AI model: {e}")
            return False

    def parse_symptoms_from_text(self, text: str) -> Dict[str, int]:
        """
        Parse natural language text to detect symptoms
        Our own custom NLP system - no external APIs!
        """
        text = text.lower()
        detected_symptoms = {}

        for symptom, keywords in self.symptom_keywords.items():
            detected_symptoms[symptom] = 0
            for keyword in keywords:
                if keyword in text:
                    detected_symptoms[symptom] = 1
                    break

        return detected_symptoms

    def calculate_confidence_score(self, probabilities: np.ndarray) -> float:
        """Calculate our own custom confidence scoring algorithm"""
        max_prob = max(probabilities)
        second_max = sorted(probabilities)[-2] if len(probabilities) > 1 else 0
        confidence_gap = max_prob - second_max

        # Our proprietary confidence calculation
        adjusted_confidence = max_prob + (confidence_gap * 0.3)
        return min(adjusted_confidence, 1.0)

    def assess_severity(self, symptoms: Dict[str, int]) -> Tuple[str, float]:
        """Our own severity assessment algorithm"""
        active_symptoms = sum(symptoms.values())
        total_symptoms = len(symptoms)

        # Custom severity scoring with medical knowledge
        severity_score = active_symptoms / total_symptoms

        # Additional weight for critical symptoms
        critical_symptoms = ['fever', 'shortness_of_breath']
        critical_count = sum(1 for sym in critical_symptoms if symptoms.get(sym, 0) == 1)
        severity_score += critical_count * 0.15

        severity_score = min(severity_score, 1.0)

        if severity_score <= 0.25:
            return "Mild", severity_score
        elif severity_score <= 0.55:
            return "Moderate", severity_score
        else:
            return "Severe", severity_score

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
            input_method = "natural_language"
        elif symptoms:
            detected_symptoms = symptoms
            input_method = "structured_input"
        else:
            return {"error": "No input provided"}

        # Convert to our model's input format
        feature_vector = np.array([[float(detected_symptoms.get(f, 0)) for f in self.feature_names]])

        # Make prediction with our custom trained model
        prediction_id = self.model.predict(feature_vector)[0]
        probabilities = self.model.predict_proba(feature_vector)[0]

        # Get primary diagnosis using our label encoder
        primary_diagnosis = self.label_encoder.inverse_transform([prediction_id])[0]

        # Calculate confidence with our custom algorithm
        confidence = self.calculate_confidence_score(probabilities)

        # Get alternative diagnoses
        alternatives = self.get_alternative_diagnoses(probabilities)

        # Assess severity with our custom algorithm
        severity, severity_score = self.assess_severity(detected_symptoms)

        # Get prescriptions from our database
        prescriptions = self.prescriptions_map.get(prediction_id, [])

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
            "alternative_diagnoses": alternatives,
            "prescriptions": prescriptions,
            "input_method": input_method,
            "ai_system": "MediChain Custom AI v2.0 - Self Contained",
            "recommendations": {
                "immediate_care": self._get_immediate_care_advice(severity, detected_symptoms),
                "follow_up": self._get_followup_advice(primary_diagnosis),
                "emergency_signs": self._get_emergency_signs()
            }
        }

        return result

    def _get_immediate_care_advice(self, severity: str, symptoms: Dict[str, int]) -> str:
        """Generate immediate care advice based on our medical knowledge"""
        if severity == "Severe":
            return "Seek immediate medical attention. Monitor symptoms closely."
        elif severity == "Moderate":
            return "Consider consulting a healthcare provider. Rest and monitor symptoms."
        else:
            return "Rest, stay hydrated, and monitor symptoms. Seek care if worsening."

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
            "system_name": "MediChain Custom AI",
            "version": "2.0",
            "model_type": "Custom Random Forest Classifier",
            "total_conditions": len(self.label_encoder.classes_) if self.label_encoder else 0,
            "symptom_features": len(self.feature_names) if self.feature_names else 0,
            "prescription_database": len(self.prescriptions_map) if self.prescriptions_map else 0,
            "external_dependencies": "None - 100% Self-Contained!",
            "capabilities": [
                "Natural language symptom parsing",
                "Multi-class medical diagnosis",
                "Custom confidence scoring",
                "Severity assessment", 
                "Prescription recommendations",
                "Alternative diagnosis suggestions"
            ]
        }

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
