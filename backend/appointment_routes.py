"""
Appointments API Routes
Handles appointment scheduling and management
"""
from flask import Blueprint, request, jsonify
from auth.firebase_auth import firebase_auth_required
from db.supabase_client import SupabaseClient
from datetime import datetime

appointments_bp = Blueprint('appointments', __name__, url_prefix='/api/appointments')
supabase = SupabaseClient()

@appointments_bp.route('', methods=['GET'])
@firebase_auth_required
def get_appointments():
    """Get user's appointments"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']

        # Get user profile to determine role
        user_response = supabase.client.table('user_profiles').select('role').eq('firebase_uid', uid).execute()
        if not user_response.data:
            return jsonify({'success': False, 'error': 'User profile not found'}), 404

        user_role = user_response.data[0]['role']

        if user_role == 'patient':
            # Patients see their own appointments
            response = supabase.client.table('appointments').select('*').eq('patient_firebase_uid', uid).execute()
        elif user_role == 'doctor':
            # Doctors see their appointments
            response = supabase.client.table('appointments').select('*').eq('doctor_firebase_uid', uid).execute()
        else:
            return jsonify({'success': False, 'error': 'Unauthorized role'}), 403

        return jsonify({
            'success': True,
            'appointments': response.data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@appointments_bp.route('', methods=['POST'])
@firebase_auth_required
def create_appointment():
    """Create a new appointment"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()

        # Validate required fields
        required_fields = ['doctor_firebase_uid', 'appointment_date']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400

        # Get user role
        user_response = supabase.client.table('user_profiles').select('role').eq('firebase_uid', uid).execute()
        if not user_response.data:
            return jsonify({'success': False, 'error': 'User profile not found'}), 404

        user_role = user_response.data[0]['role']

        if user_role == 'patient':
            # Patients can create appointments for themselves
            appointment_data = {
                **data,
                'patient_firebase_uid': uid
            }
        elif user_role == 'doctor':
            # Doctors can create appointments for patients
            if 'patient_firebase_uid' not in data:
                return jsonify({'success': False, 'error': 'Doctors must specify patient_firebase_uid'}), 400
            appointment_data = data
        else:
            return jsonify({'success': False, 'error': 'Unauthorized role'}), 403

        response = supabase.client.table('appointments').insert(appointment_data).execute()

        return jsonify({
            'success': True,
            'appointment': response.data[0] if response.data else None
        }), 201

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@appointments_bp.route('/<appointment_id>', methods=['PUT'])
@firebase_auth_required
def update_appointment(appointment_id):
    """Update an appointment"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user['uid']
        data = request.get_json()

        # Update appointment (RLS ensures users can only update their own appointments)
        response = supabase.client.table('appointments').update(data).eq('id', appointment_id).or_(
            f'patient_firebase_uid.eq.{uid},doctor_firebase_uid.eq.{uid}'
        ).execute()

        if response.data:
            return jsonify({
                'success': True,
                'appointment': response.data[0]
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Appointment not found or unauthorized'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
