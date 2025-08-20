"""
Authentication routes for signup, login, password reset, and user management
Updated to work with Supabase auth.users and profiles table schema
"""
from flask import Blueprint, request, jsonify
from auth.auth_utils import auth_utils
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
    """User registration endpoint using Supabase auth and profiles table"""
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
        
        # Step 1: Create user in Supabase Auth system
        try:
            print(f"Creating user with email: {email}")
            
            # Use Supabase Auth to create user
            auth_response = supabase.service_client.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,  # Auto-confirm for now
                "user_metadata": {
                    "full_name": full_name,
                    "role": role
                }
            })
            
            print(f"Auth response: {auth_response}")
            
            if not auth_response.user:
                print("No user returned from auth creation")
                return jsonify({'error': 'Failed to create user in auth system'}), 500
                
            user_id = auth_response.user.id
            print(f"Created user with ID: {user_id}")
            
        except Exception as auth_error:
            print(f"Auth creation error: {type(auth_error).__name__}: {auth_error}")
            if "already registered" in str(auth_error).lower() or "already exists" in str(auth_error).lower():
                return jsonify({'error': 'Email already registered'}), 409
            return jsonify({'error': f'Failed to create user account: {str(auth_error)}'}), 500
        
        # Step 2: Create profile record using the auth user's ID
        profile_data = {
            'id': user_id,  # Use the ID from auth.users
            'email': email,
            'full_name': full_name,
            'role': role
        }
        
        print(f"Creating profile with data: {profile_data}")
        
        # Use service role to insert profile (bypasses RLS)
        try:
            profile_response = supabase.service_client.table('profiles').insert(profile_data).execute()
            print(f"Profile response: {profile_response}")
            
            if profile_response.data:
                profile = profile_response.data[0]
                print(f"Created profile: {profile}")
                
                # Create role-specific record
                if role == 'patient':
                    patient_data = {
                        'user_id': user_id
                    }
                    print(f"Creating patient record: {patient_data}")
                    patient_response = supabase.service_client.table('patients').insert(patient_data).execute()
                    print(f"Patient response: {patient_response}")
                elif role == 'doctor':
                    doctor_data = {
                        'user_id': user_id
                    }
                    print(f"Creating doctor record: {doctor_data}")
                    doctor_response = supabase.service_client.table('doctors').insert(doctor_data).execute()
                    print(f"Doctor response: {doctor_response}")
                
                # Generate JWT token for immediate login
                token = auth_utils.generate_token(user_id, email, role)
                
                return jsonify({
                    'success': True,
                    'message': 'Account created successfully!',
                    'data': {
                        'user': {
                            'id': profile['id'],
                            'email': profile['email'],
                            'full_name': profile['full_name'],
                            'role': profile['role']
                        },
                        'token': token
                    }
                }), 201
            else:
                print("No profile data returned")
                return jsonify({'error': 'Failed to create profile'}), 500
        
        except Exception as profile_error:
            print(f"Profile creation error: {type(profile_error).__name__}: {profile_error}")
            # If profile creation fails, clean up the auth user
            try:
                print(f"Cleaning up auth user: {user_id}")
                supabase.service_client.auth.admin.delete_user(user_id)
            except Exception as cleanup_error:
                print(f"Cleanup error: {cleanup_error}")
            return jsonify({'error': f'Failed to create user profile: {str(profile_error)}'}), 500
            
    except Exception as e:
        print(f"Signup error: {str(e)}")  # Debug log
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint using Supabase auth"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Step 1: Authenticate with Supabase Auth
        try:
            auth_response = supabase.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if not auth_response.user:
                return jsonify({'error': 'Invalid email or password'}), 401
            
            user_id = auth_response.user.id
            
        except Exception as auth_error:
            print(f"Auth error: {auth_error}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Step 2: Get user profile
        profile_response = supabase.service_client.table('profiles').select('*').eq('id', user_id).execute()
        
        if not profile_response.data:
            return jsonify({'error': 'User profile not found'}), 404
        
        profile = profile_response.data[0]
        
        # Generate token
        token = auth_utils.generate_token(profile['id'], profile['email'], profile['role'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user': {
                    'id': profile['id'],
                    'email': profile['email'],
                    'full_name': profile['full_name'],
                    'role': profile['role']
                },
                'token': token
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug log
        return jsonify({'error': 'Invalid email or password'}), 401

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend email verification"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Resend verification email
        try:
            supabase.client.auth.resend({
                "type": "signup",
                "email": email
            })
            
            return jsonify({
                'success': True,
                'message': 'Verification email sent successfully'
            }), 200
            
        except Exception as resend_error:
            print(f"Resend verification error: {resend_error}")
            return jsonify({'error': 'Failed to send verification email'}), 500
            
    except Exception as e:
        print(f"Resend verification error: {str(e)}")
        return jsonify({'error': 'Failed to resend verification email'}), 500

@auth_bp.route('/verify-email', methods=['GET'])
def verify_email_status():
    """Check email verification status"""
    try:
        email = request.args.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Check profile verification status
        profile_response = supabase.service_client.table('profiles').select('email_verified').eq('email', email).execute()
        
        if not profile_response.data:
            return jsonify({'error': 'User not found'}), 404
        
        profile = profile_response.data[0]
        
        return jsonify({
            'success': True,
            'email_verified': profile.get('email_verified', False)
        }), 200
        
    except Exception as e:
        print(f"Verify email status error: {str(e)}")
        return jsonify({'error': 'Failed to check verification status'}), 500

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
