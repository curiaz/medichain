#!/usr/bin/env python3
"""
Fixed AI Server with Error Handling
Handles sklearn version incompatibility and provides fallback responses
"""

import logging
import os
import sys
from datetime import datetime

from flask import Flask, jsonify, request
from flask_cors import CORS

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fallback diagnosis database for when ML model fails
FALLBACK_DIAGNOSES = {
    # Common symptom patterns and their likely diagnoses
    ("fever", "cough", "fatigue"): {
        "diagnosis": "Common Cold or Flu",
        "confidence": 0.78,
        "recommendations": {
            "medications": ["Rest", "Fluids", "Acetaminophen for fever"],
            "lifestyle": [
                "Stay hydrated",
                "Get plenty of rest",
                "Isolate if contagious",
            ],
            "when_to_see_doctor": [
                "If fever over 101.5°F persists",
                "Difficulty breathing",
                "Symptoms worsen after 7 days",
            ],
        },
    },
    ("headache", "nausea", "dizziness"): {
        "diagnosis": "Migraine or Tension Headache",
        "confidence": 0.72,
        "recommendations": {
            "medications": ["Ibuprofen", "Rest in dark room", "Cold compress"],
            "lifestyle": [
                "Avoid bright lights",
                "Stay hydrated",
                "Regular sleep schedule",
            ],
            "when_to_see_doctor": [
                "Severe headache with fever",
                "Vision changes",
                "Persistent nausea",
            ],
        },
    },
    ("sore_throat", "fever", "body_aches"): {
        "diagnosis": "Strep Throat or Viral Infection",
        "confidence": 0.75,
        "recommendations": {
            "medications": [
                "Throat lozenges",
                "Warm salt water gargle",
                "Pain relievers",
            ],
            "lifestyle": ["Rest", "Warm liquids", "Humidifier"],
            "when_to_see_doctor": [
                "White patches in throat",
                "High fever",
                "Difficulty swallowing",
            ],
        },
    },
    ("chest_pain", "shortness_of_breath"): {
        "diagnosis": "Respiratory Condition - SEEK IMMEDIATE CARE",
        "confidence": 0.85,
        "recommendations": {
            "medications": ["SEEK IMMEDIATE MEDICAL ATTENTION"],
            "lifestyle": [
                "Do not delay medical care",
                "Call emergency services if severe",
            ],
            "when_to_see_doctor": ["IMMEDIATELY - Chest pain with breathing difficulty requires urgent evaluation"],
        },
    },
    ("diarrhea", "nausea", "fatigue"): {
        "diagnosis": "Gastroenteritis",
        "confidence": 0.73,
        "recommendations": {
            "medications": ["Clear fluids", "BRAT diet", "Electrolyte replacement"],
            "lifestyle": [
                "Rest",
                "Avoid dairy and fatty foods",
                "Gradual diet reintroduction",
            ],
            "when_to_see_doctor": [
                "Severe dehydration",
                "Blood in stool",
                "High fever with symptoms",
            ],
        },
    },
}


def extract_symptoms_from_text(text):
    """Extract symptoms from natural language text"""
    text_lower = text.lower()

    symptom_keywords = {
        "fever": ["fever", "high temperature", "hot", "burning up"],
        "cough": ["cough", "coughing", "hacking"],
        "fatigue": ["tired", "fatigue", "exhausted", "weak", "weary"],
        "headache": ["headache", "head pain", "head hurts"],
        "sore_throat": ["sore throat", "throat pain", "scratchy throat"],
        "nausea": ["nausea", "nauseous", "sick to stomach", "queasy"],
        "dizziness": ["dizzy", "dizziness", "lightheaded", "spinning"],
        "body_aches": ["body aches", "muscle pain", "aching", "sore muscles"],
        "chest_pain": ["chest pain", "chest hurts", "chest pressure"],
        "shortness_of_breath": [
            "shortness of breath",
            "breathing difficulty",
            "cant breathe",
            "hard to breathe",
        ],
        "diarrhea": ["diarrhea", "loose stool", "runny stool"],
        "runny_nose": ["runny nose", "nasal congestion", "stuffy nose"],
    }

    detected_symptoms = []
    for symptom, keywords in symptom_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_symptoms.append(symptom)

    return detected_symptoms


def find_best_match(symptoms):
    """Find the best matching diagnosis from fallback database"""
    best_match = None
    best_score = 0

    for pattern, diagnosis_info in FALLBACK_DIAGNOSES.items():
        # Calculate match score
        matches = sum(1 for symptom in pattern if symptom in symptoms)
        score = matches / len(pattern) if pattern else 0

        if score > best_score and matches >= 2:  # At least 2 symptoms must match
            best_match = diagnosis_info
            best_score = score

    return best_match, best_score


@app.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "service": "AI Medical Diagnosis (Fallback Mode)",
            "message": "AI server running with fallback diagnosis system",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/diagnose", methods=["POST"])
@app.route("/diagnose-enhanced", methods=["POST"])
def diagnose():
    """Main diagnosis endpoint with fallback logic"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        symptoms_text = data.get("symptoms", "")
        # Duration and intensity analysis could be added here
        # duration_text = data.get("duration", "")
        # intensity_text = data.get("intensity", "")

        if not symptoms_text:
            return jsonify({"error": "Symptoms are required"}), 400

        logger.info(f"Diagnosis request: {symptoms_text[:100]}...")

        # Extract symptoms from text
        detected_symptoms = extract_symptoms_from_text(symptoms_text)

        if not detected_symptoms:
            return (
                jsonify(
                    {
                        "error": "No recognizable symptoms found",
                        "message": "Please describe your symptoms more clearly",
                        "suggestions": ["Try describing symptoms like: fever, cough, headache, nausea, etc."],
                    }
                ),
                400,
            )

        # Find best matching diagnosis
        best_match, match_score = find_best_match(detected_symptoms)

        if not best_match:
            # Generic response for unmatched symptoms
            best_match = {
                "diagnosis": "Unspecified Condition",
                "confidence": 0.60,
                "recommendations": {
                    "medications": [
                        "Monitor symptoms",
                        "Over-the-counter pain relief if needed",
                    ],
                    "lifestyle": ["Rest", "Stay hydrated", "Monitor for changes"],
                    "when_to_see_doctor": [
                        "If symptoms worsen",
                        "If symptoms persist beyond 7 days",
                        "If new symptoms develop",
                    ],
                },
            }

        # Adjust confidence based on match quality
        final_confidence = best_match["confidence"] * (0.7 + 0.3 * match_score)

        # Determine confidence level
        if final_confidence >= 0.80:
            confidence_level = "High"
        elif final_confidence >= 0.65:
            confidence_level = "Moderate"
        else:
            confidence_level = "Low"

        # Create response
        response = {
            "primary_diagnosis": best_match["diagnosis"],
            "confidence": final_confidence,
            "confidence_level": confidence_level,
            "detected_symptoms": detected_symptoms,
            "recommendations": best_match["recommendations"],
            "analysis_summary": {
                "symptoms_detected": len(detected_symptoms),
                "pattern_match_score": match_score,
                "processing_mode": "Fallback Analysis (ML model unavailable)",
            },
            "top_predictions": [
                {
                    "diagnosis": best_match["diagnosis"],
                    "confidence": final_confidence,
                    "probability": final_confidence * 100,
                }
            ],
            "metadata": {
                "is_fallback": True,
                "ml_model_available": False,
                "timestamp": datetime.now().isoformat(),
            },
            "disclaimer": (
                "This is a preliminary assessment. Please consult a healthcare "
                "professional for proper diagnosis and treatment."
            ),
        }

        logger.info(f"Fallback diagnosis: {best_match['diagnosis']} " f"(confidence: {final_confidence:.3f})")

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in diagnosis: {e}")
        return (
            jsonify(
                {
                    "error": "Diagnosis system temporarily unavailable",
                    "message": "Please try again later or consult a healthcare professional",
                    "details": str(e),
                }
            ),
            500,
        )


@app.route("/chat", methods=["POST"])
def chat():
    """Conversational diagnosis endpoint"""
    return diagnose()  # Use same logic for now


@app.route("/model/info")
def model_info():
    """Model information endpoint"""
    return jsonify(
        {
            "model_status": "Fallback Mode",
            "reason": "Primary ML model unavailable due to sklearn version incompatibility",
            "available_features": [
                "Symptom pattern matching",
                "Basic diagnosis suggestions",
            ],
            "supported_symptoms": list(set([symptom for pattern in FALLBACK_DIAGNOSES.keys() for symptom in pattern])),
            "fallback_diagnoses": len(FALLBACK_DIAGNOSES),
        }
    )


if __name__ == "__main__":
    print("🚀 Starting AI Medical Diagnosis Server (Fallback Mode)")
    print("=" * 60)
    print("⚠️ NOTE: Running in fallback mode due to ML model compatibility issues")
    print("✅ Fallback diagnosis system initialized successfully")
    print("🌐 Server starting on http://localhost:5001")
    print("📋 Available endpoints:")
    print("  - POST /diagnose - Fallback diagnosis")
    print("  - POST /diagnose-enhanced - Enhanced fallback diagnosis")
    print("  - POST /chat - Conversational diagnosis")
    print("  - GET /health - Health check")
    print("  - GET /model/info - Model information")
    print("=" * 60)

    try:
        app.run(host="0.0.0.0", port=5001, debug=True)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
