"""
Medical Records API Routes
Handles CRUD operations for medical records with Firebase authentication
"""
from flask import Blueprint, request, jsonify
from auth.firebase_auth import firebase_auth_required, firebase_role_required
from db.supabase_client import SupabaseClient

medical_bp = Blueprint('medical', __name__, url_prefix='/api/medical')
supabase = SupabaseClient()

@medical_bp.route('/records', methods=['GET'])
@firebase_auth_required
def get_medical_records():
    """Get user's medical records"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']

        # Get user profile to determine role
        user_response = supabase.client.table('user_profiles').select('role').eq('firebase_uid', uid).execute()
        if not user_response.data:
            return jsonify({'success': False, 'error': 'User profile not found'}), 404

        user_role = user_response.data[0]['role']

        if user_role == 'patient':
            # Patients see their own records
            response = supabase.client.table('medical_records').select('*').eq('patient_firebase_uid', uid).execute()
        elif user_role == 'doctor':
            # Doctors see records of patients they've treated
            response = supabase.client.table('medical_records').select('*').eq('doctor_firebase_uid', uid).execute()
        else:
            return jsonify({'success': False, 'error': 'Unauthorized role'}), 403

        return jsonify({
            'success': True,
            'records': response.data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@medical_bp.route('/records', methods=['POST'])
@firebase_role_required(['doctor'])
def create_medical_record():
    """Create a new medical record (doctors only)"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()

        # Validate required fields
        required_fields = ['patient_firebase_uid', 'record_type', 'title', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

        # Add doctor UID and create record
        record_data = {
            **data,
            'doctor_firebase_uid': uid
        }

        response = supabase.client.table('medical_records').insert(record_data).execute()

        return jsonify({
            'success': True,
            'record': response.data[0] if response.data else None
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@medical_bp.route('/records/<record_id>', methods=['PUT'])
@firebase_role_required(['doctor'])
def update_medical_record(record_id):
    """Update a medical record (doctors only)"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()

        # Update the record (RLS will ensure doctor can only update their own patients' records)
        response = supabase.client.table('medical_records').update(data).eq('id', record_id).eq('doctor_firebase_uid', uid).execute()

        if response.data:
            return jsonify({
                'success': True,
                'record': response.data[0]
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Record not found or unauthorized'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
