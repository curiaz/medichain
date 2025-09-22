"""
Firebase Authentication Service for Backend
Handles Firebase Admin SDK operations and token verification
"""
import os
import json
from functools import wraps
from flask import request, jsonify, current_app
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv

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
                service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')
                
                if service_account_path and os.path.exists(service_account_path):
                    # Initialize with service account key file
                    cred = credentials.Certificate(service_account_path)
                    firebase_admin.initialize_app(cred)
                    print("✅ Firebase Admin initialized with service account key")
                else:
                    # Try to initialize with environment variables
                    service_account_info = {
                        "type": "service_account",
                        "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                        "private_key": os.getenv('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
                        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
                    }
                    
                    # Check if all required fields are present
                    if all(service_account_info.values()):
                        cred = credentials.Certificate(service_account_info)
                        firebase_admin.initialize_app(cred)
                        print("✅ Firebase Admin initialized with environment variables")
                    else:
                        print("⚠️ Firebase Admin not initialized - missing credentials")
                        return False
            else:
                print("✅ Firebase Admin already initialized")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing Firebase Admin: {e}")
            return False
    
    def verify_token(self, id_token):
        """Verify Firebase ID token and return user info"""
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            return {
                'success': True,
                'uid': decoded_token['uid'],
                'email': decoded_token.get('email'),
                'email_verified': decoded_token.get('email_verified', False),
                'name': decoded_token.get('name'),
                'picture': decoded_token.get('picture'),
                'token_data': decoded_token
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_user_by_uid(self, uid):
        """Get user information by UID"""
        try:
            user_record = auth.get_user(uid)
            return {
                'success': True,
                'user': {
                    'uid': user_record.uid,
                    'email': user_record.email,
                    'email_verified': user_record.email_verified,
                    'display_name': user_record.display_name,
                    'photo_url': user_record.photo_url,
                    'disabled': user_record.disabled,
                    'creation_time': user_record.user_metadata.creation_timestamp,
                    'last_sign_in': user_record.user_metadata.last_sign_in_timestamp
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_custom_token(self, uid, additional_claims=None):
        """Create a custom token for a user"""
        try:
            custom_token = auth.create_custom_token(uid, additional_claims)
            return {
                'success': True,
                'token': custom_token.decode('utf-8')
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_user(self, uid, **kwargs):
        """Update user information"""
        try:
            auth.update_user(uid, **kwargs)
            return {'success': True}
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_user(self, uid):
        """Delete a user"""
        try:
            auth.delete_user(uid)
            return {'success': True}
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def sign_in_with_email_password(self, email, password):
        """Sign in user with email and password (Note: This is for server-side only, client should use Firebase SDK)"""
        try:
            # Note: Firebase Admin SDK doesn't support sign in with email/password
            # This is typically done on the client side with Firebase Auth SDK
            # For server-side authentication, we recommend using custom tokens or other methods
            # For now, we'll return an error indicating this should be done client-side
            return {
                'success': False,
                'error': 'Email/password sign in should be done client-side with Firebase SDK'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_user_with_email_password(self, email, password):
        """Create a new user with email and password"""
        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            
            # Generate a custom token for the user
            custom_token = self.create_custom_token(user.uid)
            
            return {
                'success': True,
                'user': {
                    'uid': user.uid,
                    'email': user.email,
                    'email_verified': user.email_verified
                },
                'token': custom_token['token']
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Global instance
firebase_auth_service = FirebaseAuthService()

def firebase_auth_required(f):
    """Decorator to require Firebase authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'No authorization header provided'}), 401
        
        # Extract the token
        try:
            token = auth_header.split(' ')[1]  # Remove 'Bearer ' prefix
        except IndexError:
            return jsonify({'error': 'Invalid authorization header format'}), 401
        
        # Verify the token
        verification_result = firebase_auth_service.verify_token(token)
        
        if not verification_result['success']:
            return jsonify({'error': 'Invalid token', 'details': verification_result['error']}), 401
        
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
            user_uid = request.firebase_user['uid']
            
            try:
                # Get user profile from Supabase
                response = supabase.service_client.table('user_profiles').select('role').eq('firebase_uid', user_uid).single().execute()
                
                if not response.data:
                    return jsonify({'error': 'User profile not found'}), 404
                
                user_role = response.data['role']
                
                if user_role not in allowed_roles:
                    return jsonify({'error': f'Access denied. Required roles: {allowed_roles}'}), 403
                
                # Add role to request context
                request.user_role = user_role
                
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': f'Error checking user role: {str(e)}'}), 500
        
        return decorated_function
    return decorator

# Helper function to get current user from request context
def get_current_user():
    """Get current Firebase user from request context"""
    return getattr(request, 'firebase_user', None)

def get_current_user_role():
    """Get current user role from request context"""
    return getattr(request, 'user_role', None)

def get_current_user_uid():
    """Get current user UID from request context"""
    user = get_current_user()
    return user['uid'] if user else None
