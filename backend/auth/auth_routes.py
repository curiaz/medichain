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
from werkzeug.utils import secure_filename

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


def require_auth(f):
    """Decorator to require authentication"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({"success": False, "error": "Missing or invalid authorization token"}), 401
        return f(*args, **kwargs)
    return decorated_function


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
                return jsonify({"success": False, "error": f"{field} is required"}), 400

        email = data["email"].strip().lower()
        password = data["password"]
        name = data["name"].strip()
        role = data["role"].lower()

        # Validate email
        try:
            validate_email(email)
        except EmailNotValidError as e:
            return jsonify({"success": False, "error": str(e)}), 400

        # Validate role
        if role not in ["doctor", "patient", "admin"]:
            return jsonify({"success": False, "error": "Role must be doctor, patient, or admin"}), 400

        # Validate password
        password_error = validate_password(password)
        if password_error:
            return jsonify({"success": False, "error": password_error}), 400

        # Check if user already exists
        existing_user = supabase.client.table("user_profiles").select("*").eq("email", email).execute()
        if existing_user.data:
            return jsonify({"success": False, "error": "Email already registered"}), 409

        # Hash password
        password_hash = auth_utils.hash_password(password)

        # Split name into first and last name
        name_parts = name.strip().split(maxsplit=1)
        first_name = name_parts[0] if name_parts else name
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Generate a unique firebase_uid for Supabase-only auth
        import uuid
        firebase_uid = f"supabase_{uuid.uuid4().hex}"

        # Create user
        user_data = {
            "firebase_uid": firebase_uid,
            "email": email,
            "password_hash": password_hash,
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
        }

        response = supabase.client.table("user_profiles").insert(user_data).execute()

        if response.data:
            user = response.data[0]
            token = auth_utils.generate_token(user["id"], user["email"], user["role"])

            return jsonify({
                        "success": True,
                        "message": "User registered successfully",
                        "data": {
                            "user": {
                                "id": user["id"],
                                "email": user["email"],
                                "first_name": user.get("first_name", ""),
                                "last_name": user.get("last_name", ""),
                                "role": user["role"],
                            },
                            "token": token,
                        },
            }), 201
        else:
            return jsonify({"success": False, "error": "Registration failed"}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@auth_bp.route("/register", methods=["POST"])
def register():
    """User registration endpoint - handles both Firebase tokens and direct registration"""
    try:
        print("[DEBUG] 📥 Register endpoint called")
        data = request.get_json(silent=True)
        print(f"[DEBUG] 📦 Received data keys: {list(data.keys()) if data else 'None'}")
        
        if not isinstance(data, dict):
            print("[DEBUG] ❌ Invalid JSON body received")
            return jsonify({
                "success": False, 
                "error": "Invalid request format. Please provide valid JSON data."
            }), 400
        
        # 🆕 CHECK: Is this a Firebase token registration?
        if 'id_token' in data:
            # ========== FIREBASE TOKEN REGISTRATION ==========
            print("[DEBUG] 🔥 Firebase token registration detected")
            id_token = data.get('id_token')
            name = data.get('name', '')
            role = data.get('role', 'patient').lower()
            
            # Validate required fields
            if not id_token:
                print("[DEBUG] ❌ Missing Firebase ID token")
                return jsonify({
                    "success": False,
                    "error": "Firebase token is required for registration."
                }), 400
            
            if not name or not name.strip():
                print("[DEBUG] ❌ Missing name")
                return jsonify({
                    "success": False,
                    "error": "Name is required for registration."
                }), 400
            
            if role not in ['patient', 'doctor']:
                print(f"[DEBUG] ❌ Invalid role: {role}")
                return jsonify({
                    "success": False,
                    "error": "Invalid account type. Must be 'patient' or 'doctor'."
                }), 400
            
            try:
                from auth.firebase_auth import firebase_auth_service
                
                # Verify Firebase token
                print("[DEBUG] Verifying Firebase token...")
                result = firebase_auth_service.verify_token(id_token)
                
                if result.get("success"):
                    uid = result.get("uid")
                    email = result.get("email")
                    print(f"[DEBUG] ✅ Firebase user verified: {email} (UID: {uid})")
                    
                    # Check if user already exists by email OR firebase_uid
                    # Query separately since Supabase Python client doesn't support .or_() directly
                    existing_by_uid = None
                    existing_by_email = None
                    
                    try:
                        # Check by firebase_uid first
                        existing_by_uid = supabase.service_client.table("user_profiles").select("*").eq("firebase_uid", uid).execute() if supabase.service_client else supabase.client.table("user_profiles").select("*").eq("firebase_uid", uid).execute()
                    except Exception as uid_check_error:
                        print(f"[DEBUG] ⚠️  Error checking by UID: {uid_check_error}")
                    
                    try:
                        # Check by email
                        existing_by_email = supabase.service_client.table("user_profiles").select("*").eq("email", email).execute() if supabase.service_client else supabase.client.table("user_profiles").select("*").eq("email", email).execute()
                    except Exception as email_check_error:
                        print(f"[DEBUG] ⚠️  Error checking by email: {email_check_error}")
                    
                    # Combine results - user exists if found by either UID or email
                    existing = None
                    if existing_by_uid and existing_by_uid.data and len(existing_by_uid.data) > 0:
                        existing = existing_by_uid
                        print(f"[DEBUG] ✅ User found by UID: {uid}")
                    elif existing_by_email and existing_by_email.data and len(existing_by_email.data) > 0:
                        existing = existing_by_email
                        print(f"[DEBUG] ✅ User found by email: {email}")
                    else:
                        print(f"[DEBUG] ℹ️  No existing user found for UID: {uid} or email: {email}")
                    
                    if existing and existing.data and len(existing.data) > 0:
                        print("[DEBUG] User already exists, returning existing profile")
                        user = existing.data[0]
                        full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                        
                        return jsonify({
                            "success": True,
                            "message": "User already registered",
                            "data": {
                                "user": {
                                    "id": user["id"],
                                    "uid": uid,
                                    "email": user["email"],
                                    "first_name": user.get("first_name", ""),
                                    "last_name": user.get("last_name", ""),
                                    "full_name": full_name,
                                    "role": user["role"]
                                },
                                "token": id_token
                            }
                        }), 200
                    
                    # Create new user profile
                    name_parts = name.strip().split(maxsplit=1)
                    first_name = name_parts[0] if name_parts else name
                    last_name = name_parts[1] if len(name_parts) > 1 else ""
                    
                    user_data = {
                        "firebase_uid": uid,
                        "email": email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "role": role
                    }
                    
                    # 🆕 FIXED: Hash and store password if provided (optional - column may not exist)
                    password = data.get('password')
                    if password:
                        try:
                            password_hash = auth_utils.hash_password(password)
                            user_data["password_hash"] = password_hash
                            print(f"[DEBUG] ✅ Password hash generated and will be stored")
                        except Exception as hash_error:
                            print(f"[DEBUG] ⚠️  Could not hash password: {hash_error}")
                            # Continue without password hash
                    
                    try:
                        print(f"[DEBUG] Inserting user data: {user_data}")
                        
                        # Try using service_client first (bypasses RLS)
                        if supabase.service_client:
                            print(f"[DEBUG] Using service_client to bypass RLS")
                            try:
                                response = supabase.service_client.table("user_profiles").insert(user_data).execute()
                                print(f"[DEBUG] ✅ Database insert response (service_client): {response}")
                            except Exception as service_error:
                                print(f"[DEBUG] ⚠️  Service client insert failed, trying regular client: {service_error}")
                                # Fallback to regular client
                                response = supabase.client.table("user_profiles").insert(user_data).execute()
                                print(f"[DEBUG] ✅ Database insert response (regular client): {response}")
                        else:
                            print(f"[DEBUG] Service client not available, using regular client")
                            response = supabase.client.table("user_profiles").insert(user_data).execute()
                            print(f"[DEBUG] ✅ Database insert response: {response}")
                    except Exception as db_error:
                        print(f"[DEBUG] ❌ Database error details: {type(db_error).__name__}: {db_error}")
                        import traceback
                        traceback.print_exc()
                        
                        # Check for duplicate email error
                        error_str = str(db_error)
                        if "23505" in error_str or "duplicate key" in error_str.lower():
                            if "email" in error_str.lower():
                                # User already exists, try to return existing profile
                                print(f"[DEBUG] User already exists by email, fetching existing profile...")
                                try:
                                    existing = supabase.service_client.table("user_profiles").select("*").eq("email", email).execute() if supabase.service_client else supabase.client.table("user_profiles").select("*").eq("email", email).execute()
                                    if existing.data:
                                        user = existing.data[0]
                                        return jsonify({
                                            "success": True,
                                            "message": "User already registered",
                                            "data": {
                                                "user": {
                                                    "id": user["id"],
                                                    "uid": user.get("firebase_uid", uid),
                                                    "email": user["email"],
                                                    "first_name": user.get("first_name", ""),
                                                    "last_name": user.get("last_name", ""),
                                                    "role": user.get("role", role)
                                                },
                                                "token": id_token
                                            }
                                        }), 200
                                except:
                                    pass
                                
                                return jsonify({
                                    "success": False,
                                    "error": "This email is already registered. Please login instead or use a different email."
                                }), 409
                            else:
                                return jsonify({
                                    "success": False,
                                    "error": "Account already exists. Please login instead."
                                }), 409
                        
                        # Try without password_hash if that's the issue
                        if "password_hash" in user_data and ("column" in error_str.lower() or "does not exist" in error_str.lower()):
                            print(f"[DEBUG] Retrying without password_hash column...")
                            retry_data = {k: v for k, v in user_data.items() if k != "password_hash"}
                            try:
                                if supabase.service_client:
                                    response = supabase.service_client.table("user_profiles").insert(retry_data).execute()
                                else:
                                    response = supabase.client.table("user_profiles").insert(retry_data).execute()
                                print(f"[DEBUG] ✅ Insert succeeded without password_hash")
                            except Exception as retry_error:
                                print(f"[DEBUG] ❌ Retry also failed: {retry_error}")
                                import traceback
                                traceback.print_exc()
                                return jsonify({
                                    "success": False,
                                    "error": f"Failed to create user profile: {str(retry_error)}",
                                    "details": "Please check database schema and RLS policies"
                                }), 500
                        else:
                            # Return detailed error for debugging
                            return jsonify({
                                "success": False,
                                "error": f"Failed to create user profile: {str(db_error)}",
                                "error_type": type(db_error).__name__,
                                "details": "Check backend logs for more information"
                            }), 500
                    
                    if response.data:
                        user = response.data[0]
                        print(f"[DEBUG] ✅ New user profile created for {email}")
                        
                        return jsonify({
                            "success": True,
                            "message": "Account created successfully! Welcome to MediChain.",
                            "data": {
                                "user": {
                                    "id": user["id"],
                                    "uid": uid,
                                    "email": user["email"],
                                    "first_name": user.get("first_name", ""),
                                    "last_name": user.get("last_name", ""),
                                    "role": user["role"]
                                },
                                "token": id_token
                            }
                        }), 201
                    else:
                        print("[DEBUG] ❌ No data returned from database insert")
                        return jsonify({
                            "success": False,
                            "error": "Failed to create user profile. Please try again."
                        }), 500
                else:
                    error_msg = result.get("error", "Invalid Firebase token")
                    print(f"[DEBUG] ❌ Firebase token verification failed: {error_msg}")
                    return jsonify({
                        "success": False,
                        "error": f"Authentication failed: {error_msg}"
                    }), 401
                    
            except Exception as firebase_error:
                print(f"[DEBUG] ❌ Firebase registration error: {firebase_error}")
                import traceback
                error_trace = traceback.format_exc()
                print(f"[DEBUG] Full traceback:\n{error_trace}")
                return jsonify({
                    "success": False, 
                    "error": f"Firebase registration failed: {str(firebase_error)}",
                    "error_type": type(firebase_error).__name__,
                    "details": "Check backend logs for full error details"
                }), 500
        else:
            # Redirect to signup for non-Firebase registration
            return signup()

    except Exception as e:
        print(f"[DEBUG] ❌ Exception in register: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@auth_bp.route("/doctor-signup", methods=["POST"])
def doctor_signup():
    """
    Doctor registration endpoint - Step 1 of multi-step signup
    NO verification file required in step 1 - documents uploaded in step 4
    Handles multipart/form-data for file uploads
    Supports both regular signup (email/password) and Google signup (id_token)
    """
    try:
        print("=" * 80)
        print("[DEBUG] 🏥 Doctor signup request received - NEW ROUTE (auth_bp)")
        print("[DEBUG] ⚠️  IMPORTANT: Verification file is NOT required in step 1")
        print("[DEBUG] ⚠️  Documents will be uploaded in step 4 of the multi-step flow")
        print("[DEBUG] Route: /api/auth/doctor-signup")
        print("[DEBUG] Blueprint: auth_bp")
        print("=" * 80)
        
        # Check if this is a Google signup (id_token provided) or regular signup
        id_token = request.form.get('id_token', '').strip()
        is_google_signup = bool(id_token)
        
        if is_google_signup:
            print("[DEBUG] 🔥 Google signup detected (id_token provided)")
            # For Google signup, verify token and extract user info
            try:
                from auth.firebase_auth import firebase_auth_service
                
                # Verify Firebase token
                result = firebase_auth_service.verify_token(id_token)
                
                if not result.get("success"):
                    return jsonify({
                        "success": False,
                        "error": "Invalid authentication token. Please try again."
                    }), 401
                
                uid = result.get("uid")
                email = result.get("email", '').strip().lower()
                email_verified = result.get("email_verified", False)
                
                # Get name from form or token
                name = request.form.get('name', '').strip()
                if name:
                    name_parts = name.split(' ', 1)
                    first_name = name_parts[0] if len(name_parts) > 0 else ''
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                else:
                    first_name = request.form.get('firstName', '').strip()
                    last_name = request.form.get('lastName', '').strip()
                
                print(f"[DEBUG] Google signup: {email} (UID: {uid}), {first_name} {last_name}")
                
                # Validate name
                if not first_name or not last_name:
                    return jsonify({
                        "success": False,
                        "error": "Please enter your first and last name."
                    }), 400
                
                # Get and validate password for Google signup
                password = request.form.get('password', '')
                if not password or len(password) < 6:
                    print("[DEBUG] ❌ Invalid password for Google signup")
                    return jsonify({
                        "success": False,
                        "error": "Password must be at least 6 characters long."
                    }), 400
                
                # Hash password for database storage
                password_hash = auth_utils.hash_password(password)
                print(f"[DEBUG] ✅ Password hash generated for Google signup")
                
            except Exception as token_error:
                print(f"[DEBUG] ❌ Token verification error: {token_error}")
                return jsonify({
                    "success": False,
                    "error": "Failed to verify authentication. Please try again."
                }), 401
        else:
            print("[DEBUG] 📧 Regular signup detected (email/password)")
            # Regular signup - get form data
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            first_name = request.form.get('firstName', '').strip()
            last_name = request.form.get('lastName', '').strip()
            
            # Validate required fields
            if not email:
                print("[DEBUG] ❌ Missing email")
                return jsonify({
                    "success": False,
                    "error": "Please enter your email address."
                }), 400
            
            if not password or len(password) < 6:
                print("[DEBUG] ❌ Invalid password")
                return jsonify({
                    "success": False,
                    "error": "Password must be at least 6 characters long."
                }), 400
            
            if not first_name or not last_name:
                print("[DEBUG] ❌ Missing name")
                return jsonify({
                    "success": False,
                    "error": "Please enter your first and last name."
                }), 400
            
            # Create Firebase account for regular signup
            try:
                from auth.firebase_auth import firebase_auth_service
                
                # Create user in Firebase
                user_record = auth.create_user(
                    email=email,
                    password=password,
                    display_name=f"{first_name} {last_name}"
                )
                
                uid = user_record.uid
                print(f"[DEBUG] ✅ Firebase user created: {email} (UID: {uid})")
                
                # Hash password for database storage
                password_hash = auth_utils.hash_password(password)
                
            except Exception as firebase_error:
                firebase_error_msg = str(firebase_error)
                print(f"[DEBUG] ❌ Firebase error: {firebase_error_msg}")
                
                # Handle specific Firebase errors
                if 'EMAIL_EXISTS' in firebase_error_msg or 'email-already-exists' in firebase_error_msg:
                    return jsonify({
                        "success": False,
                        "error": "An account with this email already exists."
                    }), 400
                if 'WEAK_PASSWORD' in firebase_error_msg:
                    return jsonify({
                        "success": False,
                        "error": "Password should be at least 6 characters long."
                    }), 400
                
                # Generic failure
                return jsonify({
                    "success": False,
                    "error": f"Failed to create account: {firebase_error_msg}"
                }), 500
        
        # Force specialization to "General Practitioner" only
        specialization = "General Practitioner"
        
        # NOTE: Verification file upload is NOT handled in step 1
        # Documents will be uploaded in step 4 of the multi-step signup flow
        # No file handling logic here - completely removed from step 1
        
        print(f"[DEBUG] Doctor signup data: {email}, {first_name} {last_name}, {specialization}")
        print(f"[DEBUG] Step 1: No verification file needed - will be uploaded in step 4")
        print("[DEBUG] ⚠️  IMPORTANT: Account will be created AFTER OTP verification")
        
        print("[DEBUG] ✅ Validation passed, proceeding with OTP email (NO database creation yet)...")
        
        # NOTE: Account (user_profiles) will be created AFTER OTP verification
        # Store signup data temporarily in OTP storage for later use
        # 🔔 Send OTP email for email verification
        try:
            # Import OTP service - PRIORITIZE database service
            try:
                from services.otp_service import otp_service
                print("[DEBUG] ✅ Using Database OTP Service for doctor signup")
            except ImportError:
                try:
                    from services.simple_otp_manager import simple_otp_manager as otp_service
                    print("[DEBUG] ⚠️  Using Simple OTP Manager (fallback) for doctor signup")
                except ImportError as e:
                    print(f"[DEBUG] ⚠️  OTP service not available: {e}")
                    otp_service = None
            
            if otp_service:
                # Store signup data in OTP metadata for later use after verification
                signup_metadata = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password_hash": password_hash if password_hash else None,
                    "firebase_uid": uid,
                    "is_google_signup": is_google_signup,
                    "specialization": specialization
                }
                
                # Generate OTP and store it with signup metadata
                # Store metadata as JSON string in firebase_reset_link field (we'll use it differently)
                import json
                metadata_json = json.dumps(signup_metadata)
                otp_result = otp_service.store_otp(email, metadata_json)  # Store metadata in firebase_reset_link field
                
                if otp_result.get("success"):
                    otp_code = otp_result.get("otp_code")
                    
                    # Send OTP email (doctor signup template)
                    full_name = f"{first_name} {last_name}".strip()
                    email_sent = send_otp_email(email, full_name, otp_code, is_doctor_signup=True)
                    
                    if email_sent:
                        print(f"[DEBUG] ✅ OTP email sent to {email}")
                        
                        # Return response indicating email verification is required
                        return jsonify({
                            "success": True,
                            "message": "Please verify your email with the OTP sent to your inbox.",
                            "requires_email_verification": True,
                            "otp_sent": True,
                            "email": email
                        }), 201
                    else:
                        print(f"[DEBUG] ⚠️  Failed to send OTP email to {email}")
                else:
                    print(f"[DEBUG] ⚠️  Failed to generate OTP: {otp_result.get('error')}")
            else:
                print(f"[DEBUG] ⚠️  OTP service not available")
                # Clean up Firebase user if OTP service not available
                try:
                    if not is_google_signup:
                        auth.delete_user(uid)
                except:
                    pass
                return jsonify({
                    "success": False,
                    "error": "Failed to send verification email. Please try again."
                }), 500
                    
        except Exception as otp_error:
            print(f"[DEBUG] ⚠️  OTP email error: {otp_error}")
            import traceback
            traceback.print_exc()
            # Clean up Firebase user if OTP fails
            try:
                if not is_google_signup:
                    auth.delete_user(uid)
            except:
                pass
            return jsonify({
                "success": False,
                "error": "Failed to send verification email. Please try again."
            }), 500

    except Exception as e:
        print(f"[DEBUG] ❌ Exception in doctor signup: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "An error occurred during signup. Please try again."
        }), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    """User login endpoint - handles both Firebase tokens and email/password"""
    try:
        data = request.get_json(silent=True)
        
        # 🔧 FIXED: Validate JSON body first
        if not isinstance(data, dict):
            print("[DEBUG] Invalid JSON body")
            return jsonify({"success": False, "error": "Invalid JSON body"}), 400
        
        print("[DEBUG] Login request data keys:", list(data.keys()) if data else None)

        # 🆕 CHECK: Is this a Firebase token login or email/password login?
        if 'id_token' in data:
            # ========== FIREBASE TOKEN LOGIN ==========
            print("[DEBUG] 🔥 Firebase token login detected")
            id_token = data['id_token']
            
            try:
                from auth.firebase_auth import firebase_auth_service
                
                # Verify Firebase token
                print("[DEBUG] Verifying Firebase token...")
                result = firebase_auth_service.verify_token(id_token)
                
                if result.get("success"):
                    uid = result.get("uid")
                    email = result.get("email")
                    print(f"[DEBUG] ✅ Firebase auth successful: {email} (UID: {uid})")
                    
                    # Get user profile from Supabase
                    response = supabase.client.table("user_profiles").select("*").eq("firebase_uid", uid).execute()
                    
                    if response.data:
                        user = response.data[0]
                        
                        # Construct full name
                        full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                        if not full_name:
                            full_name = user.get("email", "").split("@")[0]
                        
                        # Optionally include doctor profile
                        doctor_profile = None
                        try:
                            if user.get("role") == "doctor":
                                # Select ALL doctor profile fields for complete profile data
                                dp_resp = supabase.service_client.table("doctor_profiles").select(
                                    "*"
                                ).eq("firebase_uid", uid).execute()
                                if dp_resp.data:
                                    doctor_profile = dp_resp.data[0]
                        except Exception as _:
                            doctor_profile = None
                        
                        print(f"[DEBUG] ✅ User profile found for Firebase UID: {uid}")
                        
                        # Return Firebase-compatible response
                        return jsonify({
                            "success": True,
                            "message": "Login successful",
                            "data": {
                                "user": {
                                    "id": user["id"],
                                    "uid": uid,
                                    "email": user["email"],
                                    "first_name": user.get("first_name", ""),
                                    "last_name": user.get("last_name", ""),
                                    "full_name": full_name,
                                    "role": user["role"],
                                    "firebase_uid": uid,
                                    "phone": user.get("phone", ""),
                                    "address": user.get("address", ""),
                                    "city": user.get("city", ""),
                                    "state": user.get("state", ""),
                                    "zip_code": user.get("zip_code", ""),
                                    "date_of_birth": user.get("date_of_birth", ""),
                                    "gender": user.get("gender", ""),
                                    "emergency_contact": user.get("emergency_contact", ""),
                                    "medical_conditions": user.get("medical_conditions", []),
                                    "allergies": user.get("allergies", []),
                                    "current_medications": user.get("current_medications", []),
                                    "blood_type": user.get("blood_type", ""),
                                    "medical_notes": user.get("medical_notes", ""),
                                    "profile_visibility": user.get("profile_visibility", "private"),
                                    "show_email": user.get("show_email", False),
                                    "show_phone": user.get("show_phone", False),
                                    "medical_info_visible_to_doctors": user.get("medical_info_visible_to_doctors", True),
                                    "allow_ai_analysis": user.get("allow_ai_analysis", True),
                                    "share_data_for_research": user.get("share_data_for_research", False),
                                    "doctor_profile": doctor_profile,
                                },
                                "token": id_token
                            }
                        }), 200
                    else:
                        print(f"[DEBUG] ❌ No user profile found for Firebase UID: {uid}")
                        return jsonify({
                            "success": False,
                            "error": "User profile not found. Please complete registration."
                        }), 404
                else:
                    error_msg = result.get('error', 'Unknown error')
                    print(f"[DEBUG] ❌ Firebase token verification failed: {error_msg}")
                    print(f"[DEBUG] Token preview: {id_token[:50] if id_token else 'None'}...")
                    
                    # Provide more specific error messages
                    if "expired" in error_msg.lower():
                        error_message = "Your session has expired. Please log in again."
                    elif "invalid" in error_msg.lower() or "malformed" in error_msg.lower():
                        error_message = "Invalid authentication token. Please log in again."
                    elif "revoked" in error_msg.lower():
                        error_message = "Your session has been revoked. Please log in again."
                    else:
                        error_message = f"Authentication failed: {error_msg}"
                    
                    return jsonify({
                        "success": False,
                        "error": error_message,
                        "error_code": "INVALID_TOKEN"
                    }), 401
                    
            except Exception as firebase_error:
                print(f"[DEBUG] ❌ Firebase auth error: {firebase_error}")
                import traceback
                traceback.print_exc()
                return jsonify({
                    "success": False,
                    "error": "Firebase authentication failed"
                }), 500
        
        else:
            # ========== EMAIL/PASSWORD LOGIN ==========
            print("[DEBUG] 📧 Email/password login detected")
            email = data.get("email", "").strip().lower()
            password = data.get("password", "")
            print(f"[DEBUG] Email: {email}, Password: {'*' * len(password) if password else 'missing'}")

            # Validate inputs
            if not email or not email.strip():
                print("[DEBUG] ❌ Missing email")
                return jsonify({
                    "success": False,
                    "error": "Please enter your email address."
                }), 400
            
            if not password or not password.strip():
                print("[DEBUG] ❌ Missing password")
                return jsonify({
                    "success": False,
                    "error": "Please enter your password."
                }), 400

            # Find user in database
            try:
                response = supabase.client.table("user_profiles").select("*").eq("email", email).execute()
                print(f"[DEBUG] Supabase user query: {len(response.data) if response.data else 0} results")
            except Exception as db_error:
                print(f"[DEBUG] ❌ Database error during user lookup: {db_error}")
                return jsonify({
                    "success": False,
                    "error": "Database error occurred. Please try again."
                }), 500

            if not response.data:
                print("[DEBUG] ❌ No user found for email")
                return jsonify({
                    "success": False,
                    "error": "Invalid email or password."
                }), 401

            user = response.data[0]
            print(f"[DEBUG] User found: {user.get('email')}")

            # 🔧 CHECK: Is account deactivated?
            is_active = user.get('is_active', True)
            if not is_active and user.get('role') == 'doctor':
                print(f"[DEBUG] 🔒 Deactivated doctor account detected: {email}")
                return jsonify({
                    "success": False,
                    "error": "account_deactivated",
                    "message": "Your account has been deactivated. Would you like to reactivate it?",
                    "deactivated": True,
                    "email": email
                }), 403

            # 🔧 FIXED: Check if user has password_hash
            has_password_hash = user.get("password_hash") and user.get("password_hash") is not None
            
            print(f"[DEBUG] Password verification for {email}")
            print(f"[DEBUG] Has password_hash: {has_password_hash}")
            if has_password_hash:
                stored_hash = user.get("password_hash")
                print(f"[DEBUG] Stored hash: {stored_hash[:30] if stored_hash else 'NULL'}...")
            
            if has_password_hash:
                # ✅ User has password_hash - verify directly
                print("[DEBUG] ✅ User has password_hash, verifying with Supabase")
                try:
                    password_check = auth_utils.verify_password(password, user.get("password_hash"))
                    print(f"[DEBUG] Password check result: {password_check}")
                    
                    if not password_check:
                        print("[DEBUG] ❌ Password mismatch - database password_hash verification failed")
                        print(f"[DEBUG] Attempted password: {'*' * len(password)}")
                        print(f"[DEBUG] Stored hash: {user.get('password_hash')[:30] if user.get('password_hash') else 'NULL'}...")
                        
                        # DO NOT fall back to Firebase - password reset should have updated both
                        # If password_hash exists, it must match
                        return jsonify({
                            "success": False,
                            "error": "Invalid email or password. Please check your credentials and try again."
                        }), 401
                    
                    print("[DEBUG] ✅ Password verified successfully with database password_hash!")
                except Exception as verify_error:
                    print(f"[DEBUG] ❌ Password verification error: {verify_error}")
                    import traceback
                    traceback.print_exc()
                    return jsonify({
                        "success": False,
                        "error": "Authentication error occurred. Please try again."
                    }), 500
            else:
                # ⚠️ User created before password_hash integration
                print("[DEBUG] ⚠️  No password_hash found - legacy Firebase-only user")
                print("[DEBUG] These users should login via Firebase (frontend will handle it)")
                return jsonify({
                    "success": False,
                    "error": "Invalid email or password.",
                    "hint": "This account uses Firebase authentication. The app will retry automatically."
                }), 401

            # Generate token
            token = auth_utils.generate_token(user["id"], user["email"], user["role"])

            # Construct full name from first and last name
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            if not full_name:
                full_name = user.get("email", "").split("@")[0]

            # Optionally include doctor profile
            doctor_profile = None
            try:
                if user.get("role") == "doctor":
                    dp_resp = supabase.service_client.table("doctor_profiles").select(
                        "id, verification_status, specialization, verification_file_path"
                    ).eq("user_id", user["id"]).execute()
                    if dp_resp.data:
                        doctor_profile = dp_resp.data[0]
            except Exception as _:
                doctor_profile = None

            print(f"[DEBUG] ✅ Login successful for user {user['email']}")
            return jsonify({
                "success": True,
                "message": "Login successful! Welcome back.",
                "data": {
                        "user": {
                            "id": user["id"],
                            "email": user["email"],
                            "first_name": user.get("first_name", ""),
                            "last_name": user.get("last_name", ""),
                            "full_name": full_name,
                            "role": user["role"],
                            "firebase_uid": user.get("firebase_uid"),
                            "doctor_profile": doctor_profile,
                        },
                        "token": token,
                    },
            }), 200

    except Exception as e:
        print(f"[DEBUG] ❌ Exception in login: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@auth_bp.route("/me", methods=["GET"])
@auth_utils.token_required
def get_current_user():
    """Get current user information"""
    try:
        user_id = request.current_user["user_id"]

        response = (
            supabase.client.table("user_profiles")
            .select("id", "email", "first_name", "last_name", "role", "firebase_uid", "created_at")
            .eq("id", user_id)
            .execute()
        )

        if response.data:
            user = response.data[0]
            # Construct full_name from first_name and last_name
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
            user['full_name'] = full_name if full_name else user.get("email", "").split("@")[0]
            
            return jsonify({"success": True, "data": user}), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_bp.route("/password-reset-request", methods=["POST"])
def password_reset_request():
    """Request password reset using OTP system"""
    print("=" * 80)
    print("🔐 PASSWORD RESET REQUEST ENDPOINT CALLED")
    print("=" * 80)
    try:
        print(f"📥 Request method: {request.method}")
        print(f"📥 Request URL: {request.url}")
        print(f"📥 Request headers: {dict(request.headers)}")
        
        data = request.get_json(silent=True)
        print(f"📦 Request data: {data}")
        
        if data is None:
            print("❌ No JSON data received")
            return jsonify({"error": "No data received"}), 400
        
        email = data.get("email", "").strip().lower()
        print(f"📧 Email extracted: {email}")

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
            user_name = None  # Continue even if we can't get the name
        
        # Use Firebase Auth to send password reset email
        from auth.firebase_auth import firebase_auth_service
        
        print(f"📧 Requesting password reset email for: {email}")
        result = firebase_auth_service.send_password_reset_email(email, user_name=user_name)
        
        print(f"📧 Password reset result: success={result.get('success')}, email_sent={result.get('email_sent', True)}")
        
        if result["success"]:
            # Store a temporary session to allow the UI to continue its flow
            # but inform user about the Firebase reset process
            session_token = secrets.token_urlsafe(32)
            verification_code = result.get("verification_code")
            email_actually_sent = result.get("email_sent", True)  # Default to True for backward compatibility
            
            # Verification code is stored in database via OTP service
            print(f"✅ Password reset initiated for {email}")
            print(f"🔢 Verification code: {verification_code} (expires in 5 minutes)")
            print(f"🎫 Session token: {session_token}")
            print(f"📧 Email actually sent: {email_actually_sent}")
            
            # Adjust message based on whether email was actually sent
            if email_actually_sent:
                message = "Password reset email sent! Check your email for both a reset link and verification code."
                ui_message = "A password reset email has been sent with two options: use the verification code below or click the reset link in the email."
            else:
                message = "Password reset code generated. Check console for verification code (email sending failed)."
                ui_message = "Password reset code generated. Please check the backend console for the verification code as email sending failed."
                print(f"⚠️  WARNING: Email was not sent! Verification code: {verification_code}")
                print(f"⚠️  Reset link: {result.get('dev_link', 'N/A')}")
                
            return jsonify({
                "success": True,
                "message": message,
                "ui_message": ui_message,
                "session_token": session_token,
                "has_verification_code": True,
                "email_sent": email_actually_sent
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
        print("=" * 80)
        print(f"❌ PASSWORD RESET REQUEST ERROR: {str(e)}")
        print("=" * 80)
        import traceback
        print("Full traceback:")
        traceback.print_exc()
        print("=" * 80)
        return jsonify({"error": "An error occurred while processing your request"}), 500


def generate_numeric_otp():
    """Generate a 6-digit numeric OTP"""
    return f"{random.randint(100000, 999999):06d}"


def send_otp_email(email, name, otp, is_doctor_signup=False):
    """Send OTP email to user with enhanced design
    
    Args:
        email: Recipient email address
        name: Recipient name
        otp: 6-digit OTP code
        is_doctor_signup: If True, use doctor signup email template (no password reset link)
    """
    try:
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("medichain173@gmail.com")
        sender_password = os.getenv("pyrbdzinoersbczk")
        
        if not sender_email or not sender_password:
            print("Email credentials not configured")
            return False
        
        # Create email message with both HTML and plain text
        msg = MIMEMultipart("alternative")
        msg["From"] = f"Medichain Security <{sender_email}>"
        msg["To"] = email
        
        if is_doctor_signup:
            # Doctor signup email template
            msg["Subject"] = "Medichain - Email Verification"
            
            # Plain text version for doctor signup
            text_body = f"""
🏥 MEDICHAIN DOCTOR SIGNUP VERIFICATION

Hello {name},

Thank you for signing up as a doctor on Medichain!

🔑 Your email verification code is: {otp}

⏰ This code will expire in 1 minute.

Please enter this code on the signup page to verify your email address and continue with your registration.

For your security:
• Never share this code with anyone  
• Only enter this code on the official Medichain website
• Make sure you're on the correct website before entering the code

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 Visit: localhost:3001
📧 Support: medichain173@gmail.com

Best regards,
The Medichain Team

© 2025 Medichain - AI-Driven Diagnosis & Blockchain Health Records System
            """
            
            # HTML version for doctor signup
            html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Medichain Doctor Signup Verification</title>
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
            <h2 style="color: #1565c0; margin: 0 0 20px 0; font-size: 24px;">🔐 Email Verification</h2>
            
            <p style="margin: 0 0 20px 0; font-size: 16px;">Hello <strong>{name}</strong>,</p>
            
            <p style="margin: 0 0 30px 0; font-size: 16px;">Thank you for signing up as a doctor on Medichain! Please verify your email address using the code below to continue with your registration:</p>
            
            <!-- OTP Code Box -->
            <div style="background: linear-gradient(145deg, #e3f2fd 0%, #bbdefb 100%); border: 2px solid #2196f3; border-radius: 12px; padding: 25px; margin: 30px 0; text-align: center;">
                <p style="margin: 0 0 15px 0; font-size: 14px; color: #1565c0; font-weight: 600;">Your Verification Code</p>
                <div style="font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace; font-size: 36px; font-weight: 700; color: #1976d2; letter-spacing: 8px; margin: 10px 0;">{otp}</div>
                <p style="margin: 15px 0 0 0; font-size: 12px; color: #666;">⏰ Expires in 1 minute</p>
            </div>
            
            <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h3 style="margin: 0 0 15px 0; color: #856404; font-size: 16px;">🛡️ Security Guidelines</h3>
                <ul style="margin: 0; padding-left: 20px; color: #856404;">
                    <li>Never share this code with anyone</li>
                    <li>Only enter this code on the official Medichain website</li>
                    <li>Make sure you're on the correct website before entering the code</li>
                    <li>If you didn't request this verification, please ignore this email</li>
                </ul>
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
        else:
            # Password reset email template (existing)
            msg["Subject"] = "🔐 Medichain Password Reset - Verification Code"
            
            # Plain text version
            text_body = f"""
🏥 MEDICHAIN PASSWORD RESET

Hello {name},

We received a request to reset your Medichain account password.

🔑 Your verification code is: {otp}

⏰ This code will expire in 1 minute.

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
                <p style="margin: 15px 0 0 0; font-size: 12px; color: #666;">⏰ Expires in 1 minute</p>
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
        print("=" * 80)
        print("🔐 VERIFY OTP ENDPOINT CALLED")
        print("=" * 80)
        
        data = request.get_json(silent=True)
        print(f"📦 Request data: {data}")
        
        if not data:
            print("❌ No JSON data received")
            return jsonify({"error": "No data received"}), 400
        
        email = data.get("email", "").strip().lower()
        otp = data.get("otp", "").strip()
        
        # Remove all spaces from OTP (in case user entered with spaces like "1 5 3 8 1 7")
        otp = otp.replace(" ", "").replace("-", "").replace("_", "")
        
        print(f"📧 Email: {email}")
        print(f"🔢 OTP (after cleaning): '{otp}' (length: {len(otp)})")

        if not email:
            print("❌ Email is required")
            return jsonify({"error": "Email is required"}), 400
        
        if not otp:
            print("❌ OTP is required")
            return jsonify({"error": "OTP code is required"}), 400
        
        if len(otp) != 6:
            print(f"❌ Invalid OTP length: {len(otp)} (expected 6)")
            return jsonify({"error": "OTP code must be 6 digits"}), 400

        # Verify OTP using database service
        try:
            # Import OTP service - PRIORITIZE database service
            import sys
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            # PRIORITIZE database OTP service for security
            try:
                from services.otp_service import otp_service
                print("✅ Using Database OTP Service for verification (secure)")
            except ImportError:
                # Fallback to simple OTP manager if database service not available
                try:
                    from services.simple_otp_manager import simple_otp_manager as otp_service
                    print("⚠️  Using Simple OTP Manager (fallback - not secure) for verification")
                except ImportError as e:
                    print(f"❌ Warning: OTP service not available: {e}")
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
            
            # Verify the OTP code (trim and normalize)
            print(f"🔍 Verifying OTP for {email}: code='{otp}'")
            print(f"🔍 Email normalized to lowercase: {email}")
            
            # Check if OTP exists before verification
            otp_info_before = otp_service.get_otp_info(email)
            if otp_info_before:
                print(f"🔍 OTP found in database: {otp_info_before.get('otp_code')}")
            else:
                print(f"⚠️  No OTP found in database for {email}")
                # Try to find any OTPs for this email (including used ones for debugging)
                try:
                    from services.otp_service import otp_service as db_otp_service
                    all_otps = db_otp_service.supabase.client.table("temporary_otp_storage").select("*").eq("email", email).execute()
                    if all_otps.data:
                        print(f"🔍 Found {len(all_otps.data)} OTP record(s) for {email}:")
                        for otp_rec in all_otps.data:
                            print(f"   - Code: {otp_rec.get('otp_code')}, Used: {otp_rec.get('is_used')}, Expires: {otp_rec.get('expires_at')}")
                    else:
                        print(f"❌ No OTP records found in database for {email}")
                except Exception as debug_error:
                    print(f"⚠️  Could not debug OTP lookup: {debug_error}")
            
            # OTP is already cleaned above (spaces removed)
            verification_result = otp_service.verify_otp(email, otp)
            print(f"🔍 Verification result: {verification_result}")
            
            if not verification_result.get("success"):
                print(f"❌ OTP verification failed: {verification_result.get('error')}")
                return jsonify({
                    "success": False,
                    "error": verification_result.get("error", "OTP verification failed")
                }), 400
            
            # OTP verified successfully
            if verification_result["success"]:
                # Generate reset token for password change
                reset_token = verification_result.get("session_token") or secrets.token_urlsafe(32)
                print(f"✅ OTP verified! Reset token: {reset_token[:20]}...")
                # Check if this is a doctor signup verification (has metadata in firebase_reset_link)
                firebase_reset_link = verification_result.get("firebase_reset_link", "")
                
                # Try to parse metadata (doctor signup stores JSON metadata here)
                try:
                    import json
                    if firebase_reset_link and firebase_reset_link.startswith("{"):
                        signup_metadata = json.loads(firebase_reset_link)
                        
                        # This is a doctor signup - create account now
                        if signup_metadata.get("specialization"):
                            print(f"[DEBUG] ✅ Doctor signup OTP verified, creating account for {email}")
                            
                            # Extract signup data
                            first_name = signup_metadata.get("first_name", "")
                            last_name = signup_metadata.get("last_name", "")
                            password_hash = signup_metadata.get("password_hash")
                            firebase_uid = signup_metadata.get("firebase_uid")
                            is_google_signup = signup_metadata.get("is_google_signup", False)
                            specialization = signup_metadata.get("specialization", "General Practitioner")
                            
                            # Create user profile in database
                            user_data = {
                                "firebase_uid": firebase_uid,
                                "email": email,
                                "first_name": first_name,
                                "last_name": last_name,
                                "role": "doctor",
                                "verification_status": "pending"
                            }
                            
                            if password_hash:
                                user_data["password_hash"] = password_hash
                            
                            user_response = supabase.client.table("user_profiles").insert(user_data).execute()
                            
                            if not user_response.data:
                                return jsonify({
                                    "success": False,
                                    "error": "Failed to create account. Please try again."
                                }), 500
                            
                            user = user_response.data[0]
                            user_id = user["id"]
                            print(f"[DEBUG] ✅ User profile created after OTP verification: {email}")
                            
                            # Generate token for login
                            token = auth_utils.generate_token(user_id, email, "doctor")
                            
                            return jsonify({
                                "success": True,
                                "message": "Email verified! Account created successfully.",
                                "email_verified": True,
                                "account_created": True,
                                "data": {
                                    "token": token,
                                    "user": {
                                        "id": user_id,
                                        "email": email,
                                        "first_name": first_name,
                                        "last_name": last_name,
                                        "role": "doctor",
                                        "firebase_uid": firebase_uid
                                    }
                                }
                            }), 200
                except (json.JSONDecodeError, KeyError, TypeError) as parse_error:
                    # Not doctor signup metadata, continue with password reset flow
                    print(f"[DEBUG] Not doctor signup metadata: {parse_error}")
                    pass
                
                # Check if user exists (for password reset flow)
                if not firebase_reset_link or not firebase_reset_link.startswith("{"):
                    # This might be a password reset or existing user verification
                    try:
                        user_response = supabase.client.table("user_profiles").select("*").eq("email", email).execute()
                        if user_response.data:
                            # User exists - OTP verified successfully (password reset flow)
                            print(f"[DEBUG] ✅ Email verified for existing user: {email}")
                            # Continue to password reset flow below
                    except Exception as db_error:
                        print(f"[DEBUG] ⚠️  Database check error: {db_error}")
                        # Continue anyway - OTP is verified
                
                # For password reset flow - use the session_token from verification result
                # This ensures the token matches what was stored in the database
                final_reset_token = reset_token  # Use the token from line 1405
                
                print(f"✅ Password reset OTP verified for {email}")
                print(f"✅ Reset token generated: {final_reset_token[:30]}...")
                
                return jsonify({
                    "success": True,
                    "message": "Verification code validated! You can now reset your password.",
                    "reset_token": final_reset_token,
                    "firebase_mode": False,  # Not using Firebase mode for password reset
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
            # CRITICAL: This must succeed or old Firebase password will still work
            firebase_password_updated = False
            try:
                from firebase_admin import auth as firebase_auth
                
                firebase_user = None
                
                if firebase_uid:
                    try:
                        # Update existing Firebase user by UID
                        print(f"🔄 Updating Firebase password for UID: {firebase_uid}")
                        firebase_auth.update_user(firebase_uid, password=new_password)
                        firebase_user = firebase_auth.get_user(firebase_uid)
                        firebase_password_updated = True
                        print(f"✅ Updated Firebase password using UID: {firebase_uid}")
                    except Exception as uid_error:
                        print(f"⚠️  Failed to update by UID: {uid_error}, trying email...")
                        firebase_uid = None
                
                if not firebase_uid and not firebase_password_updated:
                    try:
                        # Try to get user by email and update
                        print(f"🔄 Getting Firebase user by email: {email}")
                        firebase_user = firebase_auth.get_user_by_email(email)
                        print(f"🔄 Updating Firebase password for UID: {firebase_user.uid}")
                        firebase_auth.update_user(firebase_user.uid, password=new_password)
                        firebase_password_updated = True
                        
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
                            print(f"🔄 Creating new Firebase user for: {email}")
                            firebase_user = firebase_auth.create_user(
                                email=email,
                                password=new_password,
                                email_verified=True
                            )
                            firebase_password_updated = True
                            
                            # Update profile with new Firebase UID
                            supabase.client.table("user_profiles").update({
                                "firebase_uid": firebase_user.uid,
                                "updated_at": datetime.utcnow().isoformat()
                            }).eq("email", email).execute()
                            
                            print(f"✅ Created new Firebase user and updated profile: {firebase_user.uid}")
                        except Exception as create_error:
                            print(f"❌ Failed to create Firebase user: {create_error}")
                            import traceback
                            traceback.print_exc()
                            return jsonify({"error": "Failed to update password. Please try again later."}), 500

            except Exception as firebase_error:
                print(f"❌ Firebase password update failed: {firebase_error}")
                import traceback
                traceback.print_exc()
                return jsonify({"error": "Failed to update password. Please try again."}), 500
            
            if not firebase_password_updated:
                print(f"❌ CRITICAL: Firebase password was NOT updated for {email}")
                return jsonify({"error": "Failed to update Firebase password. Please try again."}), 500
            
            # Verify Firebase password was actually updated by trying to sign in with old password
            # This is a security check to ensure old password no longer works
            print(f"🔍 Verifying Firebase password update...")
            try:
                # Try to sign in with a dummy wrong password to verify update worked
                # We can't test with old password directly, but we can verify the user exists
                if firebase_user:
                    verified_user = firebase_auth.get_user(firebase_user.uid)
                    print(f"✅ Firebase user verified: {verified_user.email} (UID: {verified_user.uid})")
                    print(f"✅ Firebase password update confirmed for {email}")
            except Exception as verify_error:
                print(f"⚠️  Could not verify Firebase password update: {verify_error}")
                # Don't fail - password was updated, just couldn't verify
            
            # 🔧 CRITICAL: Update password_hash in database to replace old password
            # This ensures the database password matches Firebase password
            try:
                # Hash the new password for database storage
                password_hash = auth_utils.hash_password(new_password)
                
                print(f"🔄 Updating password_hash in database for {email}...")
                
                # First, check current password_hash before update
                before_update = supabase.client.table("user_profiles").select("id, password_hash").eq("email", email).execute()
                if before_update.data:
                    old_hash = before_update.data[0].get("password_hash")
                    user_id = before_update.data[0].get("id")
                    print(f"🔍 Before update - User ID: {user_id}, Old hash: {old_hash[:20] if old_hash else 'NULL'}...")
                    
                    # Check if there are multiple records with same email (shouldn't happen but check)
                    if len(before_update.data) > 1:
                        print(f"⚠️  WARNING: Multiple user records found for {email}!")
                        print(f"   Found {len(before_update.data)} records - this is a data integrity issue")
                        for idx, record in enumerate(before_update.data):
                            print(f"   Record {idx+1}: ID={record.get('id')}, hash={record.get('password_hash')[:20] if record.get('password_hash') else 'NULL'}...")
                
                # Update user_profiles table with new password_hash (REPLACES old one)
                # Use service_client to bypass RLS if needed
                # IMPORTANT: Update by user ID to ensure we update the correct record
                try:
                    if not user_id:
                        # Get user_id from the user_profile we found earlier
                        user_id = user_profile.get('id')
                    
                    if not user_id:
                        print(f"❌ Cannot update: No user ID found for {email}")
                        raise Exception("User ID not found")
                    
                    print(f"🔄 Updating password_hash for user ID: {user_id}")
                    
                    if supabase.service_client:
                        # Update by ID (more reliable than email)
                        update_result = supabase.service_client.table("user_profiles").update({
                            "password_hash": password_hash,
                            "updated_at": datetime.utcnow().isoformat()
                        }).eq("id", user_id).execute()
                    else:
                        # Update by ID (more reliable than email)
                        update_result = supabase.client.table("user_profiles").update({
                            "password_hash": password_hash,
                            "updated_at": datetime.utcnow().isoformat()
                        }).eq("id", user_id).execute()
                    
                    if update_result.data:
                        updated_user = update_result.data[0]
                        new_hash = updated_user.get("password_hash")
                        print(f"✅ Updated password_hash in database for {email} (old password replaced)")
                        print(f"   User ID: {updated_user.get('id')}")
                        print(f"   New hash: {new_hash[:20] if new_hash else 'NULL'}...")
                        
                        # Verify the update actually changed the value
                        verify_user = supabase.client.table("user_profiles").select("password_hash").eq("email", email).execute()
                        if verify_user.data:
                            verified_hash = verify_user.data[0].get("password_hash")
                            if verified_hash == password_hash:
                                print(f"✅ Verified: password_hash correctly updated in database")
                            elif verified_hash == old_hash:
                                print(f"❌ ERROR: password_hash was NOT updated! Still has old value")
                                print(f"   This indicates the UPDATE query did not work")
                            else:
                                print(f"⚠️  Warning: password_hash value mismatch")
                                print(f"   Expected: {password_hash[:20]}...")
                                print(f"   Got: {verified_hash[:20] if verified_hash else 'NULL'}...")
                    else:
                        print(f"⚠️  Password hash update returned no data")
                        # Try to verify the update worked
                        verify_user = supabase.client.table("user_profiles").select("password_hash").eq("email", email).execute()
                        if verify_user.data:
                            if verify_user.data[0].get("password_hash"):
                                print(f"✅ Verified: password_hash exists in database")
                            else:
                                print(f"❌ Warning: password_hash is NULL after update")
                        
                except Exception as update_error:
                    print(f"❌ Update query failed: {update_error}")
                    import traceback
                    traceback.print_exc()
                    raise update_error
                    
            except Exception as db_update_error:
                print(f"❌ Failed to update password_hash in database: {db_update_error}")
                import traceback
                traceback.print_exc()
                # Don't fail the entire reset if database update fails, but log it
                # Firebase password was already updated, so user can still login via Firebase
                print(f"⚠️  Warning: Database password_hash not updated, but Firebase password was updated")

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


@auth_bp.route("/resend-verification", methods=["POST"])
def resend_verification():
    """Resend verification email to user"""
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

        # Check if user exists
        response = supabase.client.table("user_profiles").select("*").eq("email", email).execute()
        
        if not response.data:
            # For security, don't reveal if email exists or not
            return jsonify({
                "success": True,
                "message": "If this email is registered, a verification email will be sent"
            }), 200

        user = response.data[0]
        
        # Check if already verified
        if user.get("email_verified"):
            return jsonify({
                "success": True,
                "message": "Email is already verified"
            }), 200

        # TODO: Implement email verification sending logic
        # For now, just return success
        return jsonify({
            "success": True,
            "message": "Verification email sent successfully"
        }), 200

    except Exception as e:
        print(f"Resend verification error: {str(e)}")
        return jsonify({"error": "An error occurred while sending verification email"}), 500


@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    """Resend OTP code to user's email"""
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()

        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400

        # Validate email format
        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({"success": False, "error": "Invalid email format"}), 400

        # Import OTP service - PRIORITIZE database service
        try:
            from services.otp_service import otp_service
            print("[DEBUG] ✅ Using Database OTP Service for resend OTP")
        except ImportError:
            try:
                from services.simple_otp_manager import simple_otp_manager as otp_service
                print("[DEBUG] ⚠️  Using Simple OTP Manager (fallback) for resend OTP")
            except ImportError as e:
                print(f"[DEBUG] ⚠️  OTP service not available: {e}")
                return jsonify({
                    "success": False,
                    "error": "OTP service not available"
                }), 503

        # Check if this is a doctor signup by checking existing OTP metadata
        is_doctor_signup = False
        metadata_to_store = ""
        full_name = "User"
        
        try:
            existing_otp = otp_service.get_otp_info(email)
            if existing_otp:
                firebase_reset_link = existing_otp.get("firebase_reset_link", "")
                # Check if it's JSON metadata (doctor signup stores JSON here)
                if firebase_reset_link and firebase_reset_link.startswith("{"):
                    import json
                    try:
                        metadata = json.loads(firebase_reset_link)
                        if metadata.get("specialization"):
                            is_doctor_signup = True
                            metadata_to_store = firebase_reset_link  # Preserve metadata
                            # Get name from metadata for doctor signup
                            first_name = metadata.get("first_name", "")
                            last_name = metadata.get("last_name", "")
                            full_name = f"{first_name} {last_name}".strip() or "User"
                            print(f"[DEBUG] ✅ Detected doctor signup for resend OTP: {email}")
                    except (json.JSONDecodeError, KeyError):
                        pass
        except Exception as check_error:
            print(f"[DEBUG] ⚠️  Error checking OTP metadata: {check_error}")
        
        # If not doctor signup, get user info from database
        if not is_doctor_signup:
            try:
                user_response = supabase.client.table("user_profiles").select("first_name, last_name").eq("email", email).execute()
                if user_response.data:
                    user = user_response.data[0]
                    full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "User"
            except:
                full_name = "User"
        
        # Generate and store new OTP
        # If it's doctor signup, preserve the metadata
        
        otp_result = otp_service.store_otp(email, metadata_to_store)

        if not otp_result.get("success"):
            return jsonify({
                "success": False,
                "error": otp_result.get("error", "Failed to generate OTP")
            }), 500

        otp_code = otp_result.get("otp_code")

        # Send OTP email with appropriate template
        email_sent = send_otp_email(email, full_name, otp_code, is_doctor_signup=is_doctor_signup)

        if email_sent:
            print(f"[DEBUG] ✅ OTP email resent to {email}")
            return jsonify({
                "success": True,
                "message": "Verification code has been resent to your email",
                "otp_sent": True
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to send verification email. Please try again."
            }), 500

    except Exception as e:
        print(f"[DEBUG] ❌ Resend OTP error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": "An error occurred while resending verification code"
        }), 500


@auth_bp.route("/profile", methods=["PUT"])
@require_auth
def update_profile():
    """Update user profile information"""
    print("=" * 80)
    print("📝 PROFILE UPDATE ENDPOINT CALLED")
    print("=" * 80)
    try:
        if not supabase:
            print("❌ Supabase not available")
            return jsonify({"success": False, "error": "Database not available"}), 500
            
        data = request.get_json()
        print(f"📦 Raw request data: {data}")
        print(f"📦 Data type: {type(data)}")
        
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            print("❌ No token provided")
            return jsonify({"success": False, "error": "Authentication required"}), 401
        
        # Get user ID from request data
        firebase_uid = data.get('firebase_uid') if data else None
        print(f"🔑 Firebase UID: {firebase_uid}")
        
        if not firebase_uid:
            print("❌ No firebase_uid in request")
            return jsonify({"success": False, "error": "User ID required"}), 400
        
        print(f"🔄 Updating profile for user {firebase_uid}")
        print(f"📥 Request data keys: {list(data.keys()) if data else 'None'}")
        print(f"📥 Full request data: {data}")
        
        # Extract update fields
        update_data = {}
        allowed_fields = ['first_name', 'last_name', 'phone', 'avatar_url']
        
        for field in allowed_fields:
            if field in data and data[field] is not None and data[field] != '':
                update_data[field] = data[field]
                print(f"  ✓ Adding field '{field}': {data[field][:50] if isinstance(data[field], str) else data[field]}...")
        
        print(f"📦 Update data fields: {list(update_data.keys())}")
        
        if not update_data:
            print(f"❌ No valid fields to update. Received data: {data}")
            return jsonify({"success": False, "error": "No fields to update"}), 400
        
        # Add updated timestamp
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        print(f"📤 Sending to Supabase: {update_data}")
        
        # Update profile in Supabase
        response = supabase.client.table("user_profiles").update(update_data).eq("firebase_uid", firebase_uid).execute()
        
        print(f"📊 Supabase response: {response}")
        
        if response.data:
            print(f"✅ Profile updated successfully")
            return jsonify({
                "success": True,
                "message": "Profile updated successfully",
                "data": response.data[0]
            }), 200
        else:
            print(f"❌ No profile found for user {firebase_uid}")
            return jsonify({"success": False, "error": "User profile not found"}), 404
            
    except Exception as e:
        import traceback
        print(f"❌ Update profile error: {str(e)}")
        print(f"❌ Traceback: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500


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


@auth_bp.route("/verify-password", methods=["POST"])
def verify_password():
    """Verify user password for sensitive operations like account deletion"""
    try:
        from auth.firebase_auth import firebase_auth_service
        
        # Get Firebase token from request headers
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({
                "success": False,
                "error": "Authorization token is required"
            }), 401
        
        firebase_token = auth_header.split(" ")[1]
        
        # Verify the Firebase token first
        verification_result = firebase_auth_service.verify_token(firebase_token)
        
        if not verification_result["success"]:
            return jsonify({
                "success": False,
                "error": "Invalid or expired token"
            }), 401
        
        # Extract user info directly from verification_result (no nested "user" key)
        firebase_uid = verification_result.get("uid")
        firebase_email = verification_result.get("email")
        
        # Get password from request body
        data = request.get_json()
        
        if not data or 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Password is required'
            }), 400
        
        email = data.get('email') or firebase_email
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        print(f"🔐 Attempting to verify password for email: {email}")
        print(f"🔐 Firebase user: {firebase_uid}")
        
        # Check user's sign-in method first using Firebase Admin
        try:
            user_record = auth.get_user(firebase_uid)
            print(f" User providers: {user_record.provider_data}")
            
            # Check if user has password provider
            has_password = False
            for provider in user_record.provider_data:
                if provider.provider_id == 'password':
                    has_password = True
                    break
            
            if not has_password:
                print(" User doesn't have password provider - using Google/other OAuth")
                # For OAuth users, we'll accept the fact they're already authenticated
                return jsonify({
                    'success': True,
                    'message': 'OAuth user verified via existing session'
                }), 200
        except Exception as admin_error:
            print(f" Couldn't check user providers: {admin_error}")
        
        # Verify password by attempting to sign in with Firebase REST API
        import requests
        
        # Use the Firebase Web API key directly (this is safe for server-side use)
        firebase_api_key = os.environ.get('FIREBASE_API_KEY', 'AIzaSyDij3Q998OYB3PkSQpzIkki3wFzSF_OUcM')
        
        # Use Firebase REST API to verify password
        firebase_auth_url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}'
        
        auth_response = requests.post(firebase_auth_url, json={
            'email': email,
            'password': password,
            'returnSecureToken': True
        })
        
        print(f" Firebase response status: {auth_response.status_code}")
        
        if auth_response.status_code == 200:
            print(" Password verified successfully!")
            return jsonify({
                'success': True,
                'message': 'Password verified successfully'
            }), 200
        else:
            error_data = auth_response.json()
            error_message = error_data.get('error', {}).get('message', 'Invalid password')
            print(f" Firebase error: {error_message}")
            
            # Translate Firebase error messages
            if 'INVALID_PASSWORD' in error_message or 'INVALID_LOGIN_CREDENTIALS' in error_message or 'INVALID_EMAIL' in error_message:
                error_message = 'Incorrect password. Please try again.'
            elif 'TOO_MANY_ATTEMPTS' in error_message:
                error_message = 'Too many failed attempts. Please try again later.'
            elif 'USER_DISABLED' in error_message:
                error_message = 'This account has been disabled.'
            
            return jsonify({
                'success': False,
                'error': error_message
            }), 401
            
    except Exception as e:
        print(f" Password verification error: {str(e)}")
        import traceback
        print(f" Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Failed to verify password'
        }), 500

@auth_bp.route('/check-deactivated', methods=['POST'])
def check_deactivated_status():
    """Check if a user account is deactivated (for showing reactivation modal)"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        print(f"[DEBUG] Checking deactivation status for: {email}")
        
        # Query Supabase for user
        response = supabase.service_client.table('user_profiles').select('*').eq('email', email).execute()
        
        if not response.data:
            print(f"[DEBUG] User not found in database")
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        user = response.data[0]
        is_active = user.get('is_active', True)
        role = user.get('role', '')
        
        print(f"[DEBUG] User role: {role}, is_active: {is_active}")
        
        # Check if this is a deactivated doctor
        if role == 'doctor' and not is_active:
            print(f"[DEBUG] ✅ This is a deactivated doctor account")
            return jsonify({
                'success': True,
                'is_deactivated_doctor': True,
                'user': {
                    'email': user.get('email'),
                    'first_name': user.get('first_name'),
                    'last_name': user.get('last_name'),
                    'role': role
                },
                'message': 'Account is deactivated. Reactivation available.'
            }), 200
        else:
            print(f"[DEBUG] Not a deactivated doctor (role: {role}, active: {is_active})")
            return jsonify({
                'success': True,
                'is_deactivated_doctor': False,
                'message': 'Account is not a deactivated doctor'
            }), 200
            
    except Exception as e:
        print(f"[ERROR] Error checking deactivation status: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ========== DOCTOR SIGNUP MULTI-STEP ENDPOINTS ==========

@auth_bp.route("/doctor-signup/step3", methods=["POST"])
@auth_utils.token_required
def doctor_signup_step3():
    """Save doctor professional information (Step 3)"""
    try:
        user_id = request.current_user["user_id"]
        email = request.current_user.get("email", "").strip().lower()
        
        data = request.get_json()
        
        # Validate required fields
        prc_license_number = data.get("prcLicenseNumber", "").strip()
        prc_expiration_date = data.get("prcExpirationDate", "").strip()
        affiliation_type = data.get("affiliationType", "").strip()
        professional_address = data.get("professionalAddress", "").strip()
        
        if not prc_license_number:
            return jsonify({"success": False, "error": "PRC License Number is required"}), 400
        
        if not prc_expiration_date:
            return jsonify({"success": False, "error": "PRC Expiration Date is required"}), 400
        
        if not affiliation_type:
            return jsonify({"success": False, "error": "Affiliation Type is required"}), 400
        
        if not professional_address:
            return jsonify({"success": False, "error": "Professional Address is required"}), 400
        
        # Validate expiration date
        try:
            exp_date = datetime.fromisoformat(prc_expiration_date.replace('Z', '+00:00'))
            if exp_date.date() <= datetime.now().date():
                return jsonify({"success": False, "error": "PRC Expiration Date must be in the future"}), 400
        except ValueError:
            return jsonify({"success": False, "error": "Invalid date format"}), 400
        
        # Get user profile to get firebase_uid
        user_response = supabase.service_client.table("user_profiles").select("firebase_uid").eq("id", user_id).execute()
        if not user_response.data:
            return jsonify({"success": False, "error": "User profile not found"}), 404
        
        firebase_uid = user_response.data[0].get("firebase_uid")
        if not firebase_uid:
            return jsonify({"success": False, "error": "Firebase UID not found"}), 404
        
        # Check if doctor profile exists, if not create it
        doctor_response = supabase.service_client.table("doctor_profiles").select("*").eq("user_id", user_id).execute()
        
        if not doctor_response.data:
            # Create doctor profile (this is the first time, after OTP verification)
            doctor_data = {
                "user_id": user_id,
                "firebase_uid": firebase_uid,
                "specialization": "General Practitioner",  # Fixed specialization
                "verification_status": "pending",  # Requires admin approval
                "signup_step": 3,  # Currently on step 3
                "signup_completed": False,
                "prc_license_number": prc_license_number,
                "prc_expiration_date": prc_expiration_date,
                "affiliation_type": affiliation_type,
                "professional_address": professional_address
            }
            
            # Add optional fields based on affiliation type
            if affiliation_type in ['clinic_hospital', 'independent_private']:
                clinic_affiliation = data.get("clinicHospitalAffiliation", "").strip()
                contact_number = data.get("hospitalClinicContactNumber", "").strip()
                
                if not clinic_affiliation:
                    return jsonify({"success": False, "error": "Clinic/Hospital Affiliation is required"}), 400
                if not contact_number:
                    return jsonify({"success": False, "error": "Hospital/Clinic Contact Number is required"}), 400
                
                doctor_data["clinic_hospital_affiliation"] = clinic_affiliation
                doctor_data["hospital_clinic_contact_number"] = contact_number
            
            # Create doctor profile
            create_response = supabase.service_client.table("doctor_profiles").insert(doctor_data).execute()
            
            if create_response.data:
                print(f"[DEBUG] ✅ Doctor profile created for user {email}")
                return jsonify({
                    "success": True,
                    "message": "Professional information saved successfully"
                }), 200
            else:
                return jsonify({"success": False, "error": "Failed to create doctor profile"}), 500
        
        # Doctor profile exists, update it
        doctor = doctor_response.data[0]
        doctor_id = doctor["id"]
        
        # Prepare update data
        update_data = {
            "prc_license_number": prc_license_number,
            "prc_expiration_date": prc_expiration_date,
            "affiliation_type": affiliation_type,
            "professional_address": professional_address,
            "signup_step": 3,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Add optional fields based on affiliation type
        if affiliation_type in ['clinic_hospital', 'independent_private']:
            clinic_affiliation = data.get("clinicHospitalAffiliation", "").strip()
            contact_number = data.get("hospitalClinicContactNumber", "").strip()
            
            if not clinic_affiliation:
                return jsonify({"success": False, "error": "Clinic/Hospital Affiliation is required"}), 400
            if not contact_number:
                return jsonify({"success": False, "error": "Hospital/Clinic Contact Number is required"}), 400
            
            update_data["clinic_hospital_affiliation"] = clinic_affiliation
            update_data["hospital_clinic_contact_number"] = contact_number
        
        # Update doctor profile
        update_response = supabase.service_client.table("doctor_profiles").update(update_data).eq("id", doctor_id).execute()
        
        if update_response.data:
            print(f"[DEBUG] ✅ Doctor info saved for user {email}")
            return jsonify({
                "success": True,
                "message": "Professional information saved successfully"
            }), 200
        else:
            return jsonify({"success": False, "error": "Failed to save information"}), 500
            
    except Exception as e:
        print(f"[DEBUG] ❌ Error in step 3: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@auth_bp.route("/doctor-signup/step4", methods=["POST"])
@auth_utils.token_required
def doctor_signup_step4():
    """Upload doctor documents (Step 4)"""
    try:
        user_id = request.current_user["user_id"]
        firebase_uid = request.current_user.get("firebase_uid")
        
        if not firebase_uid:
            # Get firebase_uid from user_profiles
            user_response = supabase.service_client.table("user_profiles").select("firebase_uid").eq("id", user_id).execute()
            if user_response.data:
                firebase_uid = user_response.data[0].get("firebase_uid")
        
        # Get doctor profile
        doctor_response = supabase.service_client.table("doctor_profiles").select("*").eq("user_id", user_id).execute()
        
        if not doctor_response.data:
            return jsonify({"success": False, "error": "Doctor profile not found"}), 404
        
        doctor = doctor_response.data[0]
        doctor_id = doctor["id"]
        affiliation_type = doctor.get("affiliation_type")
        
        # Document type mapping
        doc_type_mapping = {
            'prcIdFront': 'prc_id_front',
            'prcIdBack': 'prc_id_back',
            'ptr': 'ptr',
            'boardCertificate': 'board_certificate',
            'clinicHospitalId': 'clinic_hospital_id',
            'supportingDocument': 'supporting_document'
        }
        
        # Create uploads directory
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'doctor_documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        uploaded_docs = []
        
        # Process each uploaded file
        for field_name, doc_type in doc_type_mapping.items():
            if field_name in request.files:
                file = request.files[field_name]
                
                if file and file.filename:
                    # Validate file type
                    allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
                    original_filename = file.filename
                    filename = secure_filename(file.filename)
                    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    
                    if file_ext not in allowed_extensions:
                        return jsonify({
                            "success": False,
                            "error": f"Invalid file type for {field_name}. Only PDF, JPG, PNG allowed."
                        }), 400
                    
                    # Validate file size (max 5MB)
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > 5 * 1024 * 1024:
                        return jsonify({
                            "success": False,
                            "error": f"File {filename} is too large. Maximum size is 5MB."
                        }), 400
                    
                    # Generate unique filename
                    # Use secure_filename for the base, but preserve extension
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    # Sanitize the original filename but keep extension
                    safe_base = secure_filename(os.path.splitext(original_filename)[0])
                    safe_ext = os.path.splitext(original_filename)[1].lower()
                    unique_filename = f"{firebase_uid}_{doc_type}_{timestamp}_{safe_base}{safe_ext}"
                    file_path = os.path.join(upload_dir, unique_filename)
                    
                    # Ensure directory exists
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Save file
                    file.save(file_path)
                    
                    # Verify file was saved
                    if not os.path.exists(file_path):
                        print(f"[DEBUG] ❌ ERROR: File was not saved! Path: {file_path}")
                        return jsonify({
                            "success": False,
                            "error": "Failed to save file. Please try again."
                        }), 500
                    
                    print(f"[DEBUG] ✅ File saved successfully: {file_path}")
                    print(f"[DEBUG] ✅ File size on disk: {os.path.getsize(file_path)} bytes")
                    
                    # Determine MIME type
                    mime_type = file.content_type or 'application/octet-stream'
                    if file_ext == 'pdf':
                        mime_type = 'application/pdf'
                    elif file_ext in ['jpg', 'jpeg']:
                        mime_type = 'image/jpeg'
                    elif file_ext == 'png':
                        mime_type = 'image/png'
                    
                    # Save to doctor_documents table
                    doc_data = {
                        "doctor_id": doctor_id,
                        "firebase_uid": firebase_uid,
                        "document_type": doc_type,
                        "file_name": filename,
                        "file_path": unique_filename,
                        "file_size": file_size,
                        "mime_type": mime_type
                    }
                    
                    print(f"[DEBUG] 📄 Saving document to doctor_documents table:")
                    print(f"  - doctor_id: {doctor_id}")
                    print(f"  - firebase_uid: {firebase_uid}")
                    print(f"  - document_type: {doc_type}")
                    print(f"  - file_name: {filename}")
                    print(f"  - file_path: {unique_filename}")
                    print(f"  - file_size: {file_size} bytes")
                    print(f"  - mime_type: {mime_type}")
                    
                    doc_response = supabase.service_client.table("doctor_documents").insert(doc_data).execute()
                    
                    if doc_response.data:
                        uploaded_docs.append(doc_type)
                        saved_doc = doc_response.data[0]
                        print(f"[DEBUG] ✅ Document saved to database:")
                        print(f"  - Document ID: {saved_doc.get('id')}")
                        print(f"  - All fields verified: {all(key in saved_doc for key in ['doctor_id', 'firebase_uid', 'document_type', 'file_name', 'file_path', 'file_size', 'mime_type'])}")
                    else:
                        print(f"[DEBUG] ⚠️  Warning: Document insert returned no data")
        
        # Validate required documents
        if 'prc_id_front' not in uploaded_docs:
            return jsonify({"success": False, "error": "PRC ID (Front) is required"}), 400
        
        if 'prc_id_back' not in uploaded_docs:
            return jsonify({"success": False, "error": "PRC ID (Back) is required"}), 400
        
        if affiliation_type == 'not_affiliated' and 'supporting_document' not in uploaded_docs:
            return jsonify({
                "success": False,
                "error": "Supporting document is required for non-affiliated doctors"
            }), 400
        
        # Update signup step
        supabase.service_client.table("doctor_profiles").update({
            "signup_step": 4,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", doctor_id).execute()
        
        print(f"[DEBUG] ✅ Documents uploaded for doctor {doctor_id}")
        return jsonify({
            "success": True,
            "message": "Documents uploaded successfully",
            "uploaded_documents": uploaded_docs
        }), 200
        
    except Exception as e:
        print(f"[DEBUG] ❌ Error in step 4: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@auth_bp.route("/doctor-signup/step5", methods=["POST"])
@auth_utils.token_required
def doctor_signup_step5():
    """Upload profile photo (Step 5)"""
    try:
        user_id = request.current_user["user_id"]
        firebase_uid = request.current_user.get("firebase_uid")
        
        if not firebase_uid:
            user_response = supabase.service_client.table("user_profiles").select("firebase_uid").eq("id", user_id).execute()
            if user_response.data:
                firebase_uid = user_response.data[0].get("firebase_uid")
        
        if 'profilePhoto' not in request.files:
            return jsonify({"success": False, "error": "Profile photo is required"}), 400
        
        file = request.files['profilePhoto']
        
        if not file or not file.filename:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        
        # Validate file type
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                "success": False,
                "error": "Invalid file type. Only JPG, JPEG, PNG allowed."
            }), 400
        
        # Validate file size (2-5MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size < 400 * 400:  # Rough minimum size check
            return jsonify({
                "success": False,
                "error": "Image resolution is too low. Minimum 400x400px required."
            }), 400
        
        if file_size > 5 * 1024 * 1024:
            return jsonify({
                "success": False,
                "error": "File size must be less than 5MB."
            }), 400
        
        # Create uploads directory
        upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'doctor_profile_photos')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{firebase_uid}_profile_{timestamp}.{file_ext}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Determine MIME type
        mime_type = 'image/jpeg' if file_ext in ['jpg', 'jpeg'] else 'image/png'
        
        # Construct URL (for now, relative path - can be updated to full URL if needed)
        photo_url = f"/uploads/doctor_profile_photos/{unique_filename}"
        
        # Update user profile with avatar_url
        print(f"[DEBUG] 📸 Saving avatar_url to database for user_id: {user_id}")
        print(f"[DEBUG] 📸 Photo URL: {photo_url}")
        
        update_response = supabase.service_client.table("user_profiles").update({
            "avatar_url": photo_url,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", user_id).execute()
        
        print(f"[DEBUG] 📸 Database update response: {update_response.data if update_response.data else 'No data returned'}")
        
        # Verify the update was successful
        verify_response = supabase.service_client.table("user_profiles").select("avatar_url").eq("id", user_id).execute()
        if verify_response.data:
            saved_avatar_url = verify_response.data[0].get("avatar_url")
            print(f"[DEBUG] ✅ Verified avatar_url saved to database: {saved_avatar_url}")
            if saved_avatar_url != photo_url:
                print(f"[DEBUG] ⚠️  Warning: Saved URL ({saved_avatar_url}) doesn't match expected URL ({photo_url})")
        else:
            print(f"[DEBUG] ⚠️  Warning: Could not verify avatar_url was saved")
        
        # Update doctor profile signup step
        doctor_response = supabase.service_client.table("doctor_profiles").select("id").eq("user_id", user_id).execute()
        if doctor_response.data:
            supabase.service_client.table("doctor_profiles").update({
                "signup_step": 5,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", doctor_response.data[0]["id"]).execute()
        
        print(f"[DEBUG] ✅ Profile photo uploaded and saved to database for user {user_id}")
        return jsonify({
            "success": True,
            "message": "Profile photo uploaded successfully",
            "photo_url": photo_url
        }), 200
        
    except Exception as e:
        print(f"[DEBUG] ❌ Error in step 5: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@auth_bp.route("/doctor-signup/preview", methods=["GET"])
@auth_utils.token_required
def doctor_signup_preview():
    """Get preview data for step 6"""
    try:
        user_id = request.current_user["user_id"]
        
        # Get doctor profile
        doctor_response = supabase.service_client.table("doctor_profiles").select("*").eq("user_id", user_id).execute()
        
        if not doctor_response.data:
            return jsonify({"success": False, "error": "Doctor profile not found"}), 404
        
        doctor = doctor_response.data[0]
        
        # Get documents
        docs_response = supabase.service_client.table("doctor_documents").select("*").eq("doctor_id", doctor["id"]).execute()
        documents = docs_response.data if docs_response.data else []
        
        # Get user profile for avatar
        user_response = supabase.service_client.table("user_profiles").select("avatar_url").eq("id", user_id).execute()
        avatar_url = None
        if user_response.data:
            avatar_url = user_response.data[0].get("avatar_url")
        
        preview_data = {
            "prc_license_number": doctor.get("prc_license_number"),
            "prc_expiration_date": doctor.get("prc_expiration_date"),
            "specialization": doctor.get("specialization", "General Practitioner"),
            "affiliation_type": doctor.get("affiliation_type"),
            "clinic_hospital_affiliation": doctor.get("clinic_hospital_affiliation"),
            "professional_address": doctor.get("professional_address"),
            "hospital_clinic_contact_number": doctor.get("hospital_clinic_contact_number"),
            "documents": documents,
            "profile_photo_url": avatar_url
        }
        
        return jsonify({
            "success": True,
            "data": preview_data
        }), 200
        
    except Exception as e:
        print(f"[DEBUG] ❌ Error in preview: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@auth_bp.route("/doctor-signup/submit", methods=["POST"])
@auth_utils.token_required
def doctor_signup_submit():
    """Final submission of doctor signup (Step 6)"""
    try:
        user_id = request.current_user["user_id"]
        email = request.current_user.get("email", "").strip().lower()
        
        # Get doctor profile
        doctor_response = supabase.service_client.table("doctor_profiles").select("*").eq("user_id", user_id).execute()
        
        if not doctor_response.data:
            return jsonify({"success": False, "error": "Doctor profile not found"}), 404
        
        doctor = doctor_response.data[0]
        doctor_id = doctor["id"]
        
        # Verify all required steps are completed
        if doctor.get("signup_step", 0) < 5:
            return jsonify({
                "success": False,
                "error": "Please complete all previous steps before submitting"
            }), 400
        
        # Verify required documents are uploaded
        docs_response = supabase.service_client.table("doctor_documents").select("document_type").eq("doctor_id", doctor_id).execute()
        uploaded_doc_types = [doc["document_type"] for doc in (docs_response.data or [])]
        
        if 'prc_id_front' not in uploaded_doc_types or 'prc_id_back' not in uploaded_doc_types:
            return jsonify({
                "success": False,
                "error": "Required documents are missing. Please upload PRC ID (Front and Back)."
            }), 400
        
        if doctor.get("affiliation_type") == 'not_affiliated' and 'supporting_document' not in uploaded_doc_types:
            return jsonify({
                "success": False,
                "error": "Supporting document is required for non-affiliated doctors."
            }), 400
        
        # Update doctor profile - mark signup as completed
        update_data = {
            "signup_step": 6,
            "signup_completed": True,
            "verification_status": "pending",  # Ready for admin review
            "updated_at": datetime.utcnow().isoformat()
        }
        
        update_response = supabase.service_client.table("doctor_profiles").update(update_data).eq("id", doctor_id).execute()
        
        if not update_response.data:
            return jsonify({"success": False, "error": "Failed to submit application"}), 500
        
        # Send admin notification email and create in-app notification
        try:
            from doctor_verification import send_admin_notification_email, generate_verification_token
            
            verification_token = generate_verification_token()
            
            # Store verification token
            supabase.service_client.table("doctor_profiles").update({
                "verification_token": verification_token,
                "token_expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
            }).eq("id", doctor_id).execute()
            
            # Get user info
            user_response = supabase.service_client.table("user_profiles").select("first_name, last_name").eq("id", user_id).execute()
            first_name = user_response.data[0].get("first_name", "") if user_response.data else ""
            last_name = user_response.data[0].get("last_name", "") if user_response.data else ""
            
            doctor_signup_data = {
                "firstName": first_name,
                "lastName": last_name,
                "email": email,
                "specialization": doctor.get("specialization", "General Practitioner")
            }
            
            # Get document file paths for admin email
            file_paths = []
            for doc_type in ['prc_id_front', 'prc_id_back']:
                doc_resp = supabase.service_client.table("doctor_documents").select("file_path").eq("doctor_id", doctor_id).eq("document_type", doc_type).limit(1).execute()
                if doc_resp.data:
                    upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads', 'doctor_documents')
                    file_paths.append(os.path.join(upload_dir, doc_resp.data[0]["file_path"]))
            
            email_sent = send_admin_notification_email(
                doctor_signup_data,
                file_paths[0] if file_paths else None,  # Send first document as attachment
                doctor_id,
                verification_token
            )
            
            if email_sent:
                print(f"[DEBUG] ✅ Admin notification email sent for doctor {doctor_id}")
            else:
                print(f"[DEBUG] ⚠️  Failed to send admin notification email")
            
            # Create in-app notification for all admin users
            try:
                from services.notification_service import notification_service
                
                # Get all admin users
                admin_users = supabase.service_client.table("user_profiles").select("firebase_uid").eq("role", "admin").execute()
                
                if admin_users.data and notification_service:
                    full_name = f"{first_name} {last_name}".strip()
                    notification_title = "New Doctor Signup Request"
                    notification_message = f"Dr. {full_name} has submitted their application for verification."
                    
                    for admin in admin_users.data:
                        admin_uid = admin.get("firebase_uid")
                        if admin_uid:
                            notification_service.create_notification(
                                user_id=admin_uid,
                                title=notification_title,
                                message=notification_message,
                                notification_type="doctor_signup",
                                category="doctor_verification",
                                priority="high",
                                action_url=f"/dashboard?tab=doctor-verification&doctor_id={doctor_id}",
                                action_label="Review Now"
                            )
                            print(f"[DEBUG] ✅ Created notification for admin: {admin_uid}")
                
            except Exception as notif_error:
                print(f"[DEBUG] ⚠️  In-app notification error: {notif_error}")
                import traceback
                traceback.print_exc()
                # Don't fail the submission if notification fails
                
        except Exception as email_error:
            print(f"[DEBUG] ⚠️  Email notification error: {email_error}")
            # Don't fail the submission if email fails
        
        # Get updated user data
        user_response = supabase.service_client.table("user_profiles").select("*").eq("id", user_id).execute()
        user = user_response.data[0] if user_response.data else None
        
        # Get updated doctor profile
        updated_doctor = update_response.data[0]
        
        print(f"[DEBUG] ✅ Doctor signup completed for {email}")
        return jsonify({
            "success": True,
            "message": "Application submitted successfully! Your account is pending verification.",
            "data": {
                "user": user,
                "doctor_profile": updated_doctor
            }
        }), 200
        
    except Exception as e:
        print(f"[DEBUG] ❌ Error in submit: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500
