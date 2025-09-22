#!/usr/bin/env python3
"""
Enhanced Confident AI Server with Confidence Boosting
Improved confidence mechanisms without ensemble complexity
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import numpy as np
from datetime import datetime
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the existing diagnosis system
from comprehensive_ai_diagnosis import ComprehensiveAIDiagnosis
from medical_recommendations import get_personalized_recommendations

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global AI diagnosis instance
ai_diagnosis = None

class ConfidenceBooster:
    """Enhanced confidence boosting mechanisms"""
    
    def __init__(self):
        self.confidence_multipliers = {
            'high_symptom_count': 1.20,      # 4+ symptoms
            'medium_symptom_count': 1.10,    # 3 symptoms
            'duration_specified': 1.15,      # Clear duration
            'intensity_specified': 1.12,     # Clear intensity
            'symptom_combinations': 1.18,    # Known patterns
            'manual_input': 1.08,            # User provided details
            'keyword_confidence': 1.05       # Confidence keywords
        }
        
        # Known high-confidence symptom combinations
        self.confident_combinations = [
            ['fever', 'cough', 'fatigue'],                    # Flu-like
            ['headache', 'nausea', 'dizziness'],             # Migraine
            ['chest_pain', 'shortness_of_breath'],           # Respiratory
            ['loss_of_taste', 'loss_of_smell'],              # COVID-like
            ['sore_throat', 'fever', 'body_aches'],          # Strep-like
            ['diarrhea', 'nausea', 'fatigue'],               # GI issues
            ['runny_nose', 'sore_throat', 'cough']           # Cold-like
        ]
    
    def boost_confidence(self, base_confidence, parsed_result, feature_vector):
        """Apply confidence boosting based on various factors"""
        
        boosted_confidence = base_confidence
        applied_boosts = []
        
        # 1. Symptom count boost
        symptoms = parsed_result['symptoms']
        
        # Handle both list and dict formats
        if isinstance(symptoms, list):
            symptom_count = len(symptoms)
            active_symptoms = symptoms
        elif isinstance(symptoms, dict):
            symptom_count = sum(symptoms.values())
            active_symptoms = [k for k, v in symptoms.items() if v == 1]
        else:
            symptom_count = 0
            active_symptoms = []
        
        if symptom_count >= 4:
            boosted_confidence *= self.confidence_multipliers['high_symptom_count']
            applied_boosts.append(f"High symptom count ({symptom_count})")
        elif symptom_count >= 3:
            boosted_confidence *= self.confidence_multipliers['medium_symptom_count']
            applied_boosts.append(f"Medium symptom count ({symptom_count})")
        
        # 2. Duration and intensity boost
        duration_days = parsed_result.get('duration_days', 0)
        intensity = parsed_result.get('intensity', '')
        
        if duration_days > 0 and duration_days != 3:  # 3 is default
            boosted_confidence *= self.confidence_multipliers['duration_specified']
            applied_boosts.append(f"Duration specified ({duration_days} days)")
        
        if intensity and intensity != 'moderate':  # moderate is default
            boosted_confidence *= self.confidence_multipliers['intensity_specified'] 
            applied_boosts.append(f"Intensity specified ({intensity})")
        
        # 3. Symptom combination patterns
        for combo in self.confident_combinations:
            if all(symptom in active_symptoms for symptom in combo):
                boosted_confidence *= self.confidence_multipliers['symptom_combinations']
                applied_boosts.append(f"Known pattern: {', '.join(combo)}")
                break
        
        # 4. Manual input boost
        if parsed_result.get('manual_duration_override') or parsed_result.get('manual_intensity_override'):
            boosted_confidence *= self.confidence_multipliers['manual_input']
            applied_boosts.append("Manual input provided")
        
        # 5. Confidence keywords boost
        confidence_keywords = parsed_result.get('confidence_keywords_found', 0)
        if confidence_keywords > 0:
            boost = min(self.confidence_multipliers['keyword_confidence'] ** confidence_keywords, 1.10)
            boosted_confidence *= boost
            applied_boosts.append(f"Confidence keywords ({confidence_keywords})")
        
        # Cap at 0.95 (never 100% certain in medicine)
        boosted_confidence = min(boosted_confidence, 0.95)
        
        return boosted_confidence, applied_boosts
    
    def get_confidence_level(self, confidence):
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

# Initialize confidence booster
confidence_booster = ConfidenceBooster()

def initialize_ai_system():
    """Initialize the AI diagnosis system with confidence boosting"""
    global ai_diagnosis
    
    try:
        print("🚀 Starting Enhanced Confident AI Medical Diagnosis Server")
        print("="*60)
        
        # Initialize AI diagnosis system
        ai_diagnosis = ComprehensiveAIDiagnosis()
        
        logger.info("✅ Enhanced confident AI diagnosis system initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize AI system: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_system': 'ready' if ai_diagnosis else 'not_ready',
        'confidence_boosting': 'enabled'
    })

@app.route('/model/info', methods=['GET'])
def model_info():
    """Get model information with confidence details"""
    if not ai_diagnosis:
        return jsonify({'error': 'AI system not initialized'}), 500
    
    return jsonify({
        'features': len(ai_diagnosis.feature_names),
        'diagnoses': len(ai_diagnosis.label_encoder.classes_),
        'confidence_boosting': 'enabled',
        'confidence_mechanisms': list(confidence_booster.confidence_multipliers.keys()),
        'dataset_info': 'Enhanced dataset with confidence features'
    })

@app.route('/diagnose-enhanced', methods=['POST'])
def enhanced_confident_diagnosis():
    """Enhanced diagnosis with confidence boosting"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        symptoms_text = data.get('symptoms', '')
        duration_text = data.get('duration', '')
        intensity_text = data.get('intensity', '')
        manual_duration_days = data.get('manual_duration_days')
        manual_intensity = data.get('manual_intensity')
        
        if not symptoms_text:
            return jsonify({'error': 'Symptoms are required'}), 400
        
        logger.info(f"Enhanced confident diagnosis request: {symptoms_text[:100]}...")
        
        # Get base diagnosis
        result = ai_diagnosis.diagnose(symptoms_text, duration_text, intensity_text)
        
        # Apply manual overrides
        original_duration = result['duration_days']
        original_intensity = result['intensity']
        
        if manual_duration_days is not None:
            result['duration_days'] = manual_duration_days
            result['manual_duration_override'] = True
        
        if manual_intensity is not None:
            result['intensity'] = manual_intensity
            result['manual_intensity_override'] = True
        
        # Create enhanced parsed result for confidence boosting
        enhanced_parsed_result = {
            'symptoms': result['parsed_symptoms'],
            'duration_days': result['duration_days'],
            'intensity': result['intensity'],
            'manual_duration_override': result.get('manual_duration_override', False),
            'manual_intensity_override': result.get('manual_intensity_override', False),
            'confidence_keywords_found': _count_confidence_keywords(symptoms_text + " " + duration_text + " " + intensity_text)
        }
        
        # Apply confidence boosting
        base_confidence = result['confidence']
        boosted_confidence, applied_boosts = confidence_booster.boost_confidence(
            base_confidence, enhanced_parsed_result, list(result['feature_vector'].values())
        )
        
        # Update confidence in result
        result['confidence'] = boosted_confidence
        result['base_confidence'] = base_confidence
        result['confidence_level'] = confidence_booster.get_confidence_level(boosted_confidence)
        result['confidence_boosts_applied'] = applied_boosts
        
        # Boost top predictions proportionally
        for prediction in result['top_predictions']:
            if prediction['diagnosis'] == result['primary_diagnosis']:
                prediction['confidence'] = boosted_confidence
            else:
                # Apply smaller boost to other predictions
                boost_ratio = boosted_confidence / base_confidence if base_confidence > 0 else 1.0
                prediction['confidence'] = min(prediction['confidence'] * (boost_ratio * 0.8), 0.90)
        
        # Sort top predictions by new confidence
        result['top_predictions'].sort(key=lambda x: x['confidence'], reverse=True)
        
        # Determine if duration and intensity were auto-detected
        duration_auto_detected = ai_diagnosis.symptom_parser._was_duration_detected(symptoms_text + " " + duration_text)
        intensity_auto_detected = ai_diagnosis.symptom_parser._was_intensity_detected(symptoms_text + " " + intensity_text)
        
        # Get medical recommendations
        try:
            recommendations = get_personalized_recommendations(
                result['primary_diagnosis'], 
                {'symptoms': result['parsed_symptoms']}
            )
            result['recommendations'] = recommendations
        except Exception as e:
            logger.warning(f"Could not get recommendations: {e}")
            result['recommendations'] = {
                'medications': ['Consult healthcare provider'],
                'lifestyle': ['Rest and monitor symptoms'],
                'when_to_see_doctor': ['If symptoms worsen or persist']
            }
        
        # Enhanced analysis summary
        parsed_symptoms = result['parsed_symptoms']
        if isinstance(parsed_symptoms, list):
            symptoms_detected_count = len(parsed_symptoms)
        elif isinstance(parsed_symptoms, dict):
            symptoms_detected_count = len([s for s in parsed_symptoms.values() if s == 1])
        else:
            symptoms_detected_count = 0
            
        result['analysis_summary'] = {
            'symptoms_detected': symptoms_detected_count,
            'duration_extracted': f"{result['duration_days']} days",
            'intensity_detected': result['intensity'],
            'confidence_level': result['confidence_level'],
            'duration_auto_detected': duration_auto_detected,
            'intensity_auto_detected': intensity_auto_detected,
            'needs_duration_input': not duration_auto_detected and not result.get('manual_duration_override', False),
            'needs_intensity_input': not intensity_auto_detected and not result.get('manual_intensity_override', False),
            'original_duration': original_duration,
            'original_intensity': original_intensity,
            'manual_overrides_applied': result.get('manual_duration_override', False) or result.get('manual_intensity_override', False),
            'confidence_improvement': f"+{((boosted_confidence - base_confidence) * 100):.1f}%" if boosted_confidence > base_confidence else "No boost applied"
        }
        
        logger.info(f"Enhanced confident diagnosis complete: {result['primary_diagnosis']} (confidence: {boosted_confidence:.3f}, level: {result['confidence_level']})")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in enhanced confident diagnosis: {e}")
        return jsonify({'error': f'Enhanced confident diagnosis failed: {str(e)}'}), 500

@app.route('/diagnose', methods=['POST'])
def confident_diagnosis():
    """Standard diagnosis endpoint with confidence boosting"""
    return enhanced_confident_diagnosis()

def _count_confidence_keywords(text):
    """Count confidence-indicating keywords"""
    confidence_keywords = [
        'definitely', 'certainly', 'absolutely', 'clearly', 'obviously',
        'really', 'very', 'extremely', 'quite', 'pretty', 'fairly',
        'severe', 'intense', 'terrible', 'awful', 'horrible'
    ]
    count = 0
    text_lower = text.lower()
    for keyword in confidence_keywords:
        if keyword in text_lower:
            count += 1
    return count

@app.route('/chat', methods=['POST'])
def conversational_diagnosis():
    """Conversational diagnosis with confidence boosting"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Use enhanced diagnosis for chat
        enhanced_data = {'symptoms': message, 'duration': '', 'intensity': ''}
        
        # Temporarily modify request data for reuse
        original_json = request.get_json
        request.get_json = lambda: enhanced_data
        
        response = enhanced_confident_diagnosis()
        
        # Restore original method
        request.get_json = original_json
        
        return response
        
    except Exception as e:
        logger.error(f"Error in conversational diagnosis: {e}")
        return jsonify({'error': f'Conversational diagnosis failed: {str(e)}'}), 500

if __name__ == '__main__':
    if initialize_ai_system():
        print("✅ AI system initialized successfully")
        print("🌐 Server starting on http://localhost:5001")
        print("📋 Available endpoints:")
        print("  - POST /diagnose-enhanced - Enhanced confident diagnosis")
        print("  - POST /diagnose - Standard confident diagnosis")
        print("  - POST /chat - Conversational confident diagnosis")
        print("  - GET /health - Health check")
        print("  - GET /model/info - Model information")
        print("="*60)
        app.run(host='0.0.0.0', port=5001, debug=True)
    else:
        print("❌ Failed to initialize AI system")
        exit(1)
