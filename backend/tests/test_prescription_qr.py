"""
Unit Tests for Prescription QR Code Routes
Tests QR generation, verification, and security features
"""

import pytest
import json
import hashlib
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from flask import Flask
from prescription_qr_routes import (
    prescription_qr_bp,
    generate_prescription_hash,
    generate_qr_code_image
)


@pytest.fixture
def app():
    """Create Flask app for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.register_blueprint(prescription_qr_bp)
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def mock_auth():
    """Mock Firebase authentication"""
    with patch('prescription_qr_routes.firebase_auth_service') as mock:
        mock.verify_token.return_value = {
            'success': True,
            'uid': 'test-doctor-uid-123',
            'email': 'doctor@test.com'
        }
        yield mock


@pytest.fixture
def mock_supabase():
    """Mock Supabase client"""
    with patch('prescription_qr_routes.supabase') as mock:
        yield mock


class TestGeneratePrescriptionHash:
    """Test hash generation functionality"""
    
    def test_hash_consistency(self):
        """Test that same data produces same hash"""
        prescription_data = {
            'id': 'test-id-123',
            'prescription_number': 'RX-20251030-TEST',
            'patient_firebase_uid': 'patient-uid',
            'doctor_firebase_uid': 'doctor-uid',
            'medications': json.dumps([{'name': 'Amoxicillin', 'dosage': '500mg'}])
        }
        
        hash1 = generate_prescription_hash(prescription_data)
        hash2 = generate_prescription_hash(prescription_data)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produces 64 character hex
    
    def test_hash_tamper_detection(self):
        """Test that different data produces different hash"""
        prescription_data1 = {
            'id': 'test-id-123',
            'prescription_number': 'RX-20251030-TEST',
            'patient_firebase_uid': 'patient-uid',
            'doctor_firebase_uid': 'doctor-uid',
            'medications': json.dumps([{'name': 'Amoxicillin', 'dosage': '500mg'}])
        }
        
        prescription_data2 = prescription_data1.copy()
        prescription_data2['medications'] = json.dumps([{'name': 'Aspirin', 'dosage': '100mg'}])
        
        hash1 = generate_prescription_hash(prescription_data1)
        hash2 = generate_prescription_hash(prescription_data2)
        
        assert hash1 != hash2
    
    def test_hash_format(self):
        """Test hash is valid SHA-256"""
        prescription_data = {
            'id': 'test-id-123',
            'prescription_number': 'RX-20251030-TEST',
            'patient_firebase_uid': 'patient-uid',
            'doctor_firebase_uid': 'doctor-uid',
            'medications': json.dumps([])
        }
        
        hash_value = generate_prescription_hash(prescription_data)
        
        # Should be valid hex string
        assert all(c in '0123456789abcdef' for c in hash_value)
        assert len(hash_value) == 64


class TestGenerateQRCodeImage:
    """Test QR code image generation"""
    
    def test_qr_generation(self):
        """Test QR code is generated"""
        test_data = json.dumps({
            'type': 'prescription',
            'id': 'test-id-123',
            'hash': 'abc123'
        })
        
        qr_image = generate_qr_code_image(test_data)
        
        assert qr_image is not None
        assert isinstance(qr_image, BytesIO)
        assert qr_image.tell() == 0  # Should be at start of buffer
    
    def test_qr_contains_data(self):
        """Test QR code contains valid image data"""
        test_data = json.dumps({'test': 'data'})
        
        qr_image = generate_qr_code_image(test_data)
        image_bytes = qr_image.getvalue()
        
        assert len(image_bytes) > 0
        # PNG files start with these bytes
        assert image_bytes[:4] == b'\x89PNG'
    
    def test_qr_size_variation(self):
        """Test QR code with different data sizes"""
        small_data = json.dumps({'id': '1'})
        large_data = json.dumps({
            'id': 'test-id-123',
            'prescription_number': 'RX-20251030-TEST',
            'hash': 'a' * 64,
            'verify_url': 'http://localhost:3000/verify-prescription?id=test&hash=abc123'
        })
        
        qr_small = generate_qr_code_image(small_data)
        qr_large = generate_qr_code_image(large_data)
        
        assert len(qr_small.getvalue()) > 0
        assert len(qr_large.getvalue()) > 0
        # Larger data should produce larger QR code
        assert len(qr_large.getvalue()) > len(qr_small.getvalue())


class TestGenerateQREndpoint:
    """Test /api/prescriptions/generate-qr endpoint"""
    
    def test_missing_token(self, client):
        """Test endpoint requires authentication"""
        response = client.post('/api/prescriptions/generate-qr', json={})
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'authorization' in data['error'].lower()
    
    def test_invalid_token(self, client):
        """Test endpoint rejects invalid token"""
        with patch('prescription_qr_routes.firebase_auth_service') as mock_auth:
            mock_auth.verify_token.return_value = {
                'success': False,
                'error': 'Invalid token'
            }
            
            response = client.post(
                '/api/prescriptions/generate-qr',
                json={},
                headers={'Authorization': 'Bearer invalid-token'}
            )
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_missing_required_fields(self, client, mock_auth):
        """Test endpoint requires prescription_id or ai_diagnosis_id"""
        response = client.post(
            '/api/prescriptions/generate-qr',
            json={},
            headers={'Authorization': 'Bearer test-token'}
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'required' in data['error'].lower()
    
    @patch('prescription_qr_routes.supabase')
    def test_successful_qr_generation(self, mock_supabase, client, mock_auth):
        """Test successful QR generation for AI diagnosis"""
        # Mock AI diagnosis data
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
            data={
                'id': 'test-diagnosis-123',
                'patient_firebase_uid': 'patient-uid',
                'prescription': {'medications': ['Amoxicillin 500mg']}
            }
        )
        
        # Mock prescription check (no existing)
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[]
        )
        
        # Mock prescription insert
        mock_supabase.table.return_value.insert.return_value.execute.return_value = Mock(
            data=[{
                'id': 'new-prescription-123',
                'prescription_number': 'RX-20251030-TEST',
                'patient_firebase_uid': 'patient-uid',
                'doctor_firebase_uid': 'test-doctor-uid-123',
                'medications': json.dumps([{'name': 'Amoxicillin', 'dosage': '500mg'}]),
                'issued_date': '2025-10-30'
            }]
        )
        
        # Mock prescription update (for hash)
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = Mock()
        
        response = client.post(
            '/api/prescriptions/generate-qr',
            json={
                'ai_diagnosis_id': 'test-diagnosis-123',
                'modified_prescription': 'Amoxicillin 500mg, 3 times daily'
            },
            headers={'Authorization': 'Bearer test-token'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'qr_code' in data['data']
        assert 'verification_hash' in data['data']
        assert 'prescription_id' in data['data']
        assert data['data']['qr_code'].startswith('data:image/png;base64,')


class TestVerifyPrescriptionEndpoint:
    """Test /api/prescriptions/verify endpoint"""
    
    def test_missing_required_fields(self, client):
        """Test verification requires prescription_id and hash"""
        response = client.post('/api/prescriptions/verify', json={})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'missing' in data['error'].lower()
    
    def test_prescription_not_found(self, client):
        """Test verification fails for non-existent prescription"""
        with patch('prescription_qr_routes.supabase') as mock_supabase:
            mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
                data=None
            )
            
            response = client.post(
                '/api/prescriptions/verify',
                json={
                    'prescription_id': 'non-existent-id',
                    'hash': 'fake-hash'
                }
            )
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['verified'] is False
    
    @patch('prescription_qr_routes.supabase')
    def test_invalid_hash(self, mock_supabase, client):
        """Test verification fails for invalid hash"""
        prescription_data = {
            'id': 'test-prescription-123',
            'prescription_number': 'RX-20251030-TEST',
            'patient_firebase_uid': 'patient-uid',
            'doctor_firebase_uid': 'doctor-uid',
            'medications': json.dumps([{'name': 'Amoxicillin'}]),
            'verification_hash': 'correct-hash-abc123',
            'issued_date': '2025-10-30',
            'status': 'active'
        }
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
            data=prescription_data
        )
        
        response = client.post(
            '/api/prescriptions/verify',
            json={
                'prescription_id': 'test-prescription-123',
                'hash': 'wrong-hash-xyz789'
            }
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['verified'] is False
        assert 'tampered' in data['error'].lower() or 'invalid' in data['error'].lower()
    
    @patch('prescription_qr_routes.supabase')
    def test_successful_verification(self, mock_supabase, client):
        """Test successful prescription verification"""
        # Create prescription with known hash
        prescription_data = {
            'id': 'test-prescription-123',
            'prescription_number': 'RX-20251030-TEST',
            'patient_firebase_uid': 'patient-uid',
            'doctor_firebase_uid': 'doctor-uid',
            'medications': json.dumps([{'name': 'Amoxicillin', 'dosage': '500mg'}]),
            'issued_date': '2025-10-30',
            'status': 'active',
            'instructions': 'Take with food'
        }
        
        # Generate the expected hash
        expected_hash = generate_prescription_hash(prescription_data)
        prescription_data['verification_hash'] = expected_hash
        
        # Mock Supabase responses
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
            data=prescription_data
        )
        
        # Mock doctor info
        doctor_mock = Mock()
        doctor_mock.data = {'full_name': 'Dr. Test', 'email': 'doctor@test.com'}
        
        # Mock patient info
        patient_mock = Mock()
        patient_mock.data = {'full_name': 'John Doe'}
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = [
            Mock(data=prescription_data),  # First call for prescription
            doctor_mock,  # Second call for doctor
            patient_mock  # Third call for patient
        ]
        
        response = client.post(
            '/api/prescriptions/verify',
            json={
                'prescription_id': 'test-prescription-123',
                'hash': expected_hash
            }
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['verified'] is True
        assert 'prescription_number' in data['data']
        assert 'doctor_name' in data['data']
        assert 'medications' in data['data']


class TestQRImageEndpoint:
    """Test /api/prescriptions/<id>/qr-image endpoint"""
    
    def test_prescription_not_found(self, client):
        """Test returns 404 for non-existent prescription"""
        with patch('prescription_qr_routes.supabase') as mock_supabase:
            mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
                data=None
            )
            
            response = client.get('/api/prescriptions/fake-id/qr-image')
            
            assert response.status_code == 404
    
    @patch('prescription_qr_routes.supabase')
    def test_qr_not_generated(self, mock_supabase, client):
        """Test returns 404 when QR code doesn't exist"""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
            data={'id': 'test-id', 'qr_code_data': None}
        )
        
        response = client.get('/api/prescriptions/test-id/qr-image')
        
        assert response.status_code == 404
    
    @patch('prescription_qr_routes.supabase')
    def test_successful_image_retrieval(self, mock_supabase, client):
        """Test successful QR image retrieval"""
        qr_data = json.dumps({
            'type': 'prescription',
            'id': 'test-id-123',
            'hash': 'abc123'
        })
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = Mock(
            data={'qr_code_data': qr_data}
        )
        
        response = client.get('/api/prescriptions/test-id-123/qr-image')
        
        assert response.status_code == 200
        assert response.content_type == 'image/png'
        assert len(response.data) > 0
        # PNG files start with these bytes
        assert response.data[:4] == b'\x89PNG'


class TestSecurityFeatures:
    """Test security aspects of QR code system"""
    
    def test_hash_length(self):
        """Test hash is appropriate length for security"""
        prescription_data = {
            'id': 'test-id',
            'prescription_number': 'RX-123',
            'patient_firebase_uid': 'patient',
            'doctor_firebase_uid': 'doctor',
            'medications': '[]'
        }
        
        hash_value = generate_prescription_hash(prescription_data)
        # SHA-256 produces 256 bits = 64 hex characters
        assert len(hash_value) == 64
    
    def test_hash_deterministic(self):
        """Test hash is deterministic (same input = same output)"""
        prescription_data = {
            'id': 'test-id',
            'prescription_number': 'RX-123',
            'patient_firebase_uid': 'patient',
            'doctor_firebase_uid': 'doctor',
            'medications': json.dumps([{'name': 'Test'}])
        }
        
        hashes = [generate_prescription_hash(prescription_data) for _ in range(10)]
        assert all(h == hashes[0] for h in hashes)
    
    def test_medication_order_affects_hash(self):
        """Test that medication order is normalized in hash"""
        prescription_data1 = {
            'id': 'test-id',
            'prescription_number': 'RX-123',
            'patient_firebase_uid': 'patient',
            'doctor_firebase_uid': 'doctor',
            'medications': json.dumps([{'name': 'A'}, {'name': 'B'}])
        }
        
        prescription_data2 = prescription_data1.copy()
        prescription_data2['medications'] = json.dumps([{'name': 'B'}, {'name': 'A'}])
        
        hash1 = generate_prescription_hash(prescription_data1)
        hash2 = generate_prescription_hash(prescription_data2)
        
        # Should be different because order matters in the JSON string
        assert hash1 != hash2


class TestErrorHandling:
    """Test error handling in QR routes"""
    
    @patch('prescription_qr_routes.firebase_auth_service')
    def test_auth_service_error(self, mock_auth, client):
        """Test handling of authentication service errors"""
        mock_auth.verify_token.side_effect = Exception("Auth service down")
        
        response = client.post(
            '/api/prescriptions/generate-qr',
            json={'ai_diagnosis_id': 'test'},
            headers={'Authorization': 'Bearer test-token'}
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
    
    @patch('prescription_qr_routes.supabase')
    @patch('prescription_qr_routes.firebase_auth_service')
    def test_database_error(self, mock_auth, mock_supabase, client):
        """Test handling of database errors"""
        mock_auth.verify_token.return_value = {'success': True, 'uid': 'test-uid'}
        mock_supabase.table.return_value.select.side_effect = Exception("Database error")
        
        response = client.post(
            '/api/prescriptions/generate-qr',
            json={'ai_diagnosis_id': 'test'},
            headers={'Authorization': 'Bearer test-token'}
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
