"""
Enhanced Authentication Routes with Firebase and Supabase Integration
"""
from flask import Blueprint, request, jsonify
from auth.firebase_auth import firebase_auth_service, firebase_auth_required, firebase_role_required
from db.supabase_client import SupabaseClient
import re

auth_firebase_bp = Blueprint('auth_firebase', __name__, url_prefix='/api/auth')
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

@auth_firebase_bp.route('/verify', methods=['POST'])
@firebase_auth_required
def verify_token():
    """Verify Firebase token and return user info with Supabase profile"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        # Get user profile from Supabase
        response = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
        
        if response.data:
            user_profile = response.data[0]
            
            # If user is a doctor, get doctor profile too
            doctor_profile = None
            if user_profile['role'] == 'doctor':
                doc_response = supabase.service_client.table('doctor_profiles').select('*').eq('firebase_uid', uid).execute()
                if doc_response.data:
                    doctor_profile = doc_response.data[0]
            
            return jsonify({
                'success': True,
                'user': {
                    'uid': uid,
                    'email': firebase_user['email'],
                    'email_verified': firebase_user['email_verified'],
                    'profile': user_profile,
                    'doctor_profile': doctor_profile
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User profile not found in database'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/profile', methods=['GET'])
@firebase_auth_required
def get_profile():
    """Get user profile"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        # Get user profile from Supabase
        response = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
        
        if response.data:
            user_profile = response.data[0]
            return jsonify({
                'success': True,
                'profile': user_profile
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/profile', methods=['PUT'])
@firebase_auth_required
def update_profile():
    """Update user profile"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Remove fields that shouldn't be updated directly
        restricted_fields = ['id', 'firebase_uid', 'created_at', 'updated_at']
        for field in restricted_fields:
            data.pop(field, None)
        
        # Update user profile in Supabase
        response = supabase.service_client.table('user_profiles').update(data).eq('firebase_uid', uid).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'profile': response.data[0]
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update profile'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/create-profile', methods=['POST'])
@firebase_auth_required
def create_profile():
    """Create user profile after Firebase signup"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'role']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        # Validate role
        valid_roles = ['patient', 'doctor', 'admin']
        if data['role'] not in valid_roles:
            return jsonify({'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'}), 400
        
        # Check if profile already exists
        existing = supabase.service_client.table('user_profiles').select('id').eq('firebase_uid', uid).execute()
        if existing.data:
            return jsonify({'error': 'Profile already exists'}), 409
        
        # Create profile data
        profile_data = {
            'firebase_uid': uid,
            'email': firebase_user['email'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'phone': data.get('phone'),
            'role': data['role'],
            'gender': data.get('gender'),
            'date_of_birth': data.get('date_of_birth')
        }
        
        # Insert user profile
        response = supabase.service_client.table('user_profiles').insert(profile_data).execute()
        
        if not response.data:
            return jsonify({'error': 'Failed to create profile'}), 500
        
        created_profile = response.data[0]
        
        # If user is a doctor, create doctor profile
        if data['role'] == 'doctor':
            doctor_data = {
                'firebase_uid': uid,
                'user_id': created_profile['id'],
                'license_number': data.get('license_number', ''),
                'specialization': data.get('specialization', ''),
                'years_of_experience': data.get('years_of_experience', 0),
                'hospital_affiliation': data.get('hospital_affiliation'),
                'consultation_fee': data.get('consultation_fee', 0),
                'bio': data.get('bio')
            }
            
            doc_response = supabase.service_client.table('doctor_profiles').insert(doctor_data).execute()
            
            if doc_response.data:
                created_profile['doctor_profile'] = doc_response.data[0]
        
        return jsonify({
            'success': True,
            'profile': created_profile
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/doctor-profile', methods=['GET'])
@firebase_role_required(['doctor'])
def get_doctor_profile():
    """Get doctor-specific profile"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        response = supabase.service_client.table('doctor_profiles').select('*').eq('firebase_uid', uid).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'doctor_profile': response.data[0]
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Doctor profile not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/doctor-profile', methods=['PUT'])
@firebase_role_required(['doctor'])
def update_doctor_profile():
    """Update doctor-specific profile"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Remove fields that shouldn't be updated directly
        restricted_fields = ['id', 'firebase_uid', 'user_id', 'created_at', 'updated_at']
        for field in restricted_fields:
            data.pop(field, None)
        
        response = supabase.service_client.table('doctor_profiles').update(data).eq('firebase_uid', uid).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'doctor_profile': response.data[0]
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update doctor profile'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/users', methods=['GET'])
@firebase_role_required(['admin'])
def get_all_users():
    """Get all users (admin only)"""
    try:
        response = supabase.service_client.table('user_profiles').select('*').execute()
        
        return jsonify({
            'success': True,
            'users': response.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/doctors', methods=['GET'])
def get_all_doctors():
    """Get all doctors (public endpoint)"""
    try:
        response = supabase.service_client.table('doctor_profiles').select("""
            *,
            user_profile:user_profiles(first_name, last_name, email, phone)
        """).execute()
        
        return jsonify({
            'success': True,
            'doctors': response.data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/user/<user_id>', methods=['DELETE'])
@firebase_role_required(['admin'])
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        # Delete from Supabase (cascading will handle related tables)
        response = supabase.service_client.table('user_profiles').delete().eq('firebase_uid', user_id).execute()
        
        if response.data:
            # Also delete from Firebase
            firebase_result = firebase_auth_service.delete_user(user_id)
            
            return jsonify({
                'success': True,
                'firebase_deletion': firebase_result['success']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/login', methods=['POST'])
def login():
    """Login with Firebase ID token"""
    print("🔍 LOGIN ENDPOINT CALLED")
    try:
        data = request.get_json()
        print(f"📥 Login received data keys: {list(data.keys()) if data else 'None'}")
        
        id_token = data.get('id_token') if data else None
        print(f"🔑 Login ID Token present: {bool(id_token)}")

        if not id_token:
            print("❌ Login: No ID token provided")
            return jsonify({
                'success': False,
                'error': 'ID token is required'
            }), 400

        # Verify the Firebase ID token
        print("🔐 LOGIN: Starting Firebase token verification...")
        result = firebase_auth_service.verify_token(id_token)
        print(f"🔐 LOGIN: Token verification result: {result}")

        if result['success']:
            print("✅ LOGIN: Token verification successful")
            # Extract user information from token result
            uid = result['uid']
            email = result['email']
            email_verified = result.get('email_verified', False)
            print(f"✅ LOGIN: Extracted user info - UID: {uid}, Email: {email}")

            # Get user profile from Supabase
            print(f"🗄️ LOGIN: Fetching user profile for UID: {uid}")
            response = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
            print(f"🗄️ LOGIN: Database response received: {len(response.data) if response.data else 0} records")

            # If no profile found for this UID, check if there's a profile with the same email
            if not response.data:
                print(f"🗄️ LOGIN: No profile found for UID {uid}, checking for existing email: {email}")
                email_response = supabase.service_client.table('user_profiles').select('*').eq('email', email).execute()
                print(f"🗄️ LOGIN: Email search returned {len(email_response.data) if email_response.data else 0} records")

                if email_response.data:
                    existing_profile = email_response.data[0]
                    existing_uid = existing_profile['firebase_uid']
                    print(f"✅ LOGIN: Found existing profile with same email: {existing_uid}")

                    # Update the existing profile with the new Firebase UID
                    print(f"🔄 LOGIN: Updating profile {existing_uid} to new UID {uid}")
                    try:
                        # First update user_profiles with the new UID
                        update_response = supabase.service_client.table('user_profiles').update({
                            'firebase_uid': uid
                        }).eq('email', email).execute()

                        if update_response.data:
                            print("✅ LOGIN: Successfully updated user_profiles with new Firebase UID")
                            
                            # Now update doctor_profiles if it exists
                            doctor_check = supabase.service_client.table('doctor_profiles').select('id').eq('firebase_uid', existing_uid).execute()
                            if doctor_check.data:
                                print(f"🔄 LOGIN: Found doctor profile for {existing_uid}, updating it")
                                doctor_update = supabase.service_client.table('doctor_profiles').update({
                                    'firebase_uid': uid
                                }).eq('firebase_uid', existing_uid).execute()
                                
                                if doctor_update.data:
                                    print("✅ LOGIN: Successfully updated doctor profile with new Firebase UID")
                                else:
                                    print(f"❌ LOGIN: Failed to update doctor profile: {doctor_update}")
                            
                            response = email_response  # Use the existing profile data
                            response.data[0]['firebase_uid'] = uid  # Update the UID in the response
                        else:
                            print(f"❌ LOGIN: Update failed - no data returned: {update_response}")
                            return jsonify({
                                'success': False,
                                'error': 'Failed to update user profile'
                            }), 500
                    except Exception as update_error:
                        print(f"❌ LOGIN: Update error: {str(update_error)}")
                        return jsonify({
                            'success': False,
                            'error': f'Failed to update user profile: {str(update_error)}'
                        }), 500
                else:
                    print(f"❌ LOGIN: No profile found for UID {uid} or email {email}")
                    return jsonify({
                        'success': False,
                        'error': 'User profile not found. Please register first.'
                    }), 404

            if response.data:
                user_profile = response.data[0]
                print(f"🔍 LOGIN: Retrieved user profile: {user_profile}")
                print(f"🔍 LOGIN: User role: {user_profile.get('role', 'NO ROLE FOUND')}")

                # If user is a doctor, get doctor profile too
                doctor_profile = None
                if user_profile['role'] == 'doctor':
                    doc_response = supabase.service_client.table('doctor_profiles').select('*').eq('firebase_uid', uid).execute()
                    if doc_response.data:
                        doctor_profile = doc_response.data[0]

                login_response = {
                    'success': True,
                    'token': id_token,  # Return the same token for consistency
                    'user': {
                        'uid': uid,
                        'email': email,
                        'email_verified': email_verified,
                        'profile': user_profile,
                        'doctor_profile': doctor_profile
                    }
                }
                print(f"🔍 LOGIN: Response data: {login_response}")
                return jsonify(login_response), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'User profile not found. Please complete your registration.'
                }), 404
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 401

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@auth_firebase_bp.route('/register', methods=['POST'])
def register():
    """Register new user with Firebase ID token and create Supabase profile"""
    print("🔍 REGISTER ENDPOINT CALLED")
    try:
        data = request.get_json()
        print(f"📥 Received data keys: {list(data.keys()) if data else 'None'}")
        
        id_token = data.get('id_token') if data else None
        name = data.get('name') if data else None
        role = data.get('role', 'patient') if data else 'patient'

        print(f"🔑 ID Token present: {bool(id_token)}")
        print(f"👤 Name: {name}")
        print(f"🎭 Role: {role}")

        if not id_token or not name:
            print("❌ Missing required fields")
            return jsonify({
                'success': False,
                'error': 'ID token and name are required'
            }), 400

        print("🔐 Verifying Firebase ID token...")
        # Verify the Firebase ID token to get user info
        token_result = firebase_auth_service.verify_token(id_token)
        print(f"🔐 Token verification result: {token_result.get('success', 'No success key')}")
        
        if not token_result['success']:
            print(f"❌ Token verification failed: {token_result.get('error', 'Unknown error')}")
            return jsonify({
                'success': False,
                'error': f'Invalid ID token: {token_result.get("error", "Unknown error")}'
            }), 401

        # Extract user information from token_result
        uid = token_result['uid']
        email = token_result['email']
        email_verified = token_result.get('email_verified', False)
        
        print(f"✅ Firebase user verified: UID={uid}, Email={email}")

        print("🗄️ Checking if user profile exists in Supabase...")
        # Check if user profile already exists
        try:
            existing_response = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
            print(f"🗄️ Existing profile check result: {bool(existing_response.data)}")
        except Exception as db_error:
            print(f"❌ Database error checking existing profile: {str(db_error)}")
            return jsonify({
                'success': False,
                'error': f'Database error: {str(db_error)}'
            }), 500
        
        if existing_response.data:
            print("ℹ️ User profile already exists, returning existing profile")
            # User profile already exists, return success with existing profile
            user_profile = existing_response.data[0]

            # If user is a doctor, get doctor profile too
            doctor_profile = None
            if user_profile['role'] == 'doctor':
                print("👨‍⚕️ Getting doctor profile...")
                try:
                    doc_response = supabase.service_client.table('doctor_profiles').select('*').eq('firebase_uid', uid).execute()
                    if doc_response.data:
                        doctor_profile = doc_response.data[0]
                        print("✅ Doctor profile found")
                    else:
                        print("⚠️ Doctor profile not found")
                except Exception as doc_error:
                    print(f"⚠️ Error getting doctor profile: {str(doc_error)}")

            return jsonify({
                'success': True,
                'token': id_token,
                'user': {
                    'uid': uid,
                    'email': email,
                    'email_verified': email_verified,
                    'profile': user_profile,
                    'doctor_profile': doctor_profile
                },
                'message': 'User already registered'
            }), 200

        print("🆕 Creating new user profile...")
        # Split name into first and last name
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        print(f"📝 Name parts: First='{first_name}', Last='{last_name}'")

        # Create user profile in Supabase
        user_profile_data = {
            'firebase_uid': uid,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'role': role
        }

        print(f"💾 Inserting user profile: {user_profile_data}")
        try:
            profile_response = supabase.service_client.table('user_profiles').insert(user_profile_data).execute()
            print(f"💾 Profile insert result: {bool(profile_response.data)}")
        except Exception as insert_error:
            print(f"❌ Database error inserting profile: {str(insert_error)}")
            return jsonify({
                'success': False,
                'error': f'Failed to insert user profile: {str(insert_error)}'
            }), 500

        if profile_response.data:
            user_profile = profile_response.data[0]
            print("✅ User profile created successfully")

            # If user is a doctor, create doctor profile too
            doctor_profile = None
            if role == 'doctor':
                print("👨‍⚕️ Creating doctor profile...")
                doctor_profile_data = {
                    'firebase_uid': uid,
                    'user_id': user_profile['id'],
                    'specialization': 'General Medicine',  # Default
                    'license_number': f'DR-{uid[:8].upper()}',  # Generate temporary license
                    'years_of_experience': 0
                }
                print(f"💾 Inserting doctor profile: {doctor_profile_data}")
                try:
                    doc_response = supabase.service_client.table('doctor_profiles').insert(doctor_profile_data).execute()
                    if doc_response.data:
                        doctor_profile = doc_response.data[0]
                        print("✅ Doctor profile created successfully")
                    else:
                        print("❌ Failed to create doctor profile")
                except Exception as doc_insert_error:
                    print(f"⚠️ Error creating doctor profile: {str(doc_insert_error)}")

            print("🎉 Registration completed successfully")
            return jsonify({
                'success': True,
                'token': id_token,
                'user': {
                    'uid': uid,
                    'email': email,
                    'email_verified': email_verified,
                    'profile': user_profile,
                    'doctor_profile': doctor_profile
                }
            }), 201
        else:
            print("❌ Failed to create user profile in database")
            return jsonify({
                'success': False,
                'error': 'Failed to create user profile in database'
            }), 500

    except Exception as e:
        print(f"💥 REGISTER ERROR: {str(e)}")
        import traceback
        print(f"💥 Full traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Registration failed: {str(e)}'
        }), 500
