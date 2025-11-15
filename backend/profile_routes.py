"""
Enhanced Profile Management API Routes
Comprehensive profile management with role-based features
"""
from flask import Blueprint, request, jsonify
from auth.firebase_auth import firebase_auth_required, firebase_role_required
from db.supabase_client import SupabaseClient
import json
from datetime import datetime

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')
# Initialize Supabase client with error handling
try:
    supabase = SupabaseClient()
    print("✅ Supabase client initialized for profile routes")
except Exception as e:
    print(f"⚠️  Warning: Supabase client initialization failed in profile routes: {e}")
    supabase = None

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

