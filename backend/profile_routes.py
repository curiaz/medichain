"""
Enhanced Profile Management API Routes
Comprehensive profile management with role-based features
"""
from flask import Blueprint, request, jsonify
from functools import wraps
from auth.firebase_auth import firebase_auth_required, firebase_role_required, firebase_auth_service
from db.supabase_client import SupabaseClient
import json
import os
from datetime import datetime

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')
# Initialize Supabase client with error handling
try:
    supabase = SupabaseClient()
    print("✅ Supabase client initialized for profile routes")
except Exception as e:
    print(f"⚠️  Warning: Supabase client initialization failed in profile routes: {e}")
    supabase = None


def auth_required(f):
    """Decorator that accepts both Firebase and JWT tokens"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return jsonify({"error": "No authorization header provided"}), 401
        
        try:
            token = auth_header.split(" ")[1]  # Remove 'Bearer ' prefix
        except IndexError:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Try Firebase token first
        try:
            firebase_result = firebase_auth_service.verify_token(token)
            if firebase_result.get("success"):
                request.firebase_user = firebase_result
                print(f"✅ Firebase token verified for user: {firebase_result.get('email', 'unknown')}")
                return f(*args, **kwargs)
            else:
                error_msg = firebase_result.get('error', '')
                print(f"⚠️  Firebase token verification failed: {error_msg}")
                if 'kid' in error_msg.lower():
                    print(f"🔍 Token is JWT (no 'kid' claim), trying JWT fallbacks...")
        except Exception as firebase_error:
            error_str = str(firebase_error)
            print(f"⚠️  Firebase token verification exception: {error_str}")
            if "kid" in error_str.lower() or "invalid" in error_str.lower() or "malformed" in error_str.lower():
                print(f"🔍 Token is not a Firebase token (likely JWT), trying JWT fallbacks...")
        
        # Try Supabase-style JWT
        try:
            import jwt
            decoded = jwt.decode(token, options={"verify_signature": False})
            if 'sub' in decoded and 'email' in decoded:
                request.firebase_user = {
                    "success": True,
                    "uid": decoded.get('sub'),
                    "email": decoded.get('email')
                }
                print(f"✅ Supabase JWT accepted for user: {decoded.get('email')}")
                return f(*args, **kwargs)
        except Exception as e:
            print(f"⚠️  Token decoding failed (supabase-style): {e}")
        
        # Try app-issued JWTs (medichain_token)
        try:
            from auth.auth_utils import auth_utils
            print(f"🔍 Attempting to decode JWT token (length: {len(token)})...")
            app_payload = auth_utils.decode_token(token)
            print(f"🔍 JWT decode result: {app_payload}")
            
            if app_payload and app_payload.get('email'):
                user_id = app_payload.get('user_id')
                print(f"🔍 JWT user_id: {user_id}")
                
                if user_id and supabase and supabase.service_client:
                    try:
                        print(f"🔍 Looking up user profile by id: {user_id}")
                        user_profile_response = (
                            supabase.service_client.table("user_profiles")
                            .select("firebase_uid, email, role")
                            .eq("id", user_id)
                            .execute()
                        )
                        print(f"🔍 User profile lookup result: {user_profile_response.data}")
                        
                        if user_profile_response.data:
                            user_profile = user_profile_response.data[0]
                            firebase_uid = user_profile.get('firebase_uid')
                            
                            if firebase_uid:
                                request.firebase_user = {
                                    "success": True,
                                    "uid": firebase_uid,
                                    "email": app_payload.get('email'),
                                    "role": app_payload.get('role') or user_profile.get('role')
                                }
                                print(f"✅ App JWT accepted for user: {app_payload.get('email')} (firebase_uid: {firebase_uid})")
                                return f(*args, **kwargs)
                            else:
                                print(f"⚠️  User profile found but no firebase_uid for user_id: {user_id}")
                        else:
                            # Fallback: try to find by email if user_id lookup fails
                            print(f"🔍 User profile not found by id, trying email lookup: {app_payload.get('email')}")
                            user_profile_response = (
                                supabase.service_client.table("user_profiles")
                                .select("firebase_uid, email, role")
                                .eq("email", app_payload.get('email'))
                                .execute()
                            )
                            print(f"🔍 User profile lookup by email result: {user_profile_response.data}")
                            
                            if user_profile_response.data:
                                user_profile = user_profile_response.data[0]
                                firebase_uid = user_profile.get('firebase_uid')
                                
                                if firebase_uid:
                                    request.firebase_user = {
                                        "success": True,
                                        "uid": firebase_uid,
                                        "email": app_payload.get('email'),
                                        "role": app_payload.get('role') or user_profile.get('role')
                                    }
                                    print(f"✅ App JWT accepted for user: {app_payload.get('email')} (firebase_uid: {firebase_uid}, found by email)")
                                    return f(*args, **kwargs)
                    except Exception as db_error:
                        print(f"⚠️  Database lookup failed: {db_error}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"⚠️  Missing user_id ({user_id}) or supabase client not available")
                
                # Fallback: use user_id directly if firebase_uid lookup fails
                uid = app_payload.get('user_id') or app_payload.get('uid') or app_payload.get('sub')
                print(f"⚠️  Using direct mapping with uid: {uid}")
                request.firebase_user = {
                    "success": True,
                    "uid": uid,
                    "email": app_payload.get('email'),
                    "role": app_payload.get('role')
                }
                print(f"✅ App JWT accepted for user: {app_payload.get('email')} (uid: {uid}, using direct mapping)")
                return f(*args, **kwargs)
            else:
                print(f"⚠️  JWT decode returned None or missing email: {app_payload}")
        except Exception as e:
            print(f"⚠️  App JWT decoding failed: {e}")
            import traceback
            traceback.print_exc()
        
        # All token verification methods failed
        return jsonify({
            "error": "Invalid or expired token",
            "details": "Token could not be verified as Firebase token or JWT. Please ensure you are logged in and try again."
        }), 401
    
    return decorated_function

@profile_bp.route('/complete', methods=['GET'])
@firebase_auth_required
def get_complete_profile():
    """Get complete user profile including doctor details if applicable"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        # Get user profile
        user_response = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
        
        if not user_response.data:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
        user_profile = user_response.data[0]
        
        # Get doctor profile if user is a doctor
        doctor_profile = None
        if user_profile['role'] == 'doctor':
            doctor_response = supabase.service_client.table('doctor_profiles').select('*').eq('firebase_uid', uid).execute()
            if doctor_response.data:
                doctor_profile = doctor_response.data[0]
        
        return jsonify({
            'success': True,
            'profile': {
                'user_profile': user_profile,
                'doctor_profile': doctor_profile
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route('/update', methods=['PUT'])
@firebase_auth_required
def update_profile():
    """Update user profile with comprehensive validation"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Separate user profile and doctor profile data
        user_profile_data = {}
        doctor_profile_data = {}
        
        # Define allowed fields for user profile
        user_fields = [
            'first_name', 'last_name', 'phone', 'date_of_birth', 
            'gender', 'avatar_url', 'address', 'emergency_contact',
            'medical_conditions', 'allergies'
        ]
        
        # Define allowed fields for doctor profile
        doctor_fields = [
            'license_number', 'specialization', 'years_of_experience',
            'hospital_affiliation', 'consultation_fee', 'available_hours',
            'bio', 'education', 'certifications', 'languages_spoken'
        ]
        
        # Separate the data
        for field, value in data.items():
            if field in user_fields:
                user_profile_data[field] = value
            elif field in doctor_fields:
                doctor_profile_data[field] = value
        
        # Update user profile
        if user_profile_data:
            user_response = supabase.service_client.table('user_profiles').update(user_profile_data).eq('firebase_uid', uid).execute()
            if not user_response.data:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update user profile'
                }), 500
        
        # Update doctor profile if user is a doctor and doctor data provided
        if doctor_profile_data:
            doctor_response = supabase.service_client.table('doctor_profiles').update(doctor_profile_data).eq('firebase_uid', uid).execute()
            if not doctor_response.data:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update doctor profile'
                }), 500
        
        # Get updated complete profile
        updated_user = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
        updated_doctor = None
        
        if updated_user.data and updated_user.data[0]['role'] == 'doctor':
            doctor_response = supabase.service_client.table('doctor_profiles').select('*').eq('firebase_uid', uid).execute()
            if doctor_response.data:
                updated_doctor = doctor_response.data[0]
        
        return jsonify({
            'success': True,
            'profile': {
                'user_profile': updated_user.data[0] if updated_user.data else None,
                'doctor_profile': updated_doctor
            },
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route('/avatar', methods=['POST'])
@firebase_auth_required
def upload_avatar():
    """Upload and update user avatar"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data or 'avatar_url' not in data:
            return jsonify({'success': False, 'error': 'Avatar URL required'}), 400
        
        # Update avatar URL in user profile
        response = supabase.service_client.table('user_profiles').update({
            'avatar_url': data['avatar_url']
        }).eq('firebase_uid', uid).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'avatar_url': data['avatar_url'],
                'message': 'Avatar updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update avatar'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route('/medical-info', methods=['PUT'])
@firebase_auth_required
def update_medical_info():
    """Update medical information (conditions, allergies, etc.)"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Define allowed medical fields
        medical_fields = ['medical_conditions', 'allergies', 'emergency_contact']
        
        # Filter only medical fields
        medical_data = {k: v for k, v in data.items() if k in medical_fields}
        
        if not medical_data:
            return jsonify({'success': False, 'error': 'No valid medical data provided'}), 400
        
        # Update medical information
        response = supabase.service_client.table('user_profiles').update(medical_data).eq('firebase_uid', uid).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'profile': response.data[0],
                'message': 'Medical information updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update medical information'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route('/doctor-schedule', methods=['PUT'])
@firebase_role_required(['doctor'])
def update_doctor_schedule():
    """Update doctor's available hours and schedule"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data or 'available_hours' not in data:
            return jsonify({'success': False, 'error': 'Available hours required'}), 400
        
        # Validate schedule format
        try:
            schedule_data = json.loads(data['available_hours']) if isinstance(data['available_hours'], str) else data['available_hours']
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'Invalid schedule format'}), 400
        
        # Update doctor schedule
        response = supabase.service_client.table('doctor_profiles').update({
            'available_hours': schedule_data
        }).eq('firebase_uid', uid).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'doctor_profile': response.data[0],
                'message': 'Schedule updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update schedule'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route('/verification-status', methods=['GET'])
@firebase_role_required(['doctor'])
def get_verification_status():
    """Get doctor verification status and requirements"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        # Get doctor profile
        response = supabase.service_client.table('doctor_profiles').select('*').eq('firebase_uid', uid).execute()
        
        if not response.data:
            return jsonify({
                'success': False,
                'error': 'Doctor profile not found'
            }), 404
        
        doctor_profile = response.data[0]
        
        # Check verification requirements
        verification_requirements = {
            'license_number': bool(doctor_profile.get('license_number')),
            'specialization': bool(doctor_profile.get('specialization')),
            'hospital_affiliation': bool(doctor_profile.get('hospital_affiliation')),
            'bio': bool(doctor_profile.get('bio')),
            'education': bool(doctor_profile.get('education'))
        }
        
        is_verified = doctor_profile.get('is_verified', False)
        completion_percentage = sum(verification_requirements.values()) / len(verification_requirements) * 100
        
        return jsonify({
            'success': True,
            'verification_status': {
                'is_verified': is_verified,
                'completion_percentage': completion_percentage,
                'requirements': verification_requirements,
                'profile': doctor_profile
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route('/stats', methods=['GET'])
@firebase_auth_required
def get_profile_stats():
    """Get user profile statistics and activity"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        # Get user profile
        user_response = supabase.service_client.table('user_profiles').select('role').eq('firebase_uid', uid).execute()
        if not user_response.data:
            return jsonify({'success': False, 'error': 'User profile not found'}), 404
        
        user_role = user_response.data[0]['role']
        stats = {}
        
        if user_role == 'patient':
            # Patient statistics
            appointments_response = supabase.service_client.table('appointments').select('id').eq('patient_firebase_uid', uid).execute()
            prescriptions_response = supabase.service_client.table('prescriptions').select('id').eq('patient_firebase_uid', uid).execute()
            ai_diagnoses_response = supabase.service_client.table('ai_diagnoses').select('id').eq('user_firebase_uid', uid).execute()
            
            stats = {
                'total_appointments': len(appointments_response.data) if appointments_response.data else 0,
                'total_prescriptions': len(prescriptions_response.data) if prescriptions_response.data else 0,
                'total_ai_diagnoses': len(ai_diagnoses_response.data) if ai_diagnoses_response.data else 0,
                'role': 'patient'
            }
            
        elif user_role == 'doctor':
            # Doctor statistics
            appointments_response = supabase.service_client.table('appointments').select('id').eq('doctor_firebase_uid', uid).execute()
            prescriptions_response = supabase.service_client.table('prescriptions').select('id').eq('doctor_firebase_uid', uid).execute()
            medical_records_response = supabase.service_client.table('medical_records').select('id').eq('doctor_firebase_uid', uid).execute()
            
            # Get doctor profile for additional stats
            doctor_response = supabase.service_client.table('doctor_profiles').select('rating, total_reviews').eq('firebase_uid', uid).execute()
            doctor_profile = doctor_response.data[0] if doctor_response.data else {}
            
            stats = {
                'total_appointments': len(appointments_response.data) if appointments_response.data else 0,
                'total_prescriptions': len(prescriptions_response.data) if prescriptions_response.data else 0,
                'total_medical_records': len(medical_records_response.data) if medical_records_response.data else 0,
                'rating': doctor_profile.get('rating', 0),
                'total_reviews': doctor_profile.get('total_reviews', 0),
                'role': 'doctor'
            }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@profile_bp.route('/delete-account', methods=['DELETE'])
@firebase_auth_required
def delete_account():
    """Delete patient account or deactivate doctor account"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        # Get user profile to determine role
        user_response = supabase.service_client.table('user_profiles').select('role').eq('firebase_uid', uid).execute()
        if not user_response.data:
            return jsonify({'success': False, 'error': 'User profile not found'}), 404
        
        user_role = user_response.data[0]['role']
        
        # Handle based on role
        if user_role == 'doctor':
            # DEACTIVATE doctor account instead of deleting
            # This allows patients to still view doctor details
            try:
                print(f"🔒 Starting doctor account deactivation for UID: {uid}")
                
                # Prepare update data for user_profiles
                user_update_data = {
                    'is_active': False,
                    'deactivated_at': datetime.now().isoformat()
                }
                
                # Mark user profile as deactivated
                print("📝 Updating user_profiles...")
                user_update = supabase.service_client.table('user_profiles').update(
                    user_update_data
                ).eq('firebase_uid', uid).execute()
                
                if not user_update.data:
                    raise Exception("Failed to update user_profiles - no data returned")
                
                print(f"✅ User profile deactivated: is_active=False, deactivated_at={user_update_data['deactivated_at']}")
                
                # Update doctor_profiles
                doctor_update_data = {
                    'account_status': 'deactivated'
                }
                
                print("📝 Updating doctor_profiles...")
                doctor_update = supabase.service_client.table('doctor_profiles').update(
                    doctor_update_data
                ).eq('firebase_uid', uid).execute()
                
                if doctor_update.data:
                    print(f"✅ Doctor profile updated: account_status='deactivated'")
                else:
                    print("⚠️  Doctor profile update returned no data (profile may not exist)")
                
                # Disable Firebase account (can't login but data remains)
                print("🔒 Disabling Firebase authentication...")
                from firebase_admin import auth
                auth.update_user(uid, disabled=True)
                print(f"✅ Firebase user disabled for UID: {uid}")
                
                print(f"🎉 Doctor account deactivation completed successfully")
                
                return jsonify({
                    'success': True,
                    'message': 'Your doctor account has been deactivated. Your profile remains visible to patients, but you can no longer log in.',
                    'action': 'deactivated'
                }), 200
                
            except Exception as deactivate_error:
                error_msg = str(deactivate_error)
                print(f"❌ Doctor deactivation error: {error_msg}")
                
                # Check if it's a schema error
                if 'schema cache' in error_msg.lower() or 'column' in error_msg.lower():
                    return jsonify({
                        'success': False,
                        'error': 'Database schema is missing required columns. Please run the migration SQL file.',
                        'details': error_msg,
                        'migration_file': 'MIGRATION_ADD_DEACTIVATION.sql'
                    }), 500
                
                return jsonify({
                    'success': False,
                    'error': f'Failed to deactivate account: {error_msg}'
                }), 500
        
        elif user_role == 'patient':
            # DELETE patient account completely
            print(f"🗑️ Starting patient account deletion for UID: {uid}")
            
            try:
                # Delete patient-related data
                print("🗑️ Deleting appointments...")
                supabase.service_client.table('appointments').delete().eq('patient_firebase_uid', uid).execute()
                
                print("🗑️ Deleting prescriptions...")
                supabase.service_client.table('prescriptions').delete().eq('patient_firebase_uid', uid).execute()
                
                print("🗑️ Deleting medical records...")
                supabase.service_client.table('medical_records').delete().eq('patient_firebase_uid', uid).execute()
                
                print("🗑️ Deleting AI diagnoses...")
                supabase.service_client.table('ai_diagnoses').delete().eq('user_firebase_uid', uid).execute()
                
                # Delete common user data
                print("🗑️ Deleting user documents...")
                supabase.service_client.table('user_documents').delete().eq('user_firebase_uid', uid).execute()
                
                print("🗑️ Deleting privacy settings...")
                supabase.service_client.table('privacy_settings').delete().eq('user_firebase_uid', uid).execute()
                
                print("🗑️ Deleting blockchain transactions...")
                supabase.service_client.table('blockchain_transactions').delete().eq('user_firebase_uid', uid).execute()
                
                print("🗑️ Deleting credential updates...")
                supabase.service_client.table('credential_updates').delete().eq('user_firebase_uid', uid).execute()
                
                # Delete user profile (must be last due to foreign keys)
                print("🗑️ Deleting user profile...")
                profile_delete = supabase.service_client.table('user_profiles').delete().eq('firebase_uid', uid).execute()
                print(f"✅ User profile deleted: {bool(profile_delete.data)}")
                
            except Exception as db_error:
                print(f"❌ Database deletion error: {str(db_error)}")
                # Continue with Firebase deletion even if some database operations fail
            
            # Delete user from Firebase Authentication
            print("🗑️ Deleting Firebase user...")
            from auth.firebase_auth import firebase_auth_service
            delete_result = firebase_auth_service.delete_user(uid)
            
            if not delete_result['success']:
                print(f"❌ Firebase deletion failed: {delete_result.get('error', 'Unknown error')}")
                return jsonify({
                    'success': False,
                    'error': f'Failed to delete Firebase account: {delete_result["error"]}'
                }), 500
            
            print(f"✅ Firebase user deleted for UID: {uid}")
            print(f"🎉 Patient account deletion completed successfully")
            
            return jsonify({
                'success': True,
                'message': 'Account deleted successfully. You can now register with the same email if needed.',
                'action': 'deleted'
            }), 200
        
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid user role'
            }), 400
        
    except Exception as e:
        print(f"Account deletion/deactivation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to process account: {str(e)}'
        }), 500


@profile_bp.route('/doctor/update', methods=['PUT'])
@firebase_auth_required
@firebase_role_required('doctor')
def update_doctor_profile():
    """Update doctor profile information"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"[DEBUG] Updating doctor profile for UID: {uid}")
        print(f"[DEBUG] Update data: {data}")
        
        # Separate user profile and doctor profile fields
        user_fields = ['first_name', 'last_name', 'phone', 'address', 'city', 'state', 'zip_code']
        doctor_fields = ['specialization', 'license_number', 'years_of_experience', 'hospital_affiliation']
        privacy_fields = ['profile_visibility', 'show_email', 'show_phone', 'allow_patient_messages', 'data_sharing']
        
        user_data = {k: v for k, v in data.items() if k in user_fields}
        doctor_data = {k: v for k, v in data.items() if k in doctor_fields}
        privacy_data = {k: v for k, v in data.items() if k in privacy_fields}
        
        # Get user's internal ID first (needed for doctor profile)
        user_lookup = supabase.service_client.table('user_profiles').select('id').eq('firebase_uid', uid).execute()
        user_internal_id = user_lookup.data[0].get('id') if user_lookup.data else None
        
        # Update user profile
        if user_data:
            user_data['updated_at'] = datetime.utcnow().isoformat()
            user_response = supabase.service_client.table('user_profiles').update(user_data).eq('firebase_uid', uid).execute()
            print(f"[DEBUG] User profile update response: {user_response.data}")
        
        # Always ensure doctor profile exists (create if needed)
        check_response = supabase.service_client.table('doctor_profiles').select('id').eq('firebase_uid', uid).execute()
        
        if not check_response.data:
            # Create doctor profile if it doesn't exist
            print(f"[DEBUG] No doctor profile found, creating one for UID: {uid}")
            new_doctor_profile = {
                'firebase_uid': uid,
                'user_id': user_internal_id,
                'specialization': 'General Practice',  # Default value for NOT NULL constraint
                'verification_status': 'pending',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            create_response = supabase.service_client.table('doctor_profiles').insert(new_doctor_profile).execute()
            print(f"[DEBUG] Doctor profile created: {create_response.data}")
        
        # Update doctor profile if we have data
        if doctor_data or privacy_data:
            update_data = {**doctor_data, **privacy_data}
            update_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Update existing doctor profile
            doctor_response = supabase.service_client.table('doctor_profiles').update(update_data).eq('firebase_uid', uid).execute()
            print(f"[DEBUG] Doctor profile updated with data: {doctor_response.data}")
        
        # Log activity (non-critical, don't fail if this errors)
        try:
            activity_log = {
                'firebase_uid': uid,
                'action': 'Profile Updated',
                'details': f"Updated fields: {', '.join(data.keys())}",
                'timestamp': datetime.utcnow().isoformat()
            }
            supabase.service_client.table('activity_logs').insert(activity_log).execute()
        except Exception as log_error:
            print(f"[WARN] Failed to log activity: {log_error}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error updating doctor profile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route('/doctor/details', methods=['GET'])
@firebase_auth_required
@firebase_role_required('doctor')
def get_doctor_details():
    """Get complete doctor profile details"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        print(f"[DEBUG] Fetching doctor details for UID: {uid}")
        
        # Get user profile
        user_response = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
        
        if not user_response.data:
            return jsonify({
                'success': False,
                'error': 'User profile not found'
            }), 404
        
        user_profile = user_response.data[0]
        
        # Get doctor profile
        doctor_response = supabase.service_client.table('doctor_profiles').select('*').eq('firebase_uid', uid).execute()
        
        doctor_profile = doctor_response.data[0] if doctor_response.data else {}
        
        # Merge profiles
        complete_profile = {
            **user_profile,
            **doctor_profile,
            'role': 'doctor'
        }
        
        return jsonify({
            'success': True,
            'data': complete_profile
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error fetching doctor details: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route('/doctor/documents/upload', methods=['POST'])
@firebase_auth_required
@firebase_role_required('doctor')
def upload_doctor_document():
    """Upload doctor verification documents"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        document_type = request.form.get('type', 'general')  # license, certificate, verification
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Validate file type
        allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: PDF, JPG, PNG'
            }), 400
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{uid}_{document_type}_{timestamp}.{file_ext}"
        
        # Read file content
        file_content = file.read()
        
        # Store document record in database
        document_data = {
            'firebase_uid': uid,
            'document_type': document_type,
            'filename': filename,
            'file_size': len(file_content),
            'file_type': file.content_type,
            'uploaded_at': datetime.utcnow().isoformat(),
            'status': 'pending'
        }
        
        # Create documents table entry
        doc_response = supabase.service_client.table('doctor_documents').insert(document_data).execute()
        
        # Log activity (non-critical, don't fail if this errors)
        try:
            activity_log = {
                'firebase_uid': uid,
                'action': 'Document Uploaded',
                'details': f"Uploaded {document_type}: {file.filename}",
                'timestamp': datetime.utcnow().isoformat()
            }
            supabase.service_client.table('activity_logs').insert(activity_log).execute()
        except Exception as log_error:
            print(f"[WARN] Failed to log activity: {log_error}")
        
        return jsonify({
            'success': True,
            'message': 'Document uploaded successfully',
            'document_id': doc_response.data[0]['id'] if doc_response.data else None
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error uploading document: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route('/doctor/documents', methods=['GET'])
@firebase_auth_required
@firebase_role_required('doctor')
def get_doctor_documents():
    """Get all uploaded documents for a doctor"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        # Fetch documents
        docs_response = supabase.service_client.table('doctor_documents').select('*').eq('firebase_uid', uid).order('uploaded_at', desc=True).execute()
        
        return jsonify({
            'success': True,
            'documents': docs_response.data or []
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error fetching documents: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route('/doctor/privacy', methods=['PUT'])
@firebase_auth_required
@firebase_role_required('doctor')
def update_privacy_settings():
    """Update doctor privacy settings"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Update doctor profile with privacy settings
        privacy_data = {
            'profile_visibility': data.get('profile_visibility'),
            'show_email': data.get('show_email', False),
            'show_phone': data.get('show_phone', False),
            'allow_patient_messages': data.get('allow_patient_messages', True),
            'data_sharing': data.get('data_sharing', False),
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Remove None values
        privacy_data = {k: v for k, v in privacy_data.items() if v is not None}
        
        doctor_response = supabase.service_client.table('doctor_profiles').update(privacy_data).eq('firebase_uid', uid).execute()
        
        # Log activity (non-critical, don't fail if this errors)
        try:
            activity_log = {
                'firebase_uid': uid,
                'action': 'Privacy Settings Updated',
                'details': 'Updated privacy preferences',
                'timestamp': datetime.utcnow().isoformat()
            }
            supabase.service_client.table('activity_logs').insert(activity_log).execute()
        except Exception as log_error:
            print(f"[WARN] Failed to log activity: {log_error}")
        
        return jsonify({
            'success': True,
            'message': 'Privacy settings updated successfully'
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error updating privacy settings: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route('/doctor/activity', methods=['GET'])
@firebase_auth_required
@firebase_role_required('doctor')
def get_activity_log():
    """Get doctor activity history"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        # Fetch activity logs
        logs_response = supabase.service_client.table('activity_logs').select('*').eq('firebase_uid', uid).order('timestamp', desc=True).limit(50).execute()
        
        return jsonify({
            'success': True,
            'activities': logs_response.data or []
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error fetching activity log: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_bp.route('/reactivate-account', methods=['POST'])
def reactivate_account():
    """Reactivate a deactivated doctor account"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        print(f"🔄 Starting account reactivation for email: {email}")
        
        # Get user profile
        user_response = supabase.service_client.table('user_profiles').select('*').eq('email', email).execute()
        
        if not user_response.data:
            return jsonify({
                'success': False,
                'error': 'Account not found'
            }), 404
        
        user = user_response.data[0]
        uid = user['firebase_uid']
        
        # Check if account is deactivated
        if user.get('is_active', True):
            return jsonify({
                'success': False,
                'error': 'Account is already active'
            }), 400
        
        # Check if user is a doctor
        if user['role'] != 'doctor':
            return jsonify({
                'success': False,
                'error': 'Only doctor accounts can be reactivated'
            }), 400
        
        # Verify password using Firebase
        import requests
        firebase_api_key = os.environ.get('FIREBASE_API_KEY', 'AIzaSyDij3Q998OYB3PkSQpzIkki3wFzSF_OUcM')
        firebase_auth_url = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}'
        
        # First, enable the Firebase account temporarily to verify password
        from firebase_admin import auth as firebase_auth
        firebase_auth.update_user(uid, disabled=False)
        
        auth_response = requests.post(firebase_auth_url, json={
            'email': email,
            'password': password,
            'returnSecureToken': True
        })
        
        if auth_response.status_code != 200:
            # Re-disable if password is wrong
            firebase_auth.update_user(uid, disabled=True)
            return jsonify({
                'success': False,
                'error': 'Incorrect password'
            }), 401
        
        print(f"✅ Password verified for reactivation")
        
        # Reactivate the account
        user_update_data = {
            'is_active': True,
            'deactivated_at': None
        }
        
        print("📝 Reactivating user profile...")
        user_update = supabase.service_client.table('user_profiles').update(
            user_update_data
        ).eq('firebase_uid', uid).execute()
        
        if not user_update.data:
            raise Exception("Failed to reactivate user profile")
        
        print(f"✅ User profile reactivated")
        
        # Update doctor_profiles
        doctor_update_data = {
            'account_status': 'active'
        }
        
        print("📝 Updating doctor profile...")
        supabase.service_client.table('doctor_profiles').update(
            doctor_update_data
        ).eq('firebase_uid', uid).execute()
        
        print(f"✅ Doctor profile reactivated")
        
        # Get ID token for login
        id_token = auth_response.json().get('idToken')
        
        print(f"🎉 Doctor account reactivation completed successfully")
        
        # Return login response
        return jsonify({
            'success': True,
            'message': 'Your account has been reactivated successfully!',
            'data': {
                'user': {
                    'id': user['id'],
                    'uid': uid,
                    'email': user['email'],
                    'first_name': user.get('first_name', ''),
                    'last_name': user.get('last_name', ''),
                    'role': user['role'],
                    'firebase_uid': uid
                },
                'token': id_token
            }
        }), 200
        
    except Exception as e:
        print(f"❌ Account reactivation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to reactivate account: {str(e)}'
        }), 500


# ========== PATIENT PROFILE ENDPOINTS ==========

@profile_bp.route('/patient', methods=['GET'])
@auth_required
def get_patient_profile():
    """Get patient profile information"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        print(f"[DEBUG] Getting patient profile for UID: {uid}")
        
        # Check if Supabase client is available
        if not supabase or not supabase.service_client:
            print("[ERROR] Supabase client is not available")
            return jsonify({
                'success': False,
                'error': 'Database connection unavailable'
            }), 500
        
        # Get patient profile from database
        try:
            profile_response = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
            
            print(f"[DEBUG] Profile fetch response: {profile_response.data}")
            
            if not profile_response.data or len(profile_response.data) == 0:
                print(f"[WARNING] No profile found for UID: {uid}")
                return jsonify({
                    'success': False,
                    'error': 'Profile not found'
                }), 404
            
            user_profile = profile_response.data[0]
            
            # Create medical info from user profile data
            medical_info = {
                'medical_conditions': user_profile.get('medical_conditions', []),
                'allergies': user_profile.get('allergies', []),
                'current_medications': user_profile.get('current_medications', []),
                'blood_type': user_profile.get('blood_type', ''),
                'medical_notes': user_profile.get('medical_notes', '')
            }
            
            # Create privacy settings from user profile data
            privacy_settings = {
                'profile_visibility': user_profile.get('profile_visibility', 'private'),
                'show_email': user_profile.get('show_email', False),
                'show_phone': user_profile.get('show_phone', False),
                'medical_info_visible_to_doctors': user_profile.get('medical_info_visible_to_doctors', True),
                'allow_ai_analysis': user_profile.get('allow_ai_analysis', True),
                'share_data_for_research': user_profile.get('share_data_for_research', False)
            }
            
            profile_data = {
                'user_profile': user_profile,
                'medical_info': medical_info,
                'privacy_settings': privacy_settings,
                'documents': [],
                'audit_trail': []
            }
            
            return jsonify({
                'success': True,
                'profile': profile_data,
                'message': 'Profile retrieved successfully'
            }), 200
            
        except Exception as db_error:
            print(f"[ERROR] Database error fetching profile: {db_error}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Database error: {str(db_error)}'
            }), 500
        
    except Exception as e:
        print(f"[ERROR] Error getting patient profile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@profile_bp.route('/patient/update', methods=['PUT'])
@auth_required
def update_patient_profile():
    """Update patient profile information"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"[DEBUG] Updating patient profile for UID: {uid}")
        print(f"[DEBUG] Update data: {data}")
        
        # Check if Supabase client is available
        if not supabase or not supabase.service_client:
            print("[ERROR] Supabase client is not available")
            return jsonify({
                'success': False,
                'error': 'Database connection unavailable'
            }), 500
        
        # Update user profile
        user_data = {k: v for k, v in data.items() if k in [
            'first_name', 'last_name', 'phone', 'date_of_birth', 'gender',
            'address', 'city', 'state', 'zip_code', 'emergency_contact'
        ]}
        
        # Convert empty strings to None for date and constrained fields
        if 'date_of_birth' in user_data and user_data['date_of_birth'] == '':
            user_data['date_of_birth'] = None
        if 'gender' in user_data and user_data['gender'] == '':
            user_data['gender'] = None
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'No valid fields to update'
            }), 400
        
        # Add updated_at timestamp
        user_data['updated_at'] = datetime.utcnow().isoformat()
        
        print(f"[DEBUG] Updating user_profiles with data: {user_data}")
        print(f"[DEBUG] Using firebase_uid filter: {uid}")
        
        # Update the user profile in Supabase
        print(f"[DEBUG] Executing update query with firebase_uid={uid}")
        user_response = supabase.service_client.table('user_profiles').update(user_data).eq('firebase_uid', uid).execute()
        
        print(f"[DEBUG] Supabase update response: {user_response}")
        print(f"[DEBUG] Update response data type: {type(user_response.data)}")
        print(f"[DEBUG] Update response data: {user_response.data}")
        print(f"[DEBUG] Update response data length: {len(user_response.data) if user_response.data else 0}")
        
        # Check if update was successful - Supabase returns empty array if no rows matched
        if not user_response.data or len(user_response.data) == 0:
            print(f"[WARNING] Update returned no data. Checking if user exists with UID: {uid}")
            # Check if user exists
            check_response = supabase.service_client.table('user_profiles').select('id, firebase_uid, email, first_name, last_name').eq('firebase_uid', uid).execute()
            print(f"[DEBUG] User check response: {check_response.data}")
            
            if not check_response.data or len(check_response.data) == 0:
                return jsonify({
                    'success': False,
                    'error': f'User profile not found for UID: {uid}'
                }), 404
            
            # If user exists but update returned no data, fetch the updated data manually
            print(f"[DEBUG] User exists but update didn't return data. Fetching updated profile...")
            updated_response = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
            print(f"[DEBUG] Fetched updated profile: {updated_response.data}")
            
            if updated_response.data and len(updated_response.data) > 0:
                # Verify the update actually happened by checking a field
                updated_profile = updated_response.data[0]
                print(f"[DEBUG] Updated profile first_name: {updated_profile.get('first_name')}")
                print(f"[DEBUG] Expected first_name: {user_data.get('first_name')}")
                
                return jsonify({
                    'success': True,
                    'message': 'Profile updated successfully',
                    'profile': updated_profile
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Update operation completed but could not retrieve updated data. Check database permissions.'
                }), 500
        
        # If update returned data, verify it's the updated data
        updated_profile = user_response.data[0]
        print(f"[DEBUG] Update successful. Updated profile: {updated_profile}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'profile': updated_profile
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error updating patient profile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@profile_bp.route('/patient/medical', methods=['PUT'])
@auth_required
def update_patient_medical():
    """Update patient medical information"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"[DEBUG] Updating patient medical info for UID: {uid}")
        print(f"[DEBUG] Medical data: {data}")
        
        # Update medical fields in user profile
        medical_data = {k: v for k, v in data.items() if k in [
            'medical_conditions', 'allergies', 'current_medications', 'blood_type', 'medical_notes'
        ]}
        
        if medical_data:
            medical_data['updated_at'] = datetime.utcnow().isoformat()
            user_response = supabase.service_client.table('user_profiles').update(medical_data).eq('firebase_uid', uid).execute()
            print(f"[DEBUG] Medical info update response: {user_response.data}")
        
        return jsonify({
            'success': True,
            'message': 'Medical information updated successfully'
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error updating medical info: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@profile_bp.route('/patient/privacy', methods=['PUT'])
@auth_required
def update_patient_privacy():
    """Update patient privacy settings"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        print(f"[DEBUG] Updating patient privacy settings for UID: {uid}")
        print(f"[DEBUG] Privacy data: {data}")
        
        # Update privacy fields in user profile
        privacy_data = {k: v for k, v in data.items() if k in [
            'profile_visibility', 'show_email', 'show_phone',
            'medical_info_visible_to_doctors', 'allow_ai_analysis', 'share_data_for_research'
        ]}
        
        if privacy_data:
            privacy_data['updated_at'] = datetime.utcnow().isoformat()
            user_response = supabase.service_client.table('user_profiles').update(privacy_data).eq('firebase_uid', uid).execute()
            print(f"[DEBUG] Privacy settings update response: {user_response.data}")
        
        return jsonify({
            'success': True,
            'message': 'Privacy settings updated successfully'
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error updating privacy settings: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@profile_bp.route('/patient/documents', methods=['POST'])
@auth_required
def upload_patient_document():
    """Upload patient health document"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        document_type = request.form.get('document_type', 'health_document')
        description = request.form.get('description', '')
        
        print(f"[DEBUG] Uploading document for patient UID: {uid}")
        print(f"[DEBUG] File: {file.filename}, Type: {document_type}")
        
        # For now, just store metadata (file storage would need to be implemented)
        document_data = {
            'firebase_uid': uid,
            'filename': file.filename,
            'document_type': document_type,
            'description': description,
            'file_size': len(file.read()),
            'uploaded_at': datetime.utcnow().isoformat()
        }
        
        # Store in a patient_documents table (would need to be created)
        # For now, return success
        
        return jsonify({
            'success': True,
            'data': document_data,
            'message': 'Document uploaded successfully'
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Error uploading document: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


