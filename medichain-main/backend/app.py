"""
Flask backend application for medical records with AES encryption and SHA-256 hashing
"""
# Disable SSL verification BEFORE importing anything (Windows SSL issues)
import os
import ssl
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['SSL_VERIFY'] = 'false'

# Set SSL context globally to not verify certificates
ssl._create_default_https_context = ssl._create_unverified_context

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from core.crypto_utils import MedicalRecordCrypto
from db.supabase_client import SupabaseClient
print("DEBUG: About to import auth_routes_simple")
from auth.auth_routes_simple import auth_bp
print("DEBUG: Successfully imported auth_bp from auth_routes_simple")

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize services
supabase_client = SupabaseClient()
crypto = MedicalRecordCrypto(os.getenv('AES_ENCRYPTION_KEY', '').encode('utf-8'))

# Register blueprints
app.register_blueprint(auth_bp)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'medical-records-api'})

@app.route('/api/medical-records', methods=['POST'])
def create_medical_record():
    """Create a new encrypted medical record"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['patient_id', 'diagnosis', 'prescription']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Encrypt sensitive fields
        encrypted_data = crypto.encrypt_medical_record(
            diagnosis=data['diagnosis'],
            prescription=data['prescription']
        )
        
        # Compute hash of encrypted data for integrity verification
        combined_encrypted = encrypted_data['diagnosis'] + encrypted_data['prescription']
        blockchain_hash = crypto.compute_hash(combined_encrypted)
        
        # Prepare record data
        record_data = {
            'patient_id': data['patient_id'],
            'doctor_id': data.get('doctor_id'),
            'diagnosis': encrypted_data['diagnosis'],
            'prescription': encrypted_data['prescription'],
            'blockchain_tx_hash': blockchain_hash
        }
        
        # Save to database
        created_record = supabase_client.create_health_record(record_data)
        
        if created_record:
            return jsonify({
                'success': True,
                'data': {
                    'id': created_record['id'],
                    'patient_id': created_record['patient_id'],
                    'doctor_id': created_record.get('doctor_id'),
                    'blockchain_tx_hash': created_record['blockchain_tx_hash'],
                    'created_at': created_record['created_at']
                }
            }), 201
        else:
            return jsonify({'error': 'Failed to create medical record'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medical-records/<record_id>', methods=['GET'])
def get_medical_record(record_id):
    """Retrieve and decrypt a medical record"""
    try:
        record = supabase_client.get_health_record(record_id)
        
        if not record:
            return jsonify({'error': 'Medical record not found'}), 404
        
        # Decrypt sensitive fields
        decrypted_data = crypto.decrypt_medical_record(
            encrypted_diagnosis=record['diagnosis'],
            encrypted_prescription=record['prescription']
        )
        
        # Verify integrity
        combined_encrypted = record['diagnosis'] + record['prescription']
        computed_hash = crypto.compute_hash(combined_encrypted)
        is_valid = computed_hash == record['blockchain_tx_hash']
        
        return jsonify({
            'success': True,
            'data': {
                'id': record['id'],
                'patient_id': record['patient_id'],
                'doctor_id': record.get('doctor_id'),
                'diagnosis': decrypted_data['diagnosis'],
                'prescription': decrypted_data['prescription'],
                'blockchain_tx_hash': record['blockchain_tx_hash'],
                'is_integrity_valid': is_valid,
                'created_at': record['created_at']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medical-records/patient/<patient_id>', methods=['GET'])
def get_patient_medical_records(patient_id):
    """Get all medical records for a specific patient"""
    try:
        records = supabase_client.get_health_records_by_patient(patient_id)
        
        decrypted_records = []
        for record in records:
            decrypted_data = crypto.decrypt_medical_record(
                encrypted_diagnosis=record['diagnosis'],
                encrypted_prescription=record['prescription']
            )
            
            combined_encrypted = record['diagnosis'] + record['prescription']
            computed_hash = crypto.compute_hash(combined_encrypted)
            is_valid = computed_hash == record['blockchain_tx_hash']
            
            decrypted_records.append({
                'id': record['id'],
                'patient_id': record['patient_id'],
                'doctor_id': record.get('doctor_id'),
                'diagnosis': decrypted_data['diagnosis'],
                'prescription': decrypted_data['prescription'],
                'blockchain_tx_hash': record['blockchain_tx_hash'],
                'is_integrity_valid': is_valid,
                'created_at': record['created_at']
            })
        
        return jsonify({
            'success': True,
            'data': decrypted_records
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medical-records/<record_id>', methods=['PUT'])
def update_medical_record(record_id):
    """Update an existing medical record"""
    try:
        data = request.get_json()
        
        # Get existing record
        existing_record = supabase_client.get_health_record(record_id)
        if not existing_record:
            return jsonify({'error': 'Medical record not found'}), 404
        
        # Encrypt updated fields
        encrypted_data = {}
        if 'diagnosis' in data:
            encrypted_data['diagnosis'] = crypto.encrypt_field(data['diagnosis'])
        else:
            encrypted_data['diagnosis'] = existing_record['diagnosis']
            
        if 'prescription' in data:
            encrypted_data['prescription'] = crypto.encrypt_field(data['prescription'])
        else:
            encrypted_data['prescription'] = existing_record['prescription']
        
        # Update hash
        combined_encrypted = encrypted_data['diagnosis'] + encrypted_data['prescription']
        encrypted_data['blockchain_tx_hash'] = crypto.compute_hash(combined_encrypted)
        
        # Update record
        updated_record = supabase_client.update_health_record(record_id, encrypted_data)
        
        if updated_record:
            return jsonify({
                'success': True,
                'data': {
                    'id': updated_record['id'],
                    'patient_id': updated_record['patient_id'],
                    'doctor_id': updated_record.get('doctor_id'),
                    'blockchain_tx_hash': updated_record['blockchain_tx_hash'],
                    'created_at': updated_record['created_at']
                }
            }), 200
        else:
            return jsonify({'error': 'Failed to update medical record'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/medical-records/<record_id>', methods=['DELETE'])
def delete_medical_record(record_id):
    """Delete a medical record"""
    try:
        deleted_record = supabase_client.delete_health_record(record_id)
        
        if deleted_record:
            return jsonify({'success': True, 'message': 'Medical record deleted'}), 200
        else:
            return jsonify({'error': 'Medical record not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.getenv('FLASK_PORT', 5000)))
