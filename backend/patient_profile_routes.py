from flask import Blueprint, request, jsonify
from db.supabase_client import SupabaseClient
import logging

# Create blueprint for patient profile management
patient_profile_bp = Blueprint('patient_profile', __name__, url_prefix='/api/profile')

# Initialize Supabase client
# Initialize Supabase client with error handling
try:
    supabase = SupabaseClient()
    print("✅ Supabase client initialized for patient profiles")
except Exception as e:
    print(f"⚠️  Warning: Supabase client initialization failed in patient profiles: {e}")
    supabase = None

@patient_profile_bp.route('/patient', methods=['GET'])
def get_patient_profile():
    """
    Get complete patient profile with medical information
    Only accessible by patients
    """
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify user and get user info
        user_info = supabase.verify_firebase_token(token)
        if not user_info:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401
        
        user_id = user_info['user_id']
        user_role = user_info.get('role', 'patient')
        
        # Check if user is a patient
        if user_role != 'patient':
            return jsonify({
                'success': False,
                'message': 'Profile Management is only available for patients'
            }), 403
        
        # Get patient profile from database
        profile_data = supabase.get_patient_profile(user_id)
        
        if profile_data:
            return jsonify({
                'success': True,
                'data': profile_data,
                'message': 'Patient profile retrieved successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Patient profile not found'
            }), 404
            
    except Exception as e:
        logging.error(f"Error getting patient profile: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@patient_profile_bp.route('/patient', methods=['PUT'])
def update_patient_profile():
    """
    Update patient profile information
    Only accessible by patients
    """
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify user and get user info
        user_info = supabase.verify_firebase_token(token)
        if not user_info:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401
        
        user_id = user_info['user_id']
        user_role = user_info.get('role', 'patient')
        
        # Check if user is a patient
        if user_role != 'patient':
            return jsonify({
                'success': False,
                'message': 'Profile Management is only available for patients'
            }), 403
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided'
            }), 400
        
        # Update patient profile
        updated_profile = supabase.update_patient_profile(user_id, data)
        
        if updated_profile:
            return jsonify({
                'success': True,
                'data': updated_profile,
                'message': 'Patient profile updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update patient profile'
            }), 500
            
    except Exception as e:
        logging.error(f"Error updating patient profile: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@patient_profile_bp.route('/patient/medical', methods=['PUT'])
def update_patient_medical_info():
    """
    Update patient medical information
    Only accessible by patients
    """
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify user and get user info
        user_info = supabase.verify_firebase_token(token)
        if not user_info:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401
        
        user_id = user_info['user_id']
        user_role = user_info.get('role', 'patient')
        
        # Check if user is a patient
        if user_role != 'patient':
            return jsonify({
                'success': False,
                'message': 'Medical information management is only available for patients'
            }), 403
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No medical data provided'
            }), 400
        
        # Update patient medical information
        updated_medical = supabase.update_patient_medical_info(user_id, data)
        
        if updated_medical:
            return jsonify({
                'success': True,
                'data': updated_medical,
                'message': 'Medical information updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update medical information'
            }), 500
            
    except Exception as e:
        logging.error(f"Error updating patient medical info: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@patient_profile_bp.route('/patient/documents', methods=['POST'])
def upload_patient_document():
    """
    Upload patient health document
    Only accessible by patients
    """
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify user and get user info
        user_info = supabase.verify_firebase_token(token)
        if not user_info:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401
        
        user_id = user_info['user_id']
        user_role = user_info.get('role', 'patient')
        
        # Check if user is a patient
        if user_role != 'patient':
            return jsonify({
                'success': False,
                'message': 'Document upload is only available for patients'
            }), 403
        
        # Handle file upload
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': 'No file provided'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': 'No file selected'
            }), 400
        
        # Get additional data
        document_type = request.form.get('document_type', 'health_document')
        description = request.form.get('description', '')
        
        # Upload document
        uploaded_doc = supabase.upload_patient_document(user_id, file, document_type, description)
        
        if uploaded_doc:
            return jsonify({
                'success': True,
                'data': uploaded_doc,
                'message': 'Health document uploaded successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to upload document'
            }), 500
            
    except Exception as e:
        logging.error(f"Error uploading patient document: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

@patient_profile_bp.route('/patient/privacy', methods=['PUT'])
def update_patient_privacy_settings():
    """
    Update patient privacy settings
    Only accessible by patients
    """
    try:
        # Get authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authorization token required'
            }), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify user and get user info
        user_info = supabase.verify_firebase_token(token)
        if not user_info:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token'
            }), 401
        
        user_id = user_info['user_id']
        user_role = user_info.get('role', 'patient')
        
        # Check if user is a patient
        if user_role != 'patient':
            return jsonify({
                'success': False,
                'message': 'Privacy settings management is only available for patients'
            }), 403
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'No privacy settings provided'
            }), 400
        
        # Update patient privacy settings
        updated_privacy = supabase.update_patient_privacy_settings(user_id, data)
        
        if updated_privacy:
            return jsonify({
                'success': True,
                'data': updated_privacy,
                'message': 'Privacy settings updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to update privacy settings'
            }), 500
            
    except Exception as e:
        logging.error(f"Error updating patient privacy settings: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500

