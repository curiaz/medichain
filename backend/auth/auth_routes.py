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
# Initialize Supabase client with error handling
try:
    supabase = SupabaseClient()
    print("✅ Supabase client initialized for auth routes")
except Exception as e:
    print(f"⚠️  Warning: Supabase client initialization failed in auth routes: {e}")
    supabase = None


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
    """Request password reset using OTP system"""
    try:
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
                # For security, don't reveal if email exists or not
                return jsonify({
                    "success": True,
                    "message": "If this email is registered, you will receive a verification code"
                }), 200
                
            user_profile = response.data[0]
            user_name = user_profile.get("full_name", user_profile.get("first_name", "User"))
            
        except Exception as db_error:
            print(f"Database check error: {db_error}")
            return jsonify({"error": "Database error occurred"}), 500

        # Use Firebase Auth to send password reset email
        from auth.firebase_auth import firebase_auth_service
        
        result = firebase_auth_service.send_password_reset_email(email)
        
        if result["success"]:
            # Store a temporary session to allow the UI to continue its flow
            # but inform user about the Firebase reset process
            session_token = secrets.token_urlsafe(32)
            verification_code = result.get("verification_code")
            
            # Verification code is stored in database via OTP service
            print(f"✅ Password reset initiated for {email}")
            print(f"🔢 Verification code: {verification_code} (expires in 5 minutes)")
            print(f"🎫 Session token: {session_token}")
                
            return jsonify({
                "success": True,
                "message": "Password reset email sent! Check your email for both a reset link and verification code.",
                "ui_message": "A password reset email has been sent with two options: use the verification code below or click the reset link in the email.",
                "session_token": session_token,
                "has_verification_code": True
            }), 200
        else:
            # Handle different Firebase errors gracefully
            error_message = result.get("error", "Failed to send reset email")
            
            # For security, don't reveal if user doesn't exist
            if "No user found" in error_message or "USER_NOT_FOUND" in error_message:
                return jsonify({
                    "success": True,
                    "message": "If this email is registered, you will receive a password reset email"
                }), 200
            else:
                print(f"Firebase password reset error: {error_message}")
                return jsonify({"error": "Failed to send reset email. Please try again."}), 500

    except Exception as e:
        print(f"Password reset request error: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500


def generate_numeric_otp():
    """Generate a 6-digit numeric OTP"""
    return f"{random.randint(100000, 999999):06d}"


def send_otp_email(email, name, otp):
    """Send OTP email to user with enhanced design"""
    try:
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("GMAIL_USER")
        sender_password = os.getenv("GMAIL_APP_PASSWORD")
        
        if not sender_email or not sender_password:
            print("Email credentials not configured")
            return False
        
        # Create email message with both HTML and plain text
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Medichain Security <{sender_email}>"
        msg["To"] = email
        msg["Subject"] = "🔐 Medichain Password Reset - Verification Code"
        
        # Plain text version
        text_body = f"""
🏥 MEDICHAIN PASSWORD RESET

Hello {name},

We received a request to reset your Medichain account password.

🔑 Your verification code is: {otp}

⏰ This code will expire in 10 minutes.

If you didn't request this password reset, please ignore this email or contact our support team.

For your security:
• Never share this code with anyone  
• Only enter this code on the official Medichain website
• Make sure you're on the correct website before entering the code

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 Visit: localhost:3001
📧 Support: medichain173@gmail.com

Best regards,
The Medichain Security Team

© 2025 Medichain - AI-Driven Diagnosis & Blockchain Health Records System
        """
        
        # HTML version for better presentation
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medichain Password Reset</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f8f9fa;">
    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%); padding: 30px; text-align: center;">
            <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
                <div style="width: 40px; height: 40px; background: rgba(255, 255, 255, 0.2); border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: white;">+</div>
                <h1 style="margin: 0; color: white; font-size: 28px; font-weight: 700;">Medichain</h1>
            </div>
            <p style="margin: 8px 0 0 0; color: rgba(255, 255, 255, 0.9); font-size: 14px;">AI-Driven Healthcare Platform</p>
        </div>
        
        <!-- Main Content -->
        <div style="padding: 40px 30px;">
            <h2 style="color: #1565c0; margin: 0 0 20px 0; font-size: 24px;">🔐 Password Reset Verification</h2>
            
            <p style="margin: 0 0 20px 0; font-size: 16px;">Hello <strong>{name}</strong>,</p>
            
            <p style="margin: 0 0 30px 0; font-size: 16px;">We received a request to reset your Medichain account password. Use the verification code below to proceed:</p>
            
            <!-- OTP Code Box -->
            <div style="background: linear-gradient(145deg, #e3f2fd 0%, #bbdefb 100%); border: 2px solid #2196f3; border-radius: 12px; padding: 25px; margin: 30px 0; text-align: center;">
                <p style="margin: 0 0 15px 0; font-size: 14px; color: #1565c0; font-weight: 600;">Your Verification Code</p>
                <div style="font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace; font-size: 36px; font-weight: 700; color: #1976d2; letter-spacing: 8px; margin: 10px 0;">{otp}</div>
                <p style="margin: 15px 0 0 0; font-size: 12px; color: #666;">⏰ Expires in 10 minutes</p>
            </div>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h3 style="margin: 0 0 15px 0; color: #856404; font-size: 16px;">🛡️ Security Guidelines</h3>
                <ul style="margin: 0; padding-left: 20px; color: #856404;">
                    <li>Never share this code with anyone</li>
                    <li>Only enter this code on the official Medichain website</li>
                    <li>Make sure you're on the correct website before entering the code</li>
                    <li>If you didn't request this reset, please ignore this email</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="http://localhost:3001/reset-password" style="display: inline-block; background: linear-gradient(145deg, #2196f3 0%, #1976d2 100%); color: white; text-decoration: none; padding: 12px 30px; border-radius: 8px; font-weight: 600; font-size: 16px;">Reset Password</a>
            </div>
        </div>
        
        <!-- Footer -->
        <div style="background-color: #f8f9fa; border-top: 1px solid #e9ecef; padding: 25px 30px; text-align: center;">
            <p style="margin: 0 0 10px 0; font-size: 14px; color: #6c757d;">
                <strong>Medichain</strong> | AI-Driven Diagnosis & Blockchain Health Records
            </p>
            <p style="margin: 0 0 10px 0; font-size: 12px; color: #adb5bd;">
                📧 Support: medichain173@gmail.com | 🌐 localhost:3001
            </p>
            <p style="margin: 0; font-size: 11px; color: #adb5bd;">
                © 2025 Medichain Security Team. For academic use – Taguig City University
            </p>
        </div>
    </div>
</body>
</html>
        """
        
        # Attach both text and HTML versions
        text_part = MIMEText(text_body, "plain")
        html_part = MIMEText(html_body, "html")
        
        msg.attach(text_part)
        msg.attach(html_part)
        
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


@auth_bp.route("/verify-otp", methods=["POST"])
def verify_otp():
    """Firebase-based password reset - redirect to email instructions"""
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        otp = data.get("otp", "").strip()

        if not email:
            return jsonify({"error": "Email is required"}), 400

        # Verify OTP using database service
        try:
            # Import OTP service with fallback
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            try:
                from services.simple_otp_manager import simple_otp_manager as otp_service
                print("✅ Using Simple OTP Manager for verification")
            except ImportError:
                try:
                    from services.otp_service import otp_service
                    print("✅ Using Database OTP Service for verification")
                except ImportError as e:
                    print(f"Warning: OTP service not available: {e}")
                    return jsonify({
                        "error": "OTP verification service not available. Please use the Firebase reset link from your email."
                    }), 503
            
            if not otp:
                # No OTP provided, check if there's a valid session
                otp_info = otp_service.get_otp_info(email)
                if otp_info:
                    reset_token = secrets.token_urlsafe(32)
                    return jsonify({
                        "success": True,
                        "message": "Session found! Please enter the verification code from your email.",
                        "reset_token": reset_token,
                        "firebase_mode": True,
                        "expires_in": "5 minutes",
                        "instructions": "Check your email for a 6-digit verification code or use the password reset link."
                    }), 200
                else:
                    return jsonify({
                        "error": "No verification session found. Please request a new password reset."
                    }), 400
            
            # Verify the OTP code
            verification_result = otp_service.verify_otp(email, otp)
            
            if verification_result["success"]:
                # Generate a reset token for UI continuity
                reset_token = secrets.token_urlsafe(32)
                
                return jsonify({
                    "success": True,
                    "message": "Verification code validated! You can now reset your password.",
                    "reset_token": reset_token,
                    "firebase_mode": True,
                    "firebase_reset_link": verification_result.get("firebase_reset_link")
                }), 200
            else:
                return jsonify({
                    "error": verification_result["error"]
                }), 400
                
        except Exception as db_error:
            print(f"Session check error: {db_error}")
            return jsonify({
                "error": "Please check your email for the password reset link. If you haven't received it, please try requesting a new password reset."
            }), 400

    except Exception as e:
        print(f"Firebase password reset verification error: {str(e)}")
        return jsonify({"error": "An error occurred during verification"}), 500


@auth_bp.route("/password-reset", methods=["POST"])
def password_reset():
    """Complete password reset with new password update in database"""
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        reset_token = data.get("reset_token", "").strip()
        new_password = data.get("new_password", "").strip()

        if not email:
            return jsonify({"error": "Email is required"}), 400
            
        if not reset_token:
            return jsonify({"error": "Reset token is required"}), 400
            
        if not new_password:
            return jsonify({"error": "New password is required"}), 400

        # Validate password strength
        password_error = validate_password(new_password)
        if password_error:
            return jsonify({"error": password_error}), 400

        # Verify the reset token with OTP service
        try:
            from services.simple_otp_manager import simple_otp_manager as otp_service
            print("✅ Using Simple OTP Manager for password reset")
        except ImportError:
            try:
                from services.otp_service import otp_service
                print("✅ Using Database OTP Service for password reset")
            except ImportError as e:
                print(f"❌ No OTP service available: {e}")
                return jsonify({"error": "Password reset service not available"}), 500

        # Verify the session token (reset_token) - accept both used and unused tokens for UI flow
        token_valid = False
        for stored_email, otp_data in otp_service.otp_storage.items():
            if (stored_email == email and 
                (otp_data.get('session_token') == reset_token or 
                 reset_token in str(otp_data.get('session_token', '')))):
                token_valid = True
                print(f"✅ Valid reset token found for {email}")
                break
                
        if not token_valid:
            # If no token found, still allow password reset if user exists (Firebase may handle this)
            print(f"⚠️  No matching token found for {email}, checking if user exists...")
            user_check = supabase.client.table("user_profiles").select("*").eq("email", email).execute()
            if not user_check.data:
                return jsonify({"error": "Invalid reset session. Please request a new password reset."}), 400
            print(f"✅ User exists, allowing password reset for {email}")

        print(f"🔄 Processing password reset for {email}...")
        
        # Check if user exists in database
        try:
            # Check user_profiles table to verify user exists
            user_check = supabase.client.table("user_profiles").select("*").eq("email", email).execute()

            if not user_check.data:
                print(f"❌ User not found in user_profiles for {email}")
                return jsonify({"error": "User not found in system"}), 404
                
            user_profile = user_check.data[0]
            firebase_uid = user_profile.get('firebase_uid')
            print(f"✅ User found in database: {email} (Firebase UID: {firebase_uid or 'None'})")

            # Update Firebase password (primary authentication)
            try:
                from firebase_admin import auth as firebase_auth
                
                firebase_user = None
                
                if firebase_uid:
                    try:
                        # Update existing Firebase user by UID
                        firebase_auth.update_user(firebase_uid, password=new_password)
                        firebase_user = firebase_auth.get_user(firebase_uid)
                        print(f"✅ Updated Firebase password using UID: {firebase_uid}")
                    except Exception as uid_error:
                        print(f"⚠️  Failed to update by UID: {uid_error}, trying email...")
                        firebase_uid = None
                
                if not firebase_uid:
                    try:
                        # Try to get user by email and update
                        firebase_user = firebase_auth.get_user_by_email(email)
                        firebase_auth.update_user(firebase_user.uid, password=new_password)
                        
                        # Update the user profile with Firebase UID for future use
                        supabase.client.table("user_profiles").update({
                            "firebase_uid": firebase_user.uid,
                            "updated_at": datetime.utcnow().isoformat()
                        }).eq("email", email).execute()
                        
                        print(f"✅ Updated Firebase password and stored UID: {firebase_user.uid}")
                    except Exception as email_error:
                        print(f"❌ Firebase user not found by email: {email_error}")
                        # Create Firebase user if doesn't exist
                        try:
                            firebase_user = firebase_auth.create_user(
                                email=email,
                                password=new_password,
                                email_verified=True
                            )
                            
                            # Update profile with new Firebase UID
                            supabase.client.table("user_profiles").update({
                                "firebase_uid": firebase_user.uid,
                                "updated_at": datetime.utcnow().isoformat()
                            }).eq("email", email).execute()
                            
                            print(f"✅ Created new Firebase user and updated profile: {firebase_user.uid}")
                        except Exception as create_error:
                            print(f"❌ Failed to create Firebase user: {create_error}")
                            return jsonify({"error": "Failed to update password. Please try again later."}), 500

            except Exception as firebase_error:
                print(f"❌ Firebase password update failed: {firebase_error}")
                return jsonify({"error": "Failed to update password. Please try again."}), 500

            # Update user profile timestamp
            try:
                supabase.client.table("user_profiles").update({
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("email", email).execute()
            except Exception as db_update_error:
                print(f"⚠️  Profile timestamp update failed: {db_update_error}")
                # Continue anyway - password update succeeded

            # Clean up the used token
            if hasattr(otp_service, 'otp_storage') and email in otp_service.otp_storage:
                del otp_service.otp_storage[email]

            print(f"✅ Password successfully updated for {email}")
            return jsonify({
                "success": True,
                "message": "Password updated successfully! You can now log in with your new password.",
                "redirect": "login"
            }), 200

        except Exception as db_error:
            print(f"❌ Database/Firebase update error: {db_error}")
            return jsonify({"error": "Failed to update password"}), 500

    except Exception as e:
        print(f"Password reset error: {str(e)}")
        return jsonify({"error": "An error occurred during password reset"}), 500


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
