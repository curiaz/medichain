"""
Comprehensive Profile Management System
AI-Driven Diagnosis and Prescription System with Blockchain-Integrated Health Records
"""
from flask import Blueprint, request, jsonify
from auth.firebase_auth import firebase_auth_required, firebase_role_required
from db.supabase_client import SupabaseClient
import json
import hashlib
import uuid
from datetime import datetime
import os
from werkzeug.utils import secure_filename

profile_mgmt_bp = Blueprint('profile_mgmt', __name__, url_prefix='/api/profile-management')
supabase = SupabaseClient()

# Allowed file extensions for document uploads
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'txt'}
UPLOAD_FOLDER = 'uploads/documents'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_blockchain_hash(data):
    """Generate a blockchain hash for audit trail"""
    data_string = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(data_string.encode()).hexdigest()

def create_blockchain_transaction(user_id, action, data_hash, metadata=None):
    """Create a blockchain transaction record"""
    transaction_data = {
        'user_firebase_uid': user_id,
        'action': action,
        'data_hash': data_hash,
        'metadata': metadata or {},
        'timestamp': datetime.utcnow().isoformat(),
        'blockchain_tx_hash': generate_blockchain_hash({
            'user_id': user_id,
            'action': action,
            'data_hash': data_hash,
            'timestamp': datetime.utcnow().isoformat()
        })
    }
    
    try:
        response = supabase.service_client.table('blockchain_transactions').insert(transaction_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating blockchain transaction: {e}")
        return None

@profile_mgmt_bp.route('/complete-profile', methods=['GET'])
@firebase_auth_required
def get_complete_profile():
    """Get complete user profile with all related data"""
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
        
        # Get doctor profile if applicable
        doctor_profile = None
        if user_profile['role'] == 'doctor':
            doctor_response = supabase.service_client.table('doctor_profiles').select('*').eq('firebase_uid', uid).execute()
            if doctor_response.data:
                doctor_profile = doctor_response.data[0]
        
        # Get uploaded documents
        documents_response = supabase.service_client.table('user_documents').select('*').eq('user_firebase_uid', uid).execute()
        documents = documents_response.data if documents_response.data else []
        
        # Get privacy settings
        privacy_response = supabase.service_client.table('privacy_settings').select('*').eq('user_firebase_uid', uid).execute()
        privacy_settings = privacy_response.data[0] if privacy_response.data else None
        
        # Get blockchain transaction history
        blockchain_response = supabase.service_client.table('blockchain_transactions').select('*').eq('user_firebase_uid', uid).order('timestamp', desc=True).limit(10).execute()
        blockchain_history = blockchain_response.data if blockchain_response.data else []
        
        return jsonify({
            'success': True,
            'profile': {
                'user_profile': user_profile,
                'doctor_profile': doctor_profile,
                'documents': documents,
                'privacy_settings': privacy_settings,
                'blockchain_history': blockchain_history
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_mgmt_bp.route('/update-personal-info', methods=['PUT'])
@firebase_auth_required
def update_personal_info():
    """Update personal information with blockchain audit trail"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        allowed_fields = [
            'first_name', 'last_name', 'phone', 'date_of_birth', 
            'gender', 'address', 'emergency_contact'
        ]
        
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'success': False, 'error': 'No valid fields to update'}), 400
        
        # Get current profile for comparison
        current_response = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
        if not current_response.data:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404
        
        current_profile = current_response.data[0]
        
        # Update profile
        response = supabase.service_client.table('user_profiles').update(update_data).eq('firebase_uid', uid).execute()
        
        if response.data:
            updated_profile = response.data[0]
            
            # Create blockchain transaction
            data_hash = generate_blockchain_hash(update_data)
            blockchain_tx = create_blockchain_transaction(
                uid, 
                'PERSONAL_INFO_UPDATE', 
                data_hash,
                {
                    'updated_fields': list(update_data.keys()),
                    'previous_values': {k: current_profile.get(k) for k in update_data.keys()},
                    'new_values': update_data
                }
            )
            
            return jsonify({
                'success': True,
                'profile': updated_profile,
                'blockchain_transaction': blockchain_tx,
                'message': 'Personal information updated successfully'
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

@profile_mgmt_bp.route('/update-medical-info', methods=['PUT'])
@firebase_auth_required
def update_medical_info():
    """Update medical information with blockchain audit trail"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate medical fields
        allowed_fields = [
            'medical_conditions', 'allergies', 'current_medications',
            'blood_type', 'emergency_contact', 'medical_notes'
        ]
        
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'success': False, 'error': 'No valid medical fields to update'}), 400
        
        # Get current profile
        current_response = supabase.service_client.table('user_profiles').select('*').eq('firebase_uid', uid).execute()
        if not current_response.data:
            return jsonify({'success': False, 'error': 'Profile not found'}), 404
        
        current_profile = current_response.data[0]
        
        # Update medical information
        response = supabase.service_client.table('user_profiles').update(update_data).eq('firebase_uid', uid).execute()
        
        if response.data:
            updated_profile = response.data[0]
            
            # Create blockchain transaction
            data_hash = generate_blockchain_hash(update_data)
            blockchain_tx = create_blockchain_transaction(
                uid,
                'MEDICAL_INFO_UPDATE',
                data_hash,
                {
                    'updated_fields': list(update_data.keys()),
                    'previous_values': {k: current_profile.get(k) for k in update_data.keys()},
                    'new_values': update_data
                }
            )
            
            return jsonify({
                'success': True,
                'profile': updated_profile,
                'blockchain_transaction': blockchain_tx,
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

@profile_mgmt_bp.route('/upload-document', methods=['POST'])
@firebase_auth_required
def upload_document():
    """Upload and securely store documents"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        document_type = request.form.get('document_type', 'general')
        description = request.form.get('description', '')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400
        
        # Generate secure filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uid}_{uuid.uuid4().hex}_{filename}"
        
        # Create upload directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)
        
        # Get file hash for blockchain
        with open(file_path, 'rb') as f:
            file_content = f.read()
            file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Store document metadata in database
        document_data = {
            'user_firebase_uid': uid,
            'filename': filename,
            'unique_filename': unique_filename,
            'file_path': file_path,
            'file_hash': file_hash,
            'document_type': document_type,
            'description': description,
            'file_size': len(file_content),
            'upload_date': datetime.utcnow().isoformat()
        }
        
        response = supabase.service_client.table('user_documents').insert(document_data).execute()
        
        if response.data:
            document = response.data[0]
            
            # Create blockchain transaction
            blockchain_tx = create_blockchain_transaction(
                uid,
                'DOCUMENT_UPLOAD',
                file_hash,
                {
                    'document_id': document['id'],
                    'filename': filename,
                    'document_type': document_type,
                    'file_size': len(file_content)
                }
            )
            
            return jsonify({
                'success': True,
                'document': document,
                'blockchain_transaction': blockchain_tx,
                'message': 'Document uploaded successfully'
            }), 201
        else:
            # Clean up file if database insert failed
            os.remove(file_path)
            return jsonify({
                'success': False,
                'error': 'Failed to save document metadata'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_mgmt_bp.route('/documents', methods=['GET'])
@firebase_auth_required
def get_documents():
    """Get user's uploaded documents"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        response = supabase.service_client.table('user_documents').select('*').eq('user_firebase_uid', uid).order('upload_date', desc=True).execute()
        
        return jsonify({
            'success': True,
            'documents': response.data if response.data else []
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_mgmt_bp.route('/documents/<document_id>', methods=['DELETE'])
@firebase_auth_required
def delete_document(document_id):
    """Delete a document"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        # Get document info
        doc_response = supabase.service_client.table('user_documents').select('*').eq('id', document_id).eq('user_firebase_uid', uid).execute()
        
        if not doc_response.data:
            return jsonify({'success': False, 'error': 'Document not found'}), 404
        
        document = doc_response.data[0]
        
        # Delete from database
        delete_response = supabase.service_client.table('user_documents').delete().eq('id', document_id).eq('user_firebase_uid', uid).execute()
        
        if delete_response.data:
            # Delete physical file
            try:
                os.remove(document['file_path'])
            except FileNotFoundError:
                pass  # File already deleted
            
            # Create blockchain transaction
            blockchain_tx = create_blockchain_transaction(
                uid,
                'DOCUMENT_DELETE',
                document['file_hash'],
                {
                    'document_id': document_id,
                    'filename': document['filename'],
                    'document_type': document['document_type']
                }
            )
            
            return jsonify({
                'success': True,
                'blockchain_transaction': blockchain_tx,
                'message': 'Document deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete document'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_mgmt_bp.route('/privacy-settings', methods=['GET'])
@firebase_auth_required
def get_privacy_settings():
    """Get user's privacy settings"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        response = supabase.service_client.table('privacy_settings').select('*').eq('user_firebase_uid', uid).execute()
        
        if response.data:
            return jsonify({
                'success': True,
                'privacy_settings': response.data[0]
            }), 200
        else:
            # Return default privacy settings
            default_settings = {
                'user_firebase_uid': uid,
                'profile_visibility': 'private',
                'medical_info_visible_to_doctors': True,
                'medical_info_visible_to_hospitals': False,
                'medical_info_visible_to_admins': False,
                'allow_ai_analysis': True,
                'share_data_for_research': False,
                'emergency_access_enabled': True,
                'two_factor_enabled': False,
                'login_notifications': True,
                'data_export_enabled': True
            }
            return jsonify({
                'success': True,
                'privacy_settings': default_settings
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_mgmt_bp.route('/privacy-settings', methods=['PUT'])
@firebase_auth_required
def update_privacy_settings():
    """Update privacy and security settings"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate privacy settings
        allowed_fields = [
            'profile_visibility', 'medical_info_visible_to_doctors',
            'medical_info_visible_to_hospitals', 'medical_info_visible_to_admins',
            'allow_ai_analysis', 'share_data_for_research', 'emergency_access_enabled',
            'two_factor_enabled', 'login_notifications', 'data_export_enabled'
        ]
        
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        update_data['user_firebase_uid'] = uid
        
        # Check if privacy settings exist
        existing_response = supabase.service_client.table('privacy_settings').select('id').eq('user_firebase_uid', uid).execute()
        
        if existing_response.data:
            # Update existing settings
            response = supabase.service_client.table('privacy_settings').update(update_data).eq('user_firebase_uid', uid).execute()
        else:
            # Create new settings
            response = supabase.service_client.table('privacy_settings').insert(update_data).execute()
        
        if response.data:
            updated_settings = response.data[0]
            
            # Create blockchain transaction
            data_hash = generate_blockchain_hash(update_data)
            blockchain_tx = create_blockchain_transaction(
                uid,
                'PRIVACY_SETTINGS_UPDATE',
                data_hash,
                {
                    'updated_fields': list(update_data.keys()),
                    'new_values': update_data
                }
            )
            
            return jsonify({
                'success': True,
                'privacy_settings': updated_settings,
                'blockchain_transaction': blockchain_tx,
                'message': 'Privacy settings updated successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update privacy settings'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_mgmt_bp.route('/update-credentials', methods=['PUT'])
@firebase_auth_required
def update_credentials():
    """Update login credentials (email, password, 2FA)"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # This would typically integrate with Firebase Auth
        # For now, we'll just log the request and create a blockchain transaction
        
        credential_data = {
            'user_firebase_uid': uid,
            'credential_type': data.get('credential_type', 'unknown'),
            'update_timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        
        # Store credential update record
        response = supabase.service_client.table('credential_updates').insert(credential_data).execute()
        
        if response.data:
            # Create blockchain transaction
            data_hash = generate_blockchain_hash(credential_data)
            blockchain_tx = create_blockchain_transaction(
                uid,
                'CREDENTIAL_UPDATE',
                data_hash,
                {
                    'credential_type': data.get('credential_type', 'unknown'),
                    'ip_address': request.remote_addr
                }
            )
            
            return jsonify({
                'success': True,
                'credential_update': response.data[0],
                'blockchain_transaction': blockchain_tx,
                'message': 'Credential update recorded successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to record credential update'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_mgmt_bp.route('/blockchain-history', methods=['GET'])
@firebase_auth_required
def get_blockchain_history():
    """Get user's blockchain transaction history"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit
        
        response = supabase.service_client.table('blockchain_transactions').select('*').eq('user_firebase_uid', uid).order('timestamp', desc=True).range(offset, offset + limit - 1).execute()
        
        # Get total count
        count_response = supabase.service_client.table('blockchain_transactions').select('id', count='exact').eq('user_firebase_uid', uid).execute()
        total_count = count_response.count if count_response.count else 0
        
        return jsonify({
            'success': True,
            'transactions': response.data if response.data else [],
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total_count,
                'pages': (total_count + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profile_mgmt_bp.route('/audit-trail', methods=['GET'])
@firebase_auth_required
def get_audit_trail():
    """Get comprehensive audit trail for profile changes"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        
        # Get all blockchain transactions
        blockchain_response = supabase.service_client.table('blockchain_transactions').select('*').eq('user_firebase_uid', uid).order('timestamp', desc=True).execute()
        
        # Get document uploads
        documents_response = supabase.service_client.table('user_documents').select('*').eq('user_firebase_uid', uid).order('upload_date', desc=True).execute()
        
        # Get credential updates
        credentials_response = supabase.service_client.table('credential_updates').select('*').eq('user_firebase_uid', uid).order('update_timestamp', desc=True).execute()
        
        audit_trail = []
        
        # Combine all activities
        if blockchain_response.data:
            for tx in blockchain_response.data:
                audit_trail.append({
                    'type': 'blockchain_transaction',
                    'action': tx['action'],
                    'timestamp': tx['timestamp'],
                    'data_hash': tx['data_hash'],
                    'metadata': tx['metadata']
                })
        
        if documents_response.data:
            for doc in documents_response.data:
                audit_trail.append({
                    'type': 'document_upload',
                    'action': 'DOCUMENT_UPLOAD',
                    'timestamp': doc['upload_date'],
                    'filename': doc['filename'],
                    'document_type': doc['document_type']
                })
        
        if credentials_response.data:
            for cred in credentials_response.data:
                audit_trail.append({
                    'type': 'credential_update',
                    'action': 'CREDENTIAL_UPDATE',
                    'timestamp': cred['update_timestamp'],
                    'credential_type': cred['credential_type']
                })
        
        # Sort by timestamp
        audit_trail.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'success': True,
            'audit_trail': audit_trail
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

