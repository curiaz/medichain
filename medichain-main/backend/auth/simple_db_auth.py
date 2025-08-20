"""
Simple database-only authentication (bypass Supabase Auth)
"""
from flask import Blueprint, request, jsonify
from auth.auth_utils import auth_utils
from db.supabase_client import SupabaseClient
from email_validator import validate_email, EmailNotValidError
import re
import bcrypt
import uuid

simple_auth_bp = Blueprint('simple_auth', __name__, url_prefix='/api/auth')
supabase = SupabaseClient()

def hash_password(password):
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

@simple_auth_bp.route('/signup', methods=['POST'])
def simple_signup():
    """Simple signup using only database (no Supabase Auth)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        role = data['role']
        
        # Validate email
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({'error': 'Invalid email address'}), 400
        
        # Check if user already exists
        existing_user = supabase.service_client.table('profiles').select('*').eq('email', email).execute()
        if existing_user.data:
            return jsonify({'error': 'An account with this email already exists'}), 409
        
        # Create user profile directly in database
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(password)
        
        profile_data = {
            'id': user_id,
            'email': email,
            'password_hash': hashed_password,  # Store hashed password
            'first_name': first_name,
            'last_name': last_name,
            'full_name': f"{first_name} {last_name}",
            'role': role,
            'created_at': 'now()',
            'updated_at': 'now()'
        }
        
        # Insert into profiles table
        result = supabase.service_client.table('profiles').insert(profile_data).execute()
        
        if not result.data:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Generate token
        token = auth_utils.generate_token(user_id, email, role)
        
        # Return user data (without password hash)
        user_data = {
            'id': user_id,
            'email': email,
            'full_name': f"{first_name} {last_name}",
            'role': role
        }
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'data': {
                'user': user_data,
                'token': token
            }
        }), 201
        
    except Exception as e:
        print(f"Simple signup error: {str(e)}")
        return jsonify({'error': 'Failed to create account'}), 500

@simple_auth_bp.route('/login', methods=['POST'])
def simple_login():
    """Simple login using only database (no Supabase Auth)"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Get user from database
        user_result = supabase.service_client.table('profiles').select('*').eq('email', email).execute()
        
        if not user_result.data:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user = user_result.data[0]
        
        # Verify password
        if not user.get('password_hash') or not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = auth_utils.generate_token(user['id'], user['email'], user['role'])
        
        # Return user data (without password hash)
        user_data = {
            'id': user['id'],
            'email': user['email'],
            'full_name': user['full_name'],
            'role': user['role']
        }
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': user_data,
                'token': token
            }
        }), 200
        
    except Exception as e:
        print(f"Simple login error: {str(e)}")
        return jsonify({'error': 'Invalid email or password'}), 401

@simple_auth_bp.route('/me', methods=['GET'])
@auth_utils.token_required
def simple_get_current_user():
    """Get current user information from profiles table"""
    try:
        user_id = request.current_user['user_id']
        
        # Get user profile using service client
        profile_response = supabase.service_client.table('profiles').select('id,email,full_name,first_name,last_name,role,created_at,updated_at').eq('id', user_id).execute()
        
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
        print(f"Get current user error: {str(e)}")
        return jsonify({'error': str(e)}), 500
