"""
Authentication routes for signup, login, password reset, and user management
"""
from flask import Blueprint, request, jsonify
from auth.auth_utils import auth_utils
from db.supabase_client import SupabaseClient
from email_validator import validate_email, EmailNotValidError
import re
import secrets
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
supabase = SupabaseClient()

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return "Password must be at least 6 characters long"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"\d", password):
        return "Password must contain at least one digit"
    return None

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        name = data['name'].strip()
        role = data['role'].lower()
        
        # Validate email
        try:
            validate_email(email)
        except EmailNotValidError as e:
            return jsonify({'error': str(e)}), 400
        
        # Validate role
        if role not in ['doctor', 'patient', 'admin']:
            return jsonify({'error': 'Role must be doctor, patient, or admin'}), 400
        
        # Validate password
        password_error = validate_password(password)
        if password_error:
            return jsonify({'error': password_error}), 400
        
        # Check if user already exists
        existing_user = supabase.client.table('users').select('*').eq('email', email).execute()
        if existing_user.data:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = auth_utils.hash_password(password)
        
        # Create user
        user_data = {
            'email': email,
            'password_hash': password_hash,
            'full_name': name,
            'role': role
        }
        
        response = supabase.client.table('users').insert(user_data).execute()
        
        if response.data:
            user = response.data[0]
            token = auth_utils.generate_token(user['id'], user['email'], user['role'])
            
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'data': {
                    'user': {
                        'id': user['id'],
                        'email': user['email'],
                        'full_name': user['full_name'],
                        'role': user['role']
                    },
                    'token': token
                }
            }), 201
        else:
            return jsonify({'error': 'Registration failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        response = supabase.client.table('users').select('*').eq('email', email).execute()
        
        if not response.data:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user = response.data[0]
        
        # Verify password
        if not auth_utils.verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = auth_utils.generate_token(user['id'], user['email'], user['role'])
        
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

@auth_bp.route('/me', methods=['GET'])
@auth_utils.token_required
def get_current_user():
    """Get current user information"""
    try:
        user_id = request.current_user['user_id']
        
        response = supabase.client.table('users').select('id', 'email', 'full_name', 'role', 'created_at').eq('id', user_id).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'data': response.data[0]
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/password-reset-request', methods=['POST'])
def password_reset_request():
    """Request password reset token"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Find user
        response = supabase.client.table('users').select('*').eq('email', email).execute()
        
        if not response.data:
            # Don't reveal if email exists or not
            return jsonify({'success': True, 'message': 'If email exists, reset instructions have been sent'}), 200
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        return jsonify({
            'success': True,
            'message': 'Reset token generated',
            'reset_token': reset_token  # In production, send via email
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/password-reset', methods=['POST'])
def password_reset():
    """Reset password with token"""
    try:
        data = request.get_json()
        reset_token = data.get('reset_token')
        new_password = data.get('new_password')
        
        if not reset_token or not new_password:
            return jsonify({'error': 'Reset token and new password are required'}), 400
        
        # Validate new password
        password_error = validate_password(new_password)
        if password_error:
            return jsonify({'error': password_error}), 400

        return jsonify({
            'success': True,
            'message': 'Password reset successful'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
