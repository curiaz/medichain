"""
Authentication routes for signup, login, password reset, and user management
Simple version without email verification - for stable functionality
"""
print("DEBUG: auth_routes_simple.py is being loaded!")
from flask import Blueprint, request, jsonify
from auth.auth_utils import auth_utils
from auth.hybrid_auth import create_user_hybrid, authenticate_user_hybrid
from db.supabase_client import SupabaseClient
from email_validator import validate_email, EmailNotValidError
import re

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
    """User registration endpoint using database-only authentication"""
    try:
        data = request.get_json()
        
        # DEBUG: Print received data
        print("DEBUG: Received signup data:", data)
        print("DEBUG: Data keys:", list(data.keys()) if data else "No data")
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        missing_fields = []
        for field in required_fields:
            if not data.get(field):
                missing_fields.append(field)
                print(f"DEBUG: Missing field '{field}', value: {data.get(field)}")
        
        if missing_fields:
            error_msg = f"Missing required fields: {', '.join(missing_fields)}"
            print(f"DEBUG: Returning error: {error_msg}")
            return jsonify({'error': error_msg}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
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
        
        # Create user using hybrid authentication approach
        user_result = create_user_hybrid(email, password, first_name, last_name, role)
        
        if not user_result['success']:
            return jsonify({'error': user_result['error']}), 400
        
        user = user_result['user']
        
        # Generate JWT token for immediate login
        token = auth_utils.generate_token(user['id'], user['email'], user['role'])
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully!',
            'data': {
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'role': user['role']
                },
                'token': token
            }
        }), 201
            
    except Exception as e:
        print(f"Signup error: {str(e)}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint using database-only authentication"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        print(f"DEBUG: Login attempt for email: {email}")
        print(f"DEBUG: Password length: {len(password)}")
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Authenticate using hybrid approach (database password first, then Supabase Auth fallback)
        auth_result = authenticate_user_hybrid(email, password)
        
        if not auth_result['success']:
            print(f"DEBUG: Authentication failed: {auth_result['error']}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user = auth_result['user']
        print(f"DEBUG: Authenticated user: {user}")
        
        # Generate token
        token = auth_utils.generate_token(user['id'], user['email'], user['role'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'full_name': user.get('full_name', f"{user.get('first_name', '')} {user.get('last_name', '')}").strip(),
                    'role': user['role']
                },
                'token': token
            }
        }), 200
        
    except Exception as e:
        print(f"DEBUG: Unexpected login error: {str(e)}")
        print(f"DEBUG: Error type: {type(e)}")
        return jsonify({'error': 'Invalid email or password'}), 401

@auth_bp.route('/me', methods=['GET'])
@auth_utils.token_required
def get_current_user():
    """Get current user information from profiles table"""
    try:
        user_id = request.current_user['user_id']
        
        # Get user profile using service client
        profile_response = supabase.service_client.table('profiles').select('*').eq('id', user_id).execute()
        
        if not profile_response.data:
            return jsonify({'error': 'User not found'}), 404
            
        profile = profile_response.data[0]
        
        return jsonify({
            'success': True,
            'data': {
                'user': profile
            }
        }), 200
            
    except Exception as e:
        print(f"Get current user error: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500
