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
        existing_user = supabase.client.table("user_profiles").select("*").eq("email", email).execute()
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

        response = supabase.client.table("user_profiles").insert(user_data).execute()
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
        print("[DEBUG] Login request data:", data)

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        print(f"[DEBUG] Email: {email}, Password: {'*' * len(password)}")

        if not email or not password:
            print("[DEBUG] Missing email or password")
            return jsonify({"error": "Email and password are required"}), 400

        # Find user
        response = supabase.client.table("user_profiles").select("*").eq("email", email).execute()
        print("[DEBUG] Supabase user query result:", response.data)

        if not response.data:
            print("[DEBUG] No user found for email")
            return jsonify({"error": "Invalid email or password"}), 401

        user = response.data[0]
        print(f"[DEBUG] User found: {user}")
        print(f"[DEBUG] Password hash in DB: {user.get('password_hash')}")

        # Verify password
        password_check = auth_utils.verify_password(password, user["password_hash"])
        print(f"[DEBUG] Password check result: {password_check}")
        if not password_check:
            print("[DEBUG] Password mismatch for user")
            return jsonify({"error": "Invalid email or password"}), 401

        # Generate token
        token = auth_utils.generate_token(user["id"], user["email"], user["role"])

        print("[DEBUG] Login successful for user", user["email"])
        return (
            jsonify(
                {
                    "success": True,
                    "message": "Login successful",
                    "data": {
                        "user": {
                            "id": user["id"],
                            "email": user["email"],
                            "full_name": user["full_name"],
                            "role": user["role"],
                        },
                        "token": token,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        print(f"[DEBUG] Exception in login: {e}")
        return jsonify({"error": str(e)}), 500
