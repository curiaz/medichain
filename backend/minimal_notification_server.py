#!/usr/bin/env python3
"""
Minimal Notification Test Server
Simple Flask server to test notification functionality only
"""

from flask import Flask
from flask_cors import CORS
import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(__file__))

# Import notification routes
from notification_routes import notifications_bp, init_notifications_db

# Create Flask app
app = Flask(__name__)
CORS(app, origins=['http://localhost:3000', 'http://localhost:3001'])

# Initialize notification database
print("🔧 Initializing notification database...")
try:
    init_notifications_db()
    print("✅ Notification database initialized successfully")
except Exception as e:
    print(f"❌ Error initializing notification database: {e}")

# Register notification blueprint
app.register_blueprint(notifications_bp, url_prefix='/api')

# Simple health check
@app.route('/health', methods=['GET'])
def health_check():
    return {
        'status': 'healthy',
        'service': 'notification-test-server',
        'version': '1.0.0'
    }

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return {
        'message': 'MediChain Notification Test Server',
        'status': 'running',
        'endpoints': [
            '/health',
            '/api/notifications',
            '/api/notifications/stats',
            '/api/notifications/bulk'
        ]
    }

if __name__ == '__main__':
    print("🚀 Starting Notification Test Server...")
    print("📊 Available endpoints:")
    print("   GET  /health")
    print("   GET  /api/notifications")
    print("   POST /api/notifications")
    print("   PUT  /api/notifications/{id}")
    print("   DELETE /api/notifications/{id}")
    print("   GET  /api/notifications/stats")
    print("   POST /api/notifications/bulk")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )