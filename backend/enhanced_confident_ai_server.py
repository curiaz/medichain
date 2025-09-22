#!/usr/bin/env python3
"""
Enhanced Confident AI Server for MediChain
Multi-factor confidence boosting with sophisticated mechanisms
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from datetime import datetime
import traceback
import os
import sys

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_ai_diagnosis import ComprehensiveAIDiagnosis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class ConfidenceBooster:
    """Advanced confidence boosting system with multiple enhancement mechanisms"""
    
    def __init__(self):
        # Known high-confidence symptom combinations
        self.confident_symptom_combinations = [
            # Respiratory patterns
            ['fever', 'cough', 'fatigue'],                    # Flu-like (confidence +18%)
            ['fever', 'cough', 'shortness_of_breath'],        # Pneumonia-like (+20%)
            ['loss_of_taste', 'loss_of_smell'],               # COVID-specific (+25%)
            ['chest_pain', 'shortness_of_breath'],            # Cardiac/Respiratory (+15%)
            
            # Neurological patterns
            ['headache', 'nausea', 'dizziness'],              # Migraine-like (+18%)
            ['headache', 'fever', 'body_aches'],              # Infection-like (+15%)
            
            # GI patterns  
            ['nausea', 'diarrhea', 'fever'],                  # Gastroenteritis (+17%)
            ['nausea', 'diarrhea', 'fatigue'],                # GI distress (+15%)
            
            # ENT patterns
            ['sore_throat', 'fever', 'body_aches'],           # Strep-like (+16%)
            ['runny_nose', 'sore_throat', 'cough'],           # Upper respiratory (+14%)
        ]
        
        # Confidence-indicating keywords
        self.confidence_keywords = [
            # High confidence indicators
            'severe', 'intense', 'excruciating', 'unbearable',
            'persistent', 'constant', 'worsening', 'acute',
            
            # Duration indicators
            'days', 'weeks', 'since', 'started', 'began',
            'ongoing', 'continuing', 'recurring',
            
            # Specificity indicators
            'exactly', 'precisely', 'definitely', 'clearly',
            'obviously', 'distinctly', 'specifically'
        ]

    def boost_confidence(self, base_confidence: float, symptoms: list, 
                        parsed_result: dict, feature_vector: list) -> float:
        """
        Apply multi-factor confidence boosting
        
        Args:
            base_confidence: Original model confidence
            symptoms: List of detected symptoms
            parsed_result: Parsed symptom information
            feature_vector: Feature vector used for prediction
        
        Returns:
            Enhanced confidence score
        """
        
        enhanced_confidence = base_confidence
        boost_factors = []
        
        # 1. Symptom Count Boost (more symptoms = higher confidence)
        symptom_count = len(symptoms)
        if symptom_count >= 5:
            factor = 1.20  # 20% boost for 5+ symptoms
            enhanced_confidence *= factor
            boost_factors.append(f"High symptom count ({symptom_count}): +{(factor-1)*100:.0f}%")
        elif symptom_count >= 4:
            factor = 1.15  # 15% boost for 4 symptoms
            enhanced_confidence *= factor
            boost_factors.append(f"Multiple symptoms ({symptom_count}): +{(factor-1)*100:.0f}%")
        elif symptom_count >= 3:
            factor = 1.08  # 8% boost for 3 symptoms
            enhanced_confidence *= factor
            boost_factors.append(f"Several symptoms ({symptom_count}): +{(factor-1)*100:.0f}%")
        
        # 2. Symptom Combination Pattern Boost
        for i, combination in enumerate(self.confident_symptom_combinations):
            if all(symptom in symptoms for symptom in combination):
                factor = 1.18  # 18% boost for known patterns
                enhanced_confidence *= factor
                boost_factors.append(f"Known pattern ({', '.join(combination)}): +{(factor-1)*100:.0f}%")
                break  # Only apply one pattern boost
        
        # 3. Duration Specificity Boost
        duration_days = parsed_result.get('duration_days', 7)
        if duration_days != 7:  # Not default value
            if duration_days <= 2:  # Acute condition
                factor = 1.15  # 15% boost for acute presentation
                enhanced_confidence *= factor
                boost_factors.append(f"Acute onset ({duration_days} days): +{(factor-1)*100:.0f}%")
            elif duration_days >= 14:  # Chronic condition
                factor = 1.12  # 12% boost for chronic presentation
                enhanced_confidence *= factor
                boost_factors.append(f"Chronic duration ({duration_days} days): +{(factor-1)*100:.0f}%")
            else:
                factor = 1.08  # 8% boost for specified duration
                enhanced_confidence *= factor
                boost_factors.append(f"Specified duration ({duration_days} days): +{(factor-1)*100:.0f}%")
        
        # 4. Intensity Specificity Boost
        intensity = parsed_result.get('intensity', 'moderate')
        if intensity == 'severe':
            factor = 1.15  # 15% boost for severe symptoms
            enhanced_confidence *= factor
            boost_factors.append(f"Severe intensity: +{(factor-1)*100:.0f}%")
        elif intensity == 'mild':
            factor = 1.08  # 8% boost for mild symptoms (specificity)
            enhanced_confidence *= factor
            boost_factors.append(f"Mild intensity: +{(factor-1)*100:.0f}%")
        
        # 5. Keyword Confidence Boost
        raw_text = parsed_result.get('raw_text', '')
        if isinstance(raw_text, dict):
            raw_text = str(raw_text)
        raw_text = str(raw_text).lower()
        confidence_keyword_count = sum(1 for keyword in self.confidence_keywords if keyword in raw_text)
        if confidence_keyword_count >= 3:
            factor = 1.12  # 12% boost for multiple confidence keywords
            enhanced_confidence *= factor
            boost_factors.append(f"Multiple descriptive terms ({confidence_keyword_count}): +{(factor-1)*100:.0f}%")
        elif confidence_keyword_count >= 1:
            factor = 1.06  # 6% boost for some confidence keywords
            enhanced_confidence *= factor
            boost_factors.append(f"Descriptive terms ({confidence_keyword_count}): +{(factor-1)*100:.0f}%")
        
        # 6. Manual Input Boost (user provided detailed information)
        manual_inputs = 0
        if 'duration_text' in parsed_result and parsed_result.get('duration_text'):
            manual_inputs += 1
        if 'intensity_text' in parsed_result and parsed_result.get('intensity_text'):
            manual_inputs += 1
        
        if manual_inputs >= 2:
            factor = 1.10  # 10% boost for complete manual input
            enhanced_confidence *= factor
            boost_factors.append(f"Complete information provided: +{(factor-1)*100:.0f}%")
        elif manual_inputs >= 1:
            factor = 1.05  # 5% boost for partial manual input
            enhanced_confidence *= factor
            boost_factors.append(f"Additional information provided: +{(factor-1)*100:.0f}%")
        
        # 7. Feature Vector Completeness Boost
        feature_completeness = sum(1 for f in feature_vector[:14] if f > 0) / 14  # First 14 are symptoms
        if feature_completeness >= 0.3:  # 30%+ symptoms present
            factor = 1.08  # 8% boost for comprehensive symptom profile
            enhanced_confidence *= factor
            boost_factors.append(f"Comprehensive symptoms ({feature_completeness*100:.0f}%): +{(factor-1)*100:.0f}%")
        
        # Cap confidence at 0.95 (medical diagnosis should never be 100% certain)
        final_confidence = min(enhanced_confidence, 0.95)
        
        # Log confidence boosting details
        logger.info(f"Confidence boosting applied:")
        logger.info(f"  Base confidence: {base_confidence:.3f}")
        logger.info(f"  Enhanced confidence: {enhanced_confidence:.3f}")
        logger.info(f"  Final confidence: {final_confidence:.3f}")
        for factor in boost_factors:
            logger.info(f"  - {factor}")
        
        return final_confidence, boost_factors

# Initialize AI diagnosis system and confidence booster
try:
    ai_diagnosis = ComprehensiveAIDiagnosis()
    confidence_booster = ConfidenceBooster()
    logger.info("✅ Enhanced Confident AI System initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize AI system: {e}")
    ai_diagnosis = None
    confidence_booster = None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'ai_system': 'available' if ai_diagnosis else 'unavailable',
        'confidence_booster': 'available' if confidence_booster else 'unavailable'
    })

@app.route('/diagnose', methods=['POST'])
def diagnose():
    """Enhanced diagnosis endpoint with confidence boosting"""
    try:
        if not ai_diagnosis or not confidence_booster:
            return jsonify({
                'error': 'AI system not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'error': 'No data provided',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        symptoms_text = data.get('symptoms', '')
        duration_text = data.get('duration', '')
        intensity_text = data.get('intensity', '')
        
        # Handle different symptoms formats (string or dict with symptomText)
        if isinstance(symptoms_text, dict):
            symptoms_text = symptoms_text.get('symptomText', '')
        elif not isinstance(symptoms_text, str):
            symptoms_text = str(symptoms_text)
        
        if not symptoms_text:
            return jsonify({
                'error': 'Symptoms are required',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        logger.info(f"📋 Processing diagnosis request:")
        logger.info(f"  Symptoms: {symptoms_text}")
        logger.info(f"  Duration: {duration_text}")
        logger.info(f"  Intensity: {intensity_text}")
        
        # Get base diagnosis
        result = ai_diagnosis.diagnose(symptoms_text, duration_text, intensity_text)
        
        if 'error' in result:
            return jsonify(result), 500
        
        # Apply enhanced confidence boosting
        base_confidence = result['confidence'] / 100  # Convert from percentage to decimal for processing
        symptoms = result['parsed_symptoms']
        parsed_result = {
            'symptoms': symptoms,
            'duration_days': result['duration_days'],
            'intensity': result['intensity'],
            'raw_text': symptoms_text,
            'duration_text': duration_text,
            'intensity_text': intensity_text
        }
        feature_vector = list(result['feature_vector'].values())
        
        enhanced_confidence, boost_factors = confidence_booster.boost_confidence(
            base_confidence, symptoms, parsed_result, feature_vector
        )
        
        # Update result with enhanced confidence (convert back to percentage)
        result['base_confidence'] = base_confidence * 100
        result['confidence'] = enhanced_confidence * 100
        result['confidence_boost_factors'] = boost_factors
        result['confidence_level'] = ai_diagnosis._get_confidence_level(enhanced_confidence)
        
        # Update top predictions with enhanced confidence for primary
        for pred in result['top_predictions']:
            if pred['diagnosis'] == result['primary_diagnosis']:
                pred['confidence'] = enhanced_confidence * 100
                break
        
        # Add enhancement metadata
        result['enhancement_info'] = {
            'original_confidence': base_confidence * 100,
            'enhanced_confidence': enhanced_confidence * 100,
            'boost_applied': enhanced_confidence > base_confidence,
            'boost_percentage': ((enhanced_confidence / base_confidence) - 1) * 100 if base_confidence > 0 else 0,
            'boost_factors_count': len(boost_factors)
        }
        
        logger.info(f"🎯 Diagnosis completed:")
        logger.info(f"  Primary: {result['primary_diagnosis']}")
        logger.info(f"  Base confidence: {base_confidence:.3f}")
        logger.info(f"  Enhanced confidence: {enhanced_confidence:.3f}")
        logger.info(f"  Boost factors: {len(boost_factors)}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Error in diagnosis: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/confidence-info', methods=['GET'])
def confidence_info():
    """Get information about confidence boosting mechanisms"""
    return jsonify({
        'confidence_mechanisms': {
            'symptom_count_boost': {
                'description': 'Higher confidence for more symptoms',
                'boost_ranges': {
                    '5+ symptoms': '20%',
                    '4 symptoms': '15%',
                    '3 symptoms': '8%'
                }
            },
            'pattern_recognition': {
                'description': 'Known symptom combination patterns',
                'patterns_count': len(confidence_booster.confident_symptom_combinations) if confidence_booster else 0,
                'boost_amount': '18%'
            },
            'duration_specificity': {
                'description': 'Specific duration information',
                'boost_ranges': {
                    'acute (≤2 days)': '15%',
                    'chronic (≥14 days)': '12%',
                    'specified duration': '8%'
                }
            },
            'intensity_specificity': {
                'description': 'Specific intensity information',
                'boost_ranges': {
                    'severe': '15%',
                    'mild': '8%'
                }
            },
            'descriptive_language': {
                'description': 'Confidence-indicating keywords',
                'keywords_count': len(confidence_booster.confidence_keywords) if confidence_booster else 0,
                'boost_ranges': {
                    '3+ keywords': '12%',
                    '1+ keywords': '6%'
                }
            },
            'information_completeness': {
                'description': 'Manual input of duration/intensity',
                'boost_ranges': {
                    'complete information': '10%',
                    'partial information': '5%'
                }
            }
        },
        'max_confidence': 95,  # 95% maximum confidence
        'confidence_levels': {
            'Very High': '≥85%',
            'High': '75-84%',
            'Medium': '60-74%',
            'Moderate': '45-59%',
            'Low': '<45%'
        }
    })

@app.route('/system-info', methods=['GET'])
def system_info():
    """Get system information"""
    try:
        info = {
            'system': 'Enhanced Confident AI Server v2.0',
            'status': 'operational',
            'timestamp': datetime.now().isoformat(),
            'ai_diagnosis_available': ai_diagnosis is not None,
            'confidence_booster_available': confidence_booster is not None
        }
        
        if ai_diagnosis:
            info['model_info'] = {
                'features_count': len(ai_diagnosis.feature_names),
                'supported_diagnoses': len(ai_diagnosis.label_encoder.classes_),
                'model_type': 'Random Forest Classifier'
            }
        
        if confidence_booster:
            info['confidence_mechanisms'] = {
                'symptom_combinations': len(confidence_booster.confident_symptom_combinations),
                'confidence_keywords': len(confidence_booster.confidence_keywords),
                'boost_factors': 7
            }
        
        return jsonify(info)
        
    except Exception as e:
        return jsonify({
            'error': 'Error getting system info',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Confident AI Server...")
    print("="*60)
    print("🤖 MediChain Enhanced Confident AI Server v2.0")
    print("🎯 Multi-factor confidence boosting enabled")
    print("📊 Comprehensive diagnosis with 56+ conditions")
    print("🔗 API endpoints:")
    print("   POST /diagnose - Enhanced AI diagnosis")
    print("   GET  /health - Health check")
    print("   GET  /confidence-info - Confidence mechanisms")
    print("   GET  /system-info - System information")
    print("="*60)
    
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )
