#!/usr/bin/env python3
"""
Simplified Flask Test Server
Tests if basic Flask functionality works
"""
from flask import Flask, jsonify
from flask_cors import CORS
import os

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

@app.route('/')
def health():
    return jsonify({
        'status': 'Test server is running!',
        'message': 'Basic Flask functionality works'
    })

@app.route('/api/test')
def test_api():
    return jsonify({
        'status': 'success',
        'message': 'API endpoint working'
    })

@app.route('/api/auth/test')
def test_auth():
    return jsonify({
        'status': 'success',
        'message': 'Auth endpoint accessible'
    })

if __name__ == '__main__':
    print("🚀 Starting test Flask server...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔗 Test endpoints:")
    print("   - http://localhost:5000/")
    print("   - http://localhost:5000/api/test")
    print("   - http://localhost:5000/api/auth/test")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()