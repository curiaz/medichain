"""
Authentication routes for signup, login, password reset, and user management
"""

import re
import secrets
import os
import smtplib
import random
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from email_validator import EmailNotValidError, validate_email
from flask import Blueprint, jsonify, request
from firebase_admin import auth

from auth.auth_utils import auth_utils
from db.supabase_client import SupabaseClient

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
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


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """User registration endpoint"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["email", "password", "name", "role"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"{field} is required"}), 400

        email = data["email"].strip().lower()
        password = data["password"]
        name = data["name"].strip()
        role = data["role"].lower()

        # Validate email
        try:
            validate_email(email)
        except EmailNotValidError as e:
            return jsonify({"error": str(e)}), 400

        # Validate role
        if role not in ["doctor", "patient", "admin"]:
            return jsonify({"error": "Role must be doctor, patient, or admin"}), 400

        # Validate password
        password_error = validate_password(password)
        if password_error:
            return jsonify({"error": password_error}), 400

        # Check if user already exists
        existing_user = supabase.client.table("users").select("*").eq("email", email).execute()
        if existing_user.data:
            return jsonify({"error": "Email already registered"}), 409

        # Hash password
        password_hash = auth_utils.hash_password(password)

        # Create user
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "full_name": name,
            "role": role,
        }

        response = supabase.client.table("users").insert(user_data).execute()

        if response.data:
            user = response.data[0]
            token = auth_utils.generate_token(user["id"], user["email"], user["role"])

            return (
                jsonify(
                    {
                        "success": True,
                        "message": "User registered successfully",
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
                201,
            )
        else:
            return jsonify({"error": "Registration failed"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Find user
        response = supabase.client.table("users").select("*").eq("email", email).execute()

        if not response.data:
            return jsonify({"error": "Invalid email or password"}), 401

        user = response.data[0]

        # Verify password
        if not auth_utils.verify_password(password, user["password_hash"]):
            return jsonify({"error": "Invalid email or password"}), 401

        # Generate token
        token = auth_utils.generate_token(user["id"], user["email"], user["role"])

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
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/me", methods=["GET"])
@auth_utils.token_required
def get_current_user():
    """Get current user information"""
    try:
        user_id = request.current_user["user_id"]

        response = (
            supabase.client.table("users").select("id", "email", "full_name", "role", "created_at").eq("id", user_id).execute()
        )

        if response.data:
            return jsonify({"success": True, "data": response.data[0]}), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/password-reset-request", methods=["POST"])
def password_reset_request():
    """Request password reset using Firebase Auth"""
    try:
        from auth.firebase_auth import firebase_auth_service
        
        data = request.get_json()
        email = data.get("email", "").strip().lower()

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({"error": "Invalid email format"}), 400

        # Check if user exists in Supabase (user profiles)
        try:
            response = supabase.client.table("user_profiles").select("*").eq("email", email).execute()
            
            if not response.data:
                # Don't reveal if email exists or not for security
                return jsonify({
                    "success": True,
                    "message": "If this email is registered, you will receive a password reset link"
                }), 200
        except Exception as db_error:
            print(f"Database check error: {db_error}")
            # Continue with Firebase reset even if DB check fails

        # Use Firebase Auth to send password reset email
        try:
            # Firebase Auth handles the email sending automatically
            auth.generate_password_reset_link(email)
            
            return jsonify({
                "success": True,
                "message": "Password reset link has been sent to your email"
            }), 200
            
        except auth.UserNotFoundError:
            # User doesn't exist in Firebase, but don't reveal this for security
            return jsonify({
                "success": True,
                "message": "If this email is registered, you will receive a password reset link"
            }), 200
            
        except Exception as firebase_error:
            print(f"Firebase password reset error: {firebase_error}")
            return jsonify({"error": "Failed to send password reset email"}), 500

    except Exception as e:
        print(f"Password reset request error: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500


def send_otp_email(email, name, otp):
    """Send OTP email to user"""
    try:
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("GMAIL_USER")
        sender_password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not sender_email or not sender_password:
            print("Email credentials not configured")
            return False
        
        # Create email message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = "🔐 MediChain Password Reset - Verification Code"
        
        # Email body
        email_body = f"""
🏥 MEDICHAIN PASSWORD RESET

Hello {name},

We received a request to reset your MediChain account password.

🔑 Your verification code is: {otp}

⏰ This code will expire in 10 minutes.

If you didn't request this password reset, please ignore this email or contact our support team.

For your security:
• Never share this code with anyone
• Only enter this code on the official MediChain website
• Make sure you're on the correct website before entering the code

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 Visit: localhost:3001
📧 Support: medichain173@gmail.com

Best regards,
The MediChain Security Team

© 2025 MediChain - AI-Driven Diagnosis & Blockchain Health Records System
        """
        
        msg.attach(MIMEText(email_body, "plain"))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Failed to send OTP email: {str(e)}")
        return False


@auth_bp.route("/verify-password-reset", methods=["POST"])
def verify_password_reset():
    """Verify Firebase password reset and update user profile if needed"""
    try:
        from auth.firebase_auth import firebase_auth_service
        
        data = request.get_json()
        firebase_token = data.get("firebase_token")
        
        if not firebase_token:
            return jsonify({"error": "Firebase token is required"}), 400
        
        # Verify the Firebase token
        verification_result = firebase_auth_service.verify_token(firebase_token)
        
        if not verification_result["success"]:
            return jsonify({"error": "Invalid Firebase token"}), 401
            
        user_info = verification_result["user"]
        email = user_info.get("email")
        firebase_uid = user_info.get("uid")
        
        # Update user profile in Supabase if needed
        try:
            # Check if user profile exists
            profile_response = supabase.client.table("user_profiles").select("*").eq("email", email).execute()
            
            if profile_response.data:
                # Update existing profile with Firebase UID if missing
                profile = profile_response.data[0]
                if not profile.get("firebase_uid"):
                    supabase.client.table("user_profiles").update({
                        "firebase_uid": firebase_uid,
                        "updated_at": datetime.utcnow().isoformat()
                    }).eq("email", email).execute()
                    
        except Exception as profile_error:
            print(f"Profile update error: {profile_error}")
            # Continue even if profile update fails
            
        return jsonify({
            "success": True,
            "message": "Password reset completed successfully",
            "user": {
                "email": email,
                "firebase_uid": firebase_uid
            }
        }), 200
        
    except Exception as e:
        print(f"Password reset verification error: {str(e)}")
        return jsonify({"error": "An error occurred during verification"}), 500


@auth_bp.route("/sync-firebase-user", methods=["POST"])
def sync_firebase_user():
    """Sync Firebase user with Supabase user profile after password reset or login"""
    try:
        from auth.firebase_auth import firebase_auth_service
        
        # Get Firebase token from request
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"error": "Authorization header required"}), 401
            
        try:
            firebase_token = auth_header.split(" ")[1]  # Remove 'Bearer ' prefix
        except IndexError:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Verify Firebase token
        verification_result = firebase_auth_service.verify_token(firebase_token)
        
        if not verification_result["success"]:
            return jsonify({"error": "Invalid Firebase token"}), 401
            
        user_info = verification_result["user"]
        email = user_info.get("email")
        firebase_uid = user_info.get("uid")
        name = user_info.get("name", "")
        
        if not email or not firebase_uid:
            return jsonify({"error": "Invalid user information"}), 400
        
        # Check if user profile exists in Supabase
        try:
            profile_response = supabase.client.table("user_profiles").select("*").eq("firebase_uid", firebase_uid).execute()
            
            if profile_response.data:
                # User exists, update profile
                profile = profile_response.data[0]
                
                # Update with latest information
                update_data = {
                    "email": email,
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                if name and not profile.get("full_name"):
                    update_data["full_name"] = name
                    
                supabase.client.table("user_profiles").update(update_data).eq("firebase_uid", firebase_uid).execute()
                
                return jsonify({
                    "success": True,
                    "message": "User profile synchronized",
                    "user": profile
                }), 200
                
            else:
                # User doesn't exist, create new profile
                new_profile = {
                    "firebase_uid": firebase_uid,
                    "email": email,
                    "full_name": name or email.split("@")[0],
                    "role": "patient",  # Default role
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                
                insert_response = supabase.client.table("user_profiles").insert(new_profile).execute()
                
                return jsonify({
                    "success": True,
                    "message": "User profile created",
                    "user": insert_response.data[0] if insert_response.data else new_profile
                }), 201
                
        except Exception as db_error:
            print(f"Database sync error: {db_error}")
            return jsonify({"error": "Failed to sync user profile"}), 500
        
    except Exception as e:
        print(f"User sync error: {str(e)}")
        return jsonify({"error": "An error occurred during user synchronization"}), 500
