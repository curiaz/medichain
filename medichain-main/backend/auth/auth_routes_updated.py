"""
Authentication routes for signup, login, password reset, and user management
Updated to work with the new database schema
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
        required_fields = ['email', 'password', 'full_name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        full_name = data['full_name'].strip()
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
        existing_user = supabase.client.table('profiles').select('*').eq('email', email).execute()
        if existing_user.data:
            return jsonify({'error': 'Email already registered'}), 409
        
        # Hash password
        password_hash = auth_utils.hash_password(password)
        
        # Create user in profiles table
        user_data = {
            'email': email,
            'full_name': full_name,
            'role': role
        }
        
        response = supabase.client.table('profiles').insert(user_data).execute()
        
        if response.data:
            user = response.data[0]
            token = auth_utils.generate_token(user['id'], user['email'], user['role'])
            
            # Create role-specific record
            if role == 'doctor':
                doctor_data = {
                    'user_id': user['id'],
                    'license_number': data.get('license_number', ''),
                    'specialization': data.get('specialization', []),
                    'hospital_affiliation': data.get('hospital_affiliation', ''),
                    'years_experience': data.get('years_experience', 0)
                }
                supabase.client.table('doctors').insert(doctor_data).execute()
            elif role == 'patient':
                patient_data = {
                    'user_id': user['id'],
                    'date_of_birth': data.get('date_of_birth'),
                    'gender': data.get('gender'),
                    'phone': data.get('phone'),
                    'address': data.get('address', {}),
                    'emergency_contact': data.get('emergency_contact', {})
                }
                supabase.client.table('patients').insert(patient_data).execute()
            
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
        
        # Find user in profiles table
        response = supabase.client.table('profiles').select('*').eq('email', email).execute()
        
        if not response.data:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user = response.data[0]
        
        # Verify password
        if not auth_utils.verify_password(password, user.get('password_hash', '')):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = auth_utils.generate_token(user['id'], user['email'], user['role'])
        
        # Get role-specific data
        role_data = None
        if user['role'] == 'doctor':
            doctor_response = supabase.client.table('doctors').select('*').eq('user_id', user['id']).execute()
            role_data = doctor_response.data[0] if doctor_response.data else None
        elif user['role'] == 'patient':
            patient_response = supabase.client.table('patients').select('*').eq('user_id', user['id']).execute()
            role_data = patient_response.data[0] if patient_response.data else None
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'role': user['role'],
                    'role_data': role_data
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
        
        # Get user from profiles table
        user_response = supabase.client.table('profiles').select('*').eq('id', user_id).execute()
        
        if not user_response.data:
            return jsonify({'error': 'User not found'}), 404
            
        user = user_response.data[0]
        
        # Get role-specific data
        role_data = None
        if user['role'] == 'doctor':
            doctor_response = supabase.client.table('doctors').select('*').eq('user_id', user['id']).execute()
            role_data = doctor_response.data[0] if doctor_response.data else None
        elif user['role'] == 'patient':
            patient_response = supabase.client.table('patients').select('*').eq('user_id', user['id']).execute()
            role_data = patient_response.data[0] if patient_response.data else None
        
        return jsonify({
            'success': True,
            'data': {
                'user': user,
                'role_data': role_data
            }
        }), 200
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
