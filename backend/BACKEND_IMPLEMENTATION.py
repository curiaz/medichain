"""
MediChain Backend - Flask + Firebase Auth + Supabase Integration
Complete backend implementation for healthcare system authentication
"""

from flask import Flask, request, jsonify, Blueprint
from functools import wraps
import firebase_admin
from firebase_admin import credentials, auth
from supabase import create_client, Client
import os
from datetime import datetime, timedelta
import uuid

# =====================================================
# 1. FIREBASE AUTH MIDDLEWARE
# =====================================================

def verify_firebase_token(f):
    """Decorator to verify Firebase ID token"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid authorization header format'}), 401
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
            
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(token)
            request.user = decoded_token  # Add user info to request
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': f'Invalid token: {str(e)}'}), 401
            
    return decorated_function

# =====================================================
# 2. SUPABASE CLIENT SETUP
# =====================================================

class MediChainDatabase:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
    
    def create_patient_record(self, firebase_uid, email, full_name, date_of_birth=None, role='patient'):
        """Create a new patient record in Supabase"""
        try:
            data = {
                'firebase_uid': firebase_uid,
                'email': email,
                'full_name': full_name,
                'role': role,
                'date_of_birth': date_of_birth,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('patients').insert(data).execute()
            return {'success': True, 'data': result.data[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_patient_by_firebase_uid(self, firebase_uid):
        """Get patient record by Firebase UID"""
        try:
            result = self.client.table('patients').select('*').eq('firebase_uid', firebase_uid).single().execute()
            return {'success': True, 'data': result.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_patient_record(self, firebase_uid, data):
        """Update patient record"""
        try:
            data['updated_at'] = datetime.utcnow().isoformat()
            result = self.client.table('patients').update(data).eq('firebase_uid', firebase_uid).execute()
            return {'success': True, 'data': result.data[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_medical_record(self, patient_id, doctor_id, diagnosis, treatment, notes):
        """Create a new medical record"""
        try:
            data = {
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'diagnosis': diagnosis,
                'treatment': treatment,
                'notes': notes,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('medical_records').insert(data).execute()
            return {'success': True, 'data': result.data[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_patient_medical_records(self, patient_id):
        """Get all medical records for a patient"""
        try:
            result = self.client.table('medical_records').select('*').eq('patient_id', patient_id).execute()
            return {'success': True, 'data': result.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Initialize database
db = MediChainDatabase()

# =====================================================
# 3. AUTHENTICATION ROUTES
# =====================================================

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/create-patient', methods=['POST'])
@verify_firebase_token
def create_patient():
    """Create patient record after Firebase signup"""
    try:
        data = request.get_json()
        firebase_uid = request.user['uid']
        
        # Check if patient already exists
        existing = db.get_patient_by_firebase_uid(firebase_uid)
        if existing['success']:
            return jsonify({
                'success': True,
                'message': 'Patient already exists',
                'data': existing['data']
            })
        
        # Create new patient record
        result = db.create_patient_record(
            firebase_uid=firebase_uid,
            email=data.get('email'),
            full_name=data.get('full_name'),
            date_of_birth=data.get('date_of_birth'),
            role=data.get('role', 'patient')
        )
        
        if result['success']:
            # Set custom claims in Firebase for role-based access
            auth.set_custom_user_claims(firebase_uid, {'role': data.get('role', 'patient')})
            
            return jsonify({
                'success': True,
                'message': 'Patient record created successfully',
                'data': result['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/create-or-get-patient', methods=['POST'])
@verify_firebase_token
def create_or_get_patient():
    """Create or get patient record (for Google Auth)"""
    try:
        data = request.get_json()
        firebase_uid = request.user['uid']
        
        # Try to get existing patient
        existing = db.get_patient_by_firebase_uid(firebase_uid)
        if existing['success']:
            return jsonify({
                'success': True,
                'data': existing['data']
            })
        
        # Create new patient if doesn't exist
        result = db.create_patient_record(
            firebase_uid=firebase_uid,
            email=data.get('email'),
            full_name=data.get('full_name'),
            role=data.get('role', 'patient')
        )
        
        if result['success']:
            auth.set_custom_user_claims(firebase_uid, {'role': data.get('role', 'patient')})
            return jsonify({
                'success': True,
                'data': result['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@verify_firebase_token
def get_profile():
    """Get user profile from Supabase"""
    try:
        firebase_uid = request.user['uid']
        
        result = db.get_patient_by_firebase_uid(firebase_uid)
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@verify_firebase_token
def update_profile():
    """Update user profile"""
    try:
        firebase_uid = request.user['uid']
        data = request.get_json()
        
        # Remove sensitive fields
        allowed_fields = ['full_name', 'date_of_birth', 'phone', 'address', 'emergency_contact']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        result = db.update_patient_record(firebase_uid, update_data)
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =====================================================
# 4. ROLE-BASED ACCESS CONTROL
# =====================================================

def require_role(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_role = request.user.get('role')
            if user_role != required_role:
                return jsonify({'error': 'Insufficient permissions'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# =====================================================
# 5. MEDICAL RECORDS ROUTES
# =====================================================

medical_bp = Blueprint('medical', __name__, url_prefix='/api/medical')

@medical_bp.route('/records', methods=['GET'])
@verify_firebase_token
def get_medical_records():
    """Get patient's medical records"""
    try:
        firebase_uid = request.user['uid']
        
        # Get patient ID
        patient = db.get_patient_by_firebase_uid(firebase_uid)
        if not patient['success']:
            return jsonify({'error': 'Patient not found'}), 404
        
        patient_id = patient['data']['id']
        
        # Get medical records
        records = db.get_patient_medical_records(patient_id)
        if records['success']:
            return jsonify({
                'success': True,
                'data': records['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': records['error']
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@medical_bp.route('/records', methods=['POST'])
@verify_firebase_token
@require_role('doctor')
def create_medical_record():
    """Create medical record (doctors only)"""
    try:
        data = request.get_json()
        
        result = db.create_medical_record(
            patient_id=data.get('patient_id'),
            doctor_id=request.user['uid'],
            diagnosis=data.get('diagnosis'),
            treatment=data.get('treatment'),
            notes=data.get('notes')
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

print("✅ Backend Flask routes ready!")
print("✅ Firebase Auth middleware implemented!")
print("✅ Supabase integration complete!")
print("✅ Role-based access control ready!")