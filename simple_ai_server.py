#!/usr/bin/env python3
"""
Simple AI Test Server - Test AI functionality without Supabase dependencies
"""

import sys
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

app = Flask(__name__)
CORS(app)

# Test the AI Engine directly
def test_ai_engine():
    """Test AI engine functionality"""
    try:
        from app import EnhancedAIEngine
        ai_engine = EnhancedAIEngine()
        return ai_engine
    except Exception as e:
        print(f"❌ Error initializing AI engine: {e}")
        return None

@app.route('/')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'message': 'Simple AI Test Server is running',
        'endpoints': [
            '/api/test-ai',
            '/api/diagnose'
        ]
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check for frontend"""
    return jsonify({
        'status': 'ok',
        'message': 'AI service is running'
    })

@app.route('/api/test-ai', methods=['GET'])
def test_ai():
    """Test AI engine endpoint"""
    ai_engine = test_ai_engine()
    if ai_engine:
        try:
            # Test with sample symptoms
            result = ai_engine.diagnose('fever, cough, fatigue', age='Adult (20 - 59 years)', gender='Male')
            return jsonify({
                'success': True,
                'message': 'AI engine is working',
                'sample_diagnosis': result.get('diagnosis', 'Unknown'),
                'method': result.get('method', 'Unknown')
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'AI engine test failed: {str(e)}'
            })
    else:
        return jsonify({
            'success': False,
            'error': 'Could not initialize AI engine'
        })

@app.route('/api/ai/diagnose', methods=['POST'])
def diagnose():
    """AI diagnosis endpoint"""
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', '')
        age = data.get('patientAge') or data.get('age', 'Adult (20 - 59 years)')
        gender = data.get('patientGender') or data.get('gender', 'Male')
        
        ai_engine = test_ai_engine()
        if not ai_engine:
            return jsonify({
                'success': False,
                'error': 'AI engine not available'
            }), 500
        
        result = ai_engine.diagnose(symptoms, age=age, gender=gender)
        
        # Match the expected response structure
        return jsonify({
            'diagnosis': result.get('diagnosis', 'General Assessment'),
            'formatted_response': result.get('formatted_response', ''),
            'method': result.get('method', 'ai_model'),
            'confidence': result.get('confidence', 75),
            'severity': result.get('severity', 'moderate')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🔧 Starting Simple AI Test Server...")
    print("🌐 Frontend: http://localhost:3000")
    print("🔥 Backend: http://localhost:5000")
    print("📋 Test AI: http://localhost:5000/api/test-ai")
    print("-" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)