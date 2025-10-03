#!/usr/bin/env python3
"""
Simple test server for AI diagnosis
"""
import sys
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

app = Flask(__name__)
CORS(app)

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'message': 'AI service is running'})

@app.route('/api/ai/diagnose', methods=['POST'])
def diagnose():
    try:
        from app import EnhancedAIEngine
        data = request.get_json()
        symptoms = data.get('symptoms', '')
        age = data.get('patientAge', 'Adult')
        gender = data.get('patientGender', 'Male')
        
        print(f"Received diagnosis request: {symptoms[:50]}...")
        
        ai_engine = EnhancedAIEngine()
        result = ai_engine.diagnose(symptoms, age=age, gender=gender)
        
        print(f"Diagnosis result: {result.get('diagnosis', 'Unknown')}")
        
        return jsonify({
            'diagnosis': result.get('diagnosis', 'General Assessment'),
            'formatted_response': result.get('formatted_response', ''),
            'method': result.get('method', 'ai_model'),
            'confidence': result.get('confidence', 75),
            'severity': result.get('severity', 'moderate')
        })
    except Exception as e:
        print(f"Error in diagnosis: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("🔧 Starting AI Test Server...")
    print("🌐 Frontend: http://localhost:3000")  
    print("🔥 Backend: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)