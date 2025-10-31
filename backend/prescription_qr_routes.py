"""
Prescription QR Code Generation and Verification Routes
Handles automatic QR code generation for e-prescriptions
"""
from flask import Blueprint, request, jsonify, send_file
import qrcode
import hashlib
import json
from datetime import datetime
from io import BytesIO
import base64
from auth.firebase_auth import firebase_auth_service
from db.supabase_client import SupabaseClient

prescription_qr_bp = Blueprint('prescription_qr', __name__)
supabase_client = SupabaseClient()
supabase = supabase_client.client

def generate_prescription_hash(prescription_data):
    """Generate a unique hash for prescription verification"""
    # Create a string with critical prescription data
    data_string = f"{prescription_data['id']}|{prescription_data['prescription_number']}|{prescription_data['patient_firebase_uid']}|{prescription_data['doctor_firebase_uid']}|{json.dumps(prescription_data['medications'], sort_keys=True)}"
    
    # Generate SHA-256 hash
    hash_object = hashlib.sha256(data_string.encode())
    return hash_object.hexdigest()

def generate_qr_code_image(data, size=300):
    """Generate QR code image from data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to bytes
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

@prescription_qr_bp.route('/api/prescriptions/generate-qr', methods=['POST'])
def generate_prescription_qr():
    """Generate QR code for a prescription after doctor edits"""
    try:
        # Verify Firebase token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'error': 'No authorization token'}), 401
        
        result = firebase_auth_service.verify_token(token)
        if not result.get('success'):
            return jsonify({'success': False, 'error': result.get('error', 'Invalid token')}), 401
        
        user_uid = result['uid']
        
        # Get request data
        data = request.json
        prescription_id = data.get('prescription_id')
        ai_diagnosis_id = data.get('ai_diagnosis_id')
        modified_prescription = data.get('modified_prescription')
        
        if not prescription_id and not ai_diagnosis_id:
            return jsonify({'success': False, 'error': 'prescription_id or ai_diagnosis_id required'}), 400
        
        # If AI diagnosis, create or update prescription record
        if ai_diagnosis_id:
            # Get AI diagnosis data
            ai_result = supabase.table('ai_diagnoses').select('*').eq('id', ai_diagnosis_id).single().execute()
            
            if not ai_result.data:
                return jsonify({'success': False, 'error': 'AI diagnosis not found'}), 404
            
            ai_diagnosis = ai_result.data
            
            # Check if prescription already exists
            existing_prescription = supabase.table('prescriptions').select('*').eq('ai_diagnosis_id', ai_diagnosis_id).execute()
            
            # Prepare prescription data
            medications = []
            if modified_prescription:
                # Parse modified prescription text into structured format
                medications.append({
                    'name': 'As prescribed by doctor',
                    'dosage': modified_prescription,
                    'frequency': 'As directed',
                    'duration': 'As prescribed'
                })
            elif ai_diagnosis.get('prescription'):
                # Use AI-generated prescription
                prescription_obj = ai_diagnosis['prescription']
                if isinstance(prescription_obj, dict) and 'medications' in prescription_obj:
                    medications = prescription_obj['medications']
                elif isinstance(prescription_obj, str):
                    medications.append({
                        'name': 'AI Recommended',
                        'dosage': prescription_obj,
                        'frequency': 'As directed',
                        'duration': 'As prescribed'
                    })
            
            # Generate unique prescription number
            prescription_number = f"RX-{datetime.now().strftime('%Y%m%d')}-{ai_diagnosis_id[:8].upper()}"
            
            prescription_data = {
                'patient_firebase_uid': ai_diagnosis['patient_firebase_uid'],
                'doctor_firebase_uid': user_uid,
                'ai_diagnosis_id': ai_diagnosis_id,
                'prescription_number': prescription_number,
                'medications': json.dumps(medications) if isinstance(medications, list) else medications,
                'instructions': modified_prescription or ai_diagnosis.get('prescription', ''),
                'status': 'active',
                'issued_date': datetime.now().date().isoformat(),
                'digital_signature': user_uid  # Doctor's UID as signature
            }
            
            if existing_prescription.data and len(existing_prescription.data) > 0:
                # Update existing prescription
                prescription_id = existing_prescription.data[0]['id']
                result = supabase.table('prescriptions').update(prescription_data).eq('id', prescription_id).execute()
                prescription = result.data[0] if result.data else None
            else:
                # Create new prescription
                result = supabase.table('prescriptions').insert(prescription_data).execute()
                prescription = result.data[0] if result.data else None
                prescription_id = prescription['id'] if prescription else None
        else:
            # Get existing prescription
            result = supabase.table('prescriptions').select('*').eq('id', prescription_id).single().execute()
            
            if not result.data:
                return jsonify({'success': False, 'error': 'Prescription not found'}), 404
            
            prescription = result.data
        
        # Generate verification hash
        verification_hash = generate_prescription_hash(prescription)
        
        # Create verification URL
        verification_url = f"{request.host_url}verify-prescription?id={prescription_id}&hash={verification_hash}"
        
        # Generate QR code
        qr_data = {
            'type': 'prescription',
            'id': prescription_id,
            'prescription_number': prescription['prescription_number'],
            'hash': verification_hash,
            'issued_date': prescription['issued_date'],
            'verify_url': verification_url
        }
        
        qr_json = json.dumps(qr_data)
        qr_image = generate_qr_code_image(qr_json)
        
        # Convert to base64 for frontend display
        qr_image.seek(0)
        qr_base64 = base64.b64encode(qr_image.read()).decode('utf-8')
        
        # Update prescription with verification hash
        supabase.table('prescriptions').update({
            'verification_hash': verification_hash,
            'qr_code_data': qr_json,
            'updated_at': datetime.now().isoformat()
        }).eq('id', prescription_id).execute()
        
        # Also update AI diagnosis with verification info
        if ai_diagnosis_id:
            supabase.table('ai_diagnoses').update({
                'prescription_qr_generated': True,
                'prescription_verification_hash': verification_hash,
                'updated_at': datetime.now().isoformat()
            }).eq('id', ai_diagnosis_id).execute()
        
        return jsonify({
            'success': True,
            'data': {
                'prescription_id': prescription_id,
                'qr_code': f"data:image/png;base64,{qr_base64}",
                'verification_hash': verification_hash,
                'verification_url': verification_url,
                'prescription_number': prescription['prescription_number']
            }
        }), 200
        
    except Exception as e:
        print(f"Error generating prescription QR code: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@prescription_qr_bp.route('/api/prescriptions/verify', methods=['POST'])
def verify_prescription():
    """Verify a prescription using QR code data"""
    try:
        data = request.json
        prescription_id = data.get('prescription_id') or data.get('id')
        provided_hash = data.get('hash') or data.get('verification_hash')
        
        if not prescription_id or not provided_hash:
            return jsonify({'success': False, 'error': 'Missing prescription_id or hash'}), 400
        
        # Get prescription from database
        result = supabase.table('prescriptions').select('*').eq('id', prescription_id).single().execute()
        
        if not result.data:
            return jsonify({
                'success': False,
                'verified': False,
                'error': 'Prescription not found'
            }), 404
        
        prescription = result.data
        
        # Generate hash from current prescription data
        current_hash = generate_prescription_hash(prescription)
        
        # Verify hash matches
        is_valid = (current_hash == provided_hash and 
                   prescription.get('verification_hash') == provided_hash)
        
        if is_valid:
            # Get doctor information
            doctor_result = supabase.table('user_profiles').select('full_name, email').eq('firebase_uid', prescription['doctor_firebase_uid']).single().execute()
            doctor_info = doctor_result.data if doctor_result.data else {}
            
            # Get patient information (masked for privacy)
            patient_result = supabase.table('user_profiles').select('full_name').eq('firebase_uid', prescription['patient_firebase_uid']).single().execute()
            patient_name = patient_result.data.get('full_name', 'Unknown') if patient_result.data else 'Unknown'
            
            # Mask patient name
            name_parts = patient_name.split()
            masked_name = f"{name_parts[0]} {'*' * len(name_parts[-1])}" if len(name_parts) > 1 else patient_name[0] + '*' * (len(patient_name) - 1)
            
            return jsonify({
                'success': True,
                'verified': True,
                'data': {
                    'prescription_number': prescription['prescription_number'],
                    'issued_date': prescription['issued_date'],
                    'status': prescription['status'],
                    'doctor_name': doctor_info.get('full_name', 'Unknown'),
                    'patient_name': masked_name,
                    'medications': prescription['medications'],
                    'instructions': prescription['instructions'],
                    'expiry_date': prescription.get('expiry_date'),
                    'verified_at': datetime.now().isoformat()
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'verified': False,
                'error': 'Invalid prescription or data has been tampered with'
            }), 400
            
    except Exception as e:
        print(f"Error verifying prescription: {str(e)}")
        return jsonify({'success': False, 'verified': False, 'error': str(e)}), 500

@prescription_qr_bp.route('/api/prescriptions/<prescription_id>/qr-image', methods=['GET'])
def get_prescription_qr_image(prescription_id):
    """Get QR code image for a prescription"""
    try:
        # Get prescription
        result = supabase.table('prescriptions').select('qr_code_data').eq('id', prescription_id).single().execute()
        
        if not result.data or not result.data.get('qr_code_data'):
            return jsonify({'success': False, 'error': 'QR code not found'}), 404
        
        # Generate QR code image
        qr_image = generate_qr_code_image(result.data['qr_code_data'])
        
        return send_file(qr_image, mimetype='image/png')
        
    except Exception as e:
        print(f"Error getting QR code image: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
