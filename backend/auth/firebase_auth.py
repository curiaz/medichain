"""
Firebase Authentication Service for Backend
Handles Firebase Admin SDK operations and token verification
"""

import os
from functools import wraps

import firebase_admin
from dotenv import load_dotenv
from firebase_admin import auth, credentials
from flask import jsonify, request

# Load environment variables
load_dotenv()


class FirebaseAuthService:
    """Firebase Authentication service for backend operations"""

    def __init__(self):
        self.app = None
        self.initialize_firebase()

    def initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if Firebase is already initialized
            if not firebase_admin._apps:
                # Try to load from service account key file
                service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY")

                if service_account_path and os.path.exists(service_account_path):
                    # Initialize with service account key file
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                    print("OK Firebase Admin initialized with service account key")
                else:
                    # Try to initialize with environment variables
                    service_account_info = {
                        "type": "service_account",
                        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                        "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
                        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL"),
                    }

                    # Check if all required fields are present
                    if all(service_account_info.values()):
                        cred = credentials.Certificate(service_account_info)
                        firebase_admin.initialize_app(cred)
                        print("OK Firebase Admin initialized with environment variables")
                    else:
                        print("WARNING Firebase Admin not initialized - missing credentials")
                        return False
            else:
                print("OK Firebase Admin already initialized")
            
            return True

        except Exception as e:
            print(f"ERROR Error initializing Firebase Admin: {e}")
            return False

    def verify_token(self, id_token):
        """Verify Firebase ID token and return user info"""
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            return {
                "success": True,
                "uid": decoded_token["uid"],
                "email": decoded_token.get("email"),
                "email_verified": decoded_token.get("email_verified", False),
                "name": decoded_token.get("name"),
                "picture": decoded_token.get("picture"),
                "token_data": decoded_token,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_user_by_uid(self, uid):
        """Get user information by UID"""
        try:
            user_record = auth.get_user(uid)
            return {
                "success": True,
                "user": {
                    "uid": user_record.uid,
                    "email": user_record.email,
                    "email_verified": user_record.email_verified,
                    "display_name": user_record.display_name,
                    "photo_url": user_record.photo_url,
                    "disabled": user_record.disabled,
                    "creation_time": user_record.user_metadata.creation_timestamp,
                    "last_sign_in": user_record.user_metadata.last_sign_in_timestamp,
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_custom_token(self, uid, additional_claims=None):
        """Create a custom token for a user"""
        try:
            custom_token = auth.create_custom_token(uid, additional_claims)
            return {"success": True, "token": custom_token.decode("utf-8")}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def update_user(self, uid, **kwargs):
        """Update user information"""
        try:
            auth.update_user(uid, **kwargs)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete_user(self, uid):
        """Delete a user"""
        try:
            auth.delete_user(uid)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def sign_in_with_email_password(self, email, password):
        """Sign in user with email and password (Note: This is for server-side only, client should use Firebase SDK)"""
        try:
            # Note: Firebase Admin SDK doesn't support sign in with email/password
            # This is typically done on the client side with Firebase Auth SDK
            # For server-side authentication, we recommend using custom tokens or other methods
            # For now, we'll return an error indicating this should be done client-side
            return {
                "success": False,
                "error": "Email/password sign in should be done client-side with Firebase SDK",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_user_with_email_password(self, email, password):
        """Create a new user with email and password"""
        try:
            user = auth.create_user(email=email, password=password)

            # Generate a custom token for the user
            custom_token = self.create_custom_token(user.uid)

            return {
                "success": True,
                "user": {
                    "uid": user.uid,
                    "email": user.email,
                    "email_verified": user.email_verified,
                },
                "token": custom_token["token"],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def send_password_reset_email(self, email):
        """Send password reset email via Firebase with actual email delivery and verification code"""
        try:
            # Import OTP service
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            
            try:
                from services.simple_otp_manager import simple_otp_manager as otp_service
                print("✅ Using Simple OTP Manager")
            except ImportError:
                try:
                    from services.otp_service import otp_service
                    print("✅ Using Database OTP Service")
                except ImportError as e:
                    print(f"Warning: Could not import any OTP service: {e}")
                    # Fallback to simple random code generation
                    import random
                    verification_code = str(random.randint(100000, 999999))
                    
                    # Send email with simple code
                    email_sent = self._send_reset_link_email(email, link, verification_code)
                    
                    if email_sent:
                        return {
                            "success": True,
                            "message": "Password reset email sent successfully",
                            "verification_code": verification_code,
                            "expires_in": "5 minutes"
                        }
                    else:
                        print(f"🔐 FIREBASE RESET LINK for {email}:")
                        print(f"🔗 {link}")
                        print(f"🔢 VERIFICATION CODE: {verification_code} (basic fallback)")
                        return {
                            "success": True,
                            "message": "Password reset link and code generated (check console for development)",
                            "dev_link": link,
                            "verification_code": verification_code,
                            "expires_in": "5 minutes"
                        }
            
            # Generate password reset link with proper configuration
            try:
                # Configure the action code settings for better link handling
                action_code_settings = auth.ActionCodeSettings(
                    url='http://localhost:3000/login',  # Redirect after password reset
                    handle_code_in_app=False  # Handle in web browser
                )
                link = auth.generate_password_reset_link(email, action_code_settings)
                print(f"✅ Generated Firebase reset link for {email}")
            except Exception as link_error:
                print(f"⚠️  Firebase link generation failed: {link_error}")
                # Create a fallback link
                link = f"http://localhost:3000/reset-password?email={email}"
            
            # Store OTP in database with 5-minute expiration
            otp_result = otp_service.store_otp(email, link)
            
            if not otp_result["success"]:
                return {
                    "success": False,
                    "error": "Failed to generate verification code"
                }
            
            verification_code = otp_result["otp_code"]
            
            # Send the reset link and verification code via email
            email_sent = self._send_reset_link_email(email, link, verification_code)
            
            if email_sent:
                return {
                    "success": True,
                    "message": "Password reset email sent successfully",
                    "verification_code": verification_code,  # Return code for backend verification
                    "expires_in": "5 minutes"
                }
            else:
                # For development, return both link and code in console
                print(f"🔐 FIREBASE RESET LINK for {email}:")
                print(f"🔗 {link}")
                print(f"🔢 VERIFICATION CODE: {verification_code} (expires in 5 minutes)")
                return {
                    "success": True,
                    "message": "Password reset link and code generated (check console for development)",
                    "dev_link": link,  # For development only
                    "verification_code": verification_code,
                    "expires_in": "5 minutes"
                }
                
        except auth.UserNotFoundError:
            return {
                "success": False,
                "error": "No user found with this email address"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to send password reset email: {str(e)}"
            }
    
    def _send_reset_link_email(self, email, reset_link, verification_code=None):
        """Send reset link and verification code via email service"""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            import os
            
            # Email configuration
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = os.getenv("GMAIL_USER")
            sender_password = os.getenv("GMAIL_APP_PASSWORD")
            
            if not sender_email or not sender_password:
                print("📧 Email credentials not configured - showing link in console")
                return False
            
            # Create email
            msg = MIMEMultipart("alternative")
            msg["From"] = f"Medichain Security <{sender_email}>"
            msg["To"] = email
            msg["Subject"] = "🔐 Reset Your Medichain Password"
            
            # HTML email content
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background: linear-gradient(135deg, #2196f3 0%, #1976d2 100%); padding: 30px; text-align: center; color: white; border-radius: 10px;">
                    <h1>🏥 MediChain Password Reset</h1>
                </div>
                
                <div style="padding: 30px; background: #f8f9fa; border-radius: 10px; margin: 20px 0;">
                    <h2>Reset Your Password</h2>
                    <p>We received a request to reset your MediChain account password. You have two options:</p>
                    
                    <div style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0; color: #856404;">📋 Option 1: Use Verification Code</h3>
                        <p style="margin: 0;">Enter this code in the app: <strong style="font-size: 24px; color: #2196f3; letter-spacing: 2px;">{verification_code or "N/A"}</strong></p>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <h3 style="color: #495057;">🔗 Option 2: Use Reset Link</h3>
                        <a href="{reset_link}" style="background: #2196f3; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                            🔐 Reset Password
                        </a>
                    </div>
                    
                    <p><strong>⏰ Both the code and link will expire in 1 hour.</strong></p>
                    
                    <p>If you didn't request this password reset, please ignore this email.</p>
                    
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
                    <p style="font-size: 12px; color: #666;">
                        If the button doesn't work, copy and paste this link:<br>
                        <a href="{reset_link}">{reset_link}</a>
                    </p>
                </div>
                
                <div style="text-align: center; color: #666; font-size: 12px;">
                    <p>© 2025 MediChain - AI-Driven Diagnosis & Blockchain Health Records</p>
                </div>
            </body>
            </html>
            """
            
            # Attach HTML content
            msg.attach(MIMEText(html_body, "html"))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                
            print(f"✅ Password reset email sent to {email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False


# Global instance
firebase_auth_service = FirebaseAuthService()


def firebase_auth_required(f):
    """Decorator to require Firebase authentication"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "No authorization header provided"}), 401

        # Extract the token
        try:
            token = auth_header.split(" ")[1]  # Remove 'Bearer ' prefix
        except IndexError:
            return jsonify({"error": "Invalid authorization header format"}), 401

        # Verify the token
        verification_result = firebase_auth_service.verify_token(token)

        if not verification_result["success"]:
            return (
                jsonify({"error": "Invalid token", "details": verification_result["error"]}),
                401,
            )

        # Add user info to request context
        request.firebase_user = verification_result

        return f(*args, **kwargs)

    return decorated_function


def firebase_role_required(allowed_roles):
    """Decorator to require specific user roles"""

    def decorator(f):
        @wraps(f)
        @firebase_auth_required
        def decorated_function(*args, **kwargs):
            from db.supabase_client import SupabaseClient

            # Get user profile from Supabase to check role
            supabase = SupabaseClient()
            user_uid = request.firebase_user["uid"]

            try:
                # Get user profile from Supabase
                response = (
                    supabase.service_client.table("user_profiles")
                    .select("role")
                    .eq("firebase_uid", user_uid)
                    .single()
                    .execute()
                )

                if not response.data:
                    return jsonify({"error": "User profile not found"}), 404

                user_role = response.data["role"]

                if user_role not in allowed_roles:
                    return (
                        jsonify({"error": f"Access denied. Required roles: {allowed_roles}"}),
                        403,
                    )

                # Add role to request context
                request.user_role = user_role

                return f(*args, **kwargs)

            except Exception as e:
                return jsonify({"error": f"Error checking user role: {str(e)}"}), 500

        return decorated_function

    return decorator


# Helper function to get current user from request context
def get_current_user():
    """Get current Firebase user from request context"""
    return getattr(request, "firebase_user", None)


def get_current_user_role():
    """Get current user role from request context"""
    return getattr(request, "user_role", None)


def get_current_user_uid():
    """Get current user UID from request context"""
    user = get_current_user()
    return user["uid"] if user else None
