"""
Simple Flask backend for testing without Supabase
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
CORS(app)

# Simple in-memory user store for testing
users_db = {}

# JWT Secret
JWT_SECRET = 'test-secret-key'

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'medical-records-api'})

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Simple signup endpoint for testing"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', '')
        role = data.get('role', 'patient')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if email in users_db:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Store user
        user_id = len(users_db) + 1
        users_db[email] = {
            'id': user_id,
            'email': email,
            'password_hash': generate_password_hash(password),
            'full_name': full_name,
            'role': role
        }
        
        # Generate token
        token = jwt.encode({
            'user_id': user_id,
            'email': email,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'user': {
                    'id': user_id,
                    'email': email,
                    'full_name': full_name,
                    'role': role
                },
                'token': token
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Simple login endpoint for testing"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        user = users_db.get(email)
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = jwt.encode({
            'user_id': user['id'],
            'email': user['email'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'role': user['role']
                },
                'token': token
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    """Get current user information"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token is missing'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            email = payload['email']
            user = users_db.get(email)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            return jsonify({
                'success': True,
                'data': {
                    'user': {
                        'id': user['id'],
                        'email': user['email'],
                        'full_name': user['full_name'],
                        'role': user['role']
                    }
                }
            }), 200
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
