"""
MediChain Healthcare System - Backend Routes
Firebase Auth + Supabase integration for healthcare management
"""

from flask import Flask, request, jsonify, Blueprint
from functools import wraps
import firebase_admin
from firebase_admin import credentials, auth
from db.supabase_client import SupabaseClient
import os
from datetime import datetime, timedelta
import uuid

# =====================================================
# FIREBASE AUTH MIDDLEWARE
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
            # Use centralized Firebase auth service for verification (handles clock skew)
            from auth.firebase_auth import firebase_auth_service
            result = firebase_auth_service.verify_token(token)

            if not result.get('success'):
                return jsonify({'error': f"Invalid token: {result.get('error', 'verification failed')}"}), 401

            # Add user info to request
            # Prefer full token data; ensure role comes from custom claims if present
            token_data = result.get('token_data') or {}
            if 'role' not in token_data:
                # Map custom claims role if available
                role = (token_data.get('custom_claims') or {}).get('role')
                if role:
                    token_data['role'] = role
            request.user = token_data
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': f'Invalid token: {str(e)}'}), 401
            
    return decorated_function

# =====================================================
# ROLE-BASED ACCESS CONTROL
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
# HEALTHCARE DATABASE CLASS
# =====================================================

class MediChainDatabase:
    def __init__(self):
        try:
            self.supabase = SupabaseClient()
            self.client = self.supabase.client if self.supabase.client else None
            print("✅ Supabase client initialized for healthcare database")
        except Exception as e:
            print(f"⚠️  Warning: Supabase client initialization failed in healthcare database: {e}")
            self.supabase = None
            self.client = None
    
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
    
    def create_medical_record(self, patient_id, doctor_id, diagnosis, treatment, notes, medications=None):
        """Create a new medical record"""
        try:
            data = {
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'diagnosis': diagnosis,
                'treatment': treatment,
                'notes': notes,
                'medications': medications,
                'visit_date': datetime.utcnow().date().isoformat(),
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
    
    def create_appointment(self, patient_id, doctor_id, appointment_date, reason, status='scheduled'):
        """Create a new appointment"""
        try:
            data = {
                'patient_id': patient_id,
                'doctor_id': doctor_id,
                'appointment_date': appointment_date,
                'reason': reason,
                'status': status,
                'created_at': datetime.utcnow().isoformat()
            }
            
            result = self.client.table('appointments').insert(data).execute()
            return {'success': True, 'data': result.data[0]}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_patient_appointments(self, patient_id):
        """Get all appointments for a patient"""
        try:
            result = self.client.table('appointments').select('*').eq('patient_id', patient_id).execute()
            return {'success': True, 'data': result.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}

# Initialize database (lazy loading)
healthcare_db = None

def get_healthcare_db():
    """Lazy initialization of healthcare database"""
    global healthcare_db
    if healthcare_db is None:
        healthcare_db = MediChainDatabase()
    return healthcare_db

# =====================================================
# HEALTHCARE AUTHENTICATION ROUTES
# =====================================================

healthcare_auth_bp = Blueprint('healthcare_auth', __name__, url_prefix='/api/healthcare/auth')

@healthcare_auth_bp.route('/register-patient', methods=['POST'])
@verify_firebase_token
def register_patient():
    """Register a new patient after Firebase signup"""
    try:
        data = request.get_json()
        firebase_uid = request.user['uid']
        
        # Check if patient already exists
        db = get_healthcare_db()
        existing = db.get_patient_by_firebase_uid(firebase_uid)
        if existing['success']:
            return jsonify({
                'success': True,
                'message': 'Patient already registered',
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
                'message': 'Patient registered successfully',
                'data': result['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error']
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@healthcare_auth_bp.route('/profile', methods=['GET'])
@verify_firebase_token
def get_patient_profile():
    """Get patient profile from Supabase"""
    try:
        firebase_uid = request.user['uid']
        
        db = get_healthcare_db()
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

@healthcare_auth_bp.route('/profile', methods=['PUT'])
@verify_firebase_token
def update_patient_profile():
    """Update patient profile"""
    try:
        firebase_uid = request.user['uid']
        data = request.get_json()
        
        # Remove sensitive fields
        allowed_fields = ['full_name', 'date_of_birth', 'phone', 'address', 'emergency_contact']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        db = get_healthcare_db()
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
# MEDICAL RECORDS ROUTES
# =====================================================

healthcare_medical_bp = Blueprint('healthcare_medical', __name__, url_prefix='/api/healthcare/medical')

@healthcare_medical_bp.route('/records', methods=['GET'])
@verify_firebase_token
def get_medical_records():
    """Get patient's medical records"""
    try:
        firebase_uid = request.user['uid']
        
        # Get patient ID
        db = get_healthcare_db()
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

@healthcare_medical_bp.route('/records', methods=['POST'])
@verify_firebase_token
@require_role('doctor')
def create_medical_record():
    """Create medical record (doctors only)"""
    try:
        data = request.get_json()
        
        db = get_healthcare_db()
        result = db.create_medical_record(
            patient_id=data.get('patient_id'),
            doctor_id=request.user['uid'],
            diagnosis=data.get('diagnosis'),
            treatment=data.get('treatment'),
            notes=data.get('notes'),
            medications=data.get('medications')
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

# =====================================================
# APPOINTMENTS ROUTES
# =====================================================

healthcare_appointments_bp = Blueprint('healthcare_appointments', __name__, url_prefix='/api/healthcare/appointments')

@healthcare_appointments_bp.route('/', methods=['GET'])
@verify_firebase_token
def get_appointments():
    """Get patient's appointments"""
    try:
        firebase_uid = request.user['uid']
        
        # Get patient ID
        db = get_healthcare_db()
        patient = db.get_patient_by_firebase_uid(firebase_uid)
        if not patient['success']:
            return jsonify({'error': 'Patient not found'}), 404
        
        patient_id = patient['data']['id']
        
        # Get appointments
        appointments = db.get_patient_appointments(patient_id)
        if appointments['success']:
            return jsonify({
                'success': True,
                'data': appointments['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': appointments['error']
            }), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@healthcare_appointments_bp.route('/', methods=['POST'])
@verify_firebase_token
def create_appointment():
    """Create new appointment"""
    try:
        firebase_uid = request.user['uid']
        data = request.get_json()
        
        # Get patient ID
        db = get_healthcare_db()
        patient = db.get_patient_by_firebase_uid(firebase_uid)
        if not patient['success']:
            return jsonify({'error': 'Patient not found'}), 404
        
        patient_id = patient['data']['id']
        
        result = db.create_appointment(
            patient_id=patient_id,
            doctor_id=data.get('doctor_id'),
            appointment_date=data.get('appointment_date'),
            reason=data.get('reason')
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

# =====================================================
# HEALTH CHECK ROUTES
# =====================================================

healthcare_system_bp = Blueprint('healthcare_system', __name__, url_prefix='/api/healthcare')

@healthcare_system_bp.route('/health', methods=['GET'])
def health_check():
    """Healthcare system health check"""
    try:
        # Test database connection
        db = get_healthcare_db()
        result = db.client.table('patients').select('id').limit(1).execute()
        
        return jsonify({
            'status': 'healthy',
            'service': 'MediChain Healthcare System',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat(),
            'tables': ['patients', 'doctors', 'medical_records', 'appointments', 'ai_diagnosis_history', 'contact_messages']
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

print("✅ Healthcare system routes loaded!")
print("📋 Available endpoints:")
print("   - POST /api/healthcare/auth/register-patient")
print("   - GET /api/healthcare/auth/profile")
print("   - PUT /api/healthcare/auth/profile")
print("   - GET /api/healthcare/medical/records")
print("   - POST /api/healthcare/medical/records (doctors only)")
print("   - GET /api/healthcare/appointments/")
print("   - POST /api/healthcare/appointments/")
print("   - GET /api/healthcare/health")
print("🔐 All endpoints require Firebase authentication")