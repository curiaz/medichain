"""
Simple Backend Health Check - Start Backend Without AI Model
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Backend is running",
        "python_version": "3.13.2"
    }), 200

@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({"message": "Backend test successful"}), 200

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    print(f"\n✅ Simple Backend Server starting on port {port}")
    print(f"✅ Health check: http://localhost:{port}/api/health\n")
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
