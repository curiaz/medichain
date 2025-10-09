"""
Authentication utilities for JWT tokens, password hashing, and user management
"""

from datetime import datetime, timedelta
from functools import wraps
import re

import bcrypt
import jwt
from flask import jsonify, request

from db.supabase_client import SupabaseClient


class AuthUtils:
    """Handles authentication utilities including JWT tokens and password hashing"""

    def __init__(self):
        # Use the provided JWT secret key
        self.secret_key = "isi4kI2GUSI1k841rTbeWHqVv00bN6KnBBkQJ/sfXRxdUckTXoCF1dlGmKgl1S9Qj/m4by03HN1h3x8x9woSnA=="
        
        # Initialize Supabase client with error handling
        try:
            self.supabase = SupabaseClient()
            print("✅ Supabase client initialized for auth utils")
        except Exception as e:
            print(f"⚠️  Warning: Supabase client initialization failed in auth utils: {e}")
            self.supabase = None

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def generate_token(self, user_id: str, email: str, role: str) -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user_id,
            "email": email,
            "role": role,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

    def decode_token(self, token: str):
        """Decode and verify JWT token"""
        try:
            return jwt.decode(token, self.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def token_required(self, f):
        """Decorator to require valid JWT token"""

        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            # Check for token in Authorization header
            if "Authorization" in request.headers:
                auth_header = request.headers["Authorization"]
                try:
                    token = auth_header.split(" ")[1]  # Bearer <token>
                except IndexError:
                    return jsonify({"error": "Invalid token format"}), 401

            if not token:
                return jsonify({"error": "Token is missing"}), 401

            payload = self.decode_token(token)
            if not payload:
                return jsonify({"error": "Token is invalid or expired"}), 401

            # Add user info to request context
            request.current_user = payload
            return f(*args, **kwargs)

        return decorated

    def role_required(self, allowed_roles):
        """Decorator to require specific role(s)"""

        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                if not hasattr(request, "current_user"):
                    return jsonify({"error": "Authentication required"}), 401

                user_role = request.current_user.get("role")
                if user_role not in allowed_roles:
                    return jsonify({"error": "Insufficient permissions"}), 403

                return f(*args, **kwargs)

            return decorated

        return decorator


def validate_password(password: str) -> bool:
    """
    Validate password strength
    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter  
    - Contains at least one digit
    - Contains at least one special character
    """
    if len(password) < 8:
        return False
    
    # Check for uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    
    # Check for lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    
    # Check for digit
    if not re.search(r'\d', password):
        return False
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True


auth_utils = AuthUtils()
