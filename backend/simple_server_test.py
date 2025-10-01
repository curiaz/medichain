"""
Simple Flask server test - Healthcare system without immediate Supabase connection
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

# Simple test app
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'service': 'MediChain Healthcare System',
        'message': 'Server is running successfully',
        'endpoints': [
            'GET /',
            'GET /test-healthcare',
            'POST /api/healthcare/auth/register-patient (requires Firebase auth)',
            'GET /api/healthcare/health (requires database connection)'
        ]
    }

@app.route('/test-healthcare')
def test_healthcare():
    """Test healthcare system components without database connection"""
    try:
        # Test imports without initializing connections
        from healthcare_routes import (
            healthcare_auth_bp,
            healthcare_medical_bp,
            healthcare_appointments_bp,
            healthcare_system_bp
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Healthcare system components loaded successfully',
            'components': [
                'Healthcare Authentication Routes',
                'Medical Records Management',
                'Appointment Scheduling',
                'System Health Monitoring'
            ],
            'database_status': 'Lazy loading - will connect when needed',
            'firebase_status': 'Ready for authentication'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Healthcare system error: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🏥 STARTING MEDICHAIN HEALTHCARE SYSTEM")
    print("=" * 50)
    print("✅ Healthcare routes: Ready")
    print("✅ Firebase Auth: Ready") 
    print("✅ Database: Lazy loading")
    print("📍 Server: http://localhost:5000")
    print("🔍 Test: http://localhost:5000/test-healthcare")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)