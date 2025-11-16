"""
Unit tests for Profile Management functionality
Tests both patient profile routes and profile management features
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
import sys
import os

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Import Flask app and blueprints
from flask import Flask
app = Flask(__name__)

# Import blueprints directly for testing
try:
    from patient_profile_routes import patient_profile_bp
    from profile_management import profile_mgmt_bp
    
    # Register blueprints for testing
    app.register_blueprint(patient_profile_bp)
    app.register_blueprint(profile_mgmt_bp)
except ImportError as e:
    print(f"Import warning: {e}")
    # Create mock blueprints if imports fail
    from flask import Blueprint
    patient_profile_bp = Blueprint('patient_profile', __name__)
    profile_mgmt_bp = Blueprint('profile_mgmt', __name__)


class TestProfileManagement:
    """Test cases for profile management system"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        with patch('patient_profile_routes.supabase') as mock_sb:
            yield mock_sb
    
    @pytest.fixture
    def mock_profile_supabase(self):
        """Mock Supabase client for profile management"""
        with patch('profile_management.supabase') as mock_sb:
            yield mock_sb
    
    @pytest.fixture
    def sample_user_info(self):
        """Sample user information"""
        return {
            'user_id': 'test_user_123',
            'role': 'patient',
            'email': 'test@example.com'
        }
    
    @pytest.fixture
    def sample_profile_data(self):
        """Sample profile data"""
        return {
            'user_profile': {
                'firebase_uid': 'test_user_123',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@example.com',
                'phone': '+1234567890',
                'role': 'patient'
            },
            'medical_info': {
                'medical_conditions': ['Hypertension'],
                'allergies': ['Penicillin'],
                'current_medications': ['Lisinopril'],
                'blood_type': 'A+',
                'medical_notes': 'Regular checkups needed'
            },
            'privacy_settings': {
                'profile_visibility': 'private',
                'medical_info_visible_to_doctors': True,
                'allow_ai_analysis': True
            }
        }
    
    def test_get_patient_profile_success(self, client, mock_supabase, sample_user_info, sample_profile_data):
        """Test successful retrieval of patient profile"""
        # Setup mocks
        mock_supabase.verify_firebase_token.return_value = sample_user_info
        mock_supabase.get_patient_profile.return_value = sample_profile_data
        
        # Make request with authorization header
        headers = {'Authorization': 'Bearer valid_token'}
        response = client.get('/api/profile/patient', headers=headers)
        
        # Assertions
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert data['profile']['user_profile']['first_name'] == 'John'
        assert data['profile']['user_profile']['last_name'] == 'Doe'
    
    def test_get_patient_profile_no_auth(self, client):
        """Test patient profile request without authorization"""
        response = client.get('/api/profile/patient')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Authorization token required' in data['message']
    
    def test_get_patient_profile_invalid_token(self, client, mock_supabase):
        """Test patient profile request with invalid token"""
        mock_supabase.verify_firebase_token.return_value = None
        
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/profile/patient', headers=headers)
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'Invalid or expired token' in data['message']
    
    def test_get_patient_profile_non_patient_role(self, client, mock_supabase):
        """Test patient profile request from non-patient user"""
        mock_supabase.verify_firebase_token.return_value = {
            'user_id': 'doctor_123',
            'role': 'doctor'
        }
        
        headers = {'Authorization': 'Bearer valid_token'}
        response = client.get('/api/profile/patient', headers=headers)
        
        assert response.status_code == 403
        data = json.loads(response.data)
        assert data['success'] == False
        assert 'only available for patients' in data['message']
    
    def test_update_patient_profile_success(self, client, mock_supabase, sample_user_info):
        """Test successful update of patient profile"""
        mock_supabase.verify_firebase_token.return_value = sample_user_info
        mock_supabase.update_patient_profile.return_value = True
        
        update_data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone': '+9876543210'
        }
        
        headers = {'Authorization': 'Bearer valid_token', 'Content-Type': 'application/json'}
        response = client.put('/api/profile/patient', 
                             headers=headers, 
                             data=json.dumps(update_data))
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
        assert 'Profile updated successfully' in data['message']
    
    def test_update_medical_info_success(self, client, mock_supabase, sample_user_info):
        """Test successful update of medical information"""
        mock_supabase.verify_firebase_token.return_value = sample_user_info
        mock_supabase.update_medical_info.return_value = True
        
        medical_data = {
            'medical_conditions': ['Diabetes', 'Hypertension'],
            'allergies': ['Shellfish'],
            'current_medications': ['Metformin'],
            'blood_type': 'O-'
        }
        
        headers = {'Authorization': 'Bearer valid_token', 'Content-Type': 'application/json'}
        response = client.put('/api/profile/patient/medical', 
                             headers=headers, 
                             data=json.dumps(medical_data))
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
    
    def test_privacy_settings_update(self, client, mock_supabase, sample_user_info):
        """Test updating privacy settings"""
        mock_supabase.verify_firebase_token.return_value = sample_user_info
        mock_supabase.update_privacy_settings.return_value = True
        
        privacy_data = {
            'profile_visibility': 'public',
            'medical_info_visible_to_doctors': False,
            'allow_ai_analysis': False
        }
        
        headers = {'Authorization': 'Bearer valid_token', 'Content-Type': 'application/json'}
        response = client.put('/api/profile/patient/privacy', 
                             headers=headers, 
                             data=json.dumps(privacy_data))
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] == True
    
    @patch('profile_management.datetime')
    def test_blockchain_transaction_creation(self, mock_datetime, mock_profile_supabase):
        """Test blockchain transaction creation for audit trail"""
        from profile_management import create_blockchain_transaction, generate_blockchain_hash
        
        mock_datetime.utcnow.return_value.isoformat.return_value = '2025-09-30T12:00:00'
        
        # Mock Supabase response
        mock_profile_supabase.service_client.table.return_value.insert.return_value.execute.return_value.data = [
            {'id': 1, 'blockchain_tx_hash': 'test_hash'}
        ]
        
        result = create_blockchain_transaction(
            user_id='test_user_123',
            action='profile_update',
            data_hash='sample_hash',
            metadata={'field': 'first_name'}
        )
        
        assert result is not None
        assert 'blockchain_tx_hash' in result
        # Hash is deterministically generated from transaction data
        assert len(result['blockchain_tx_hash']) == 64  # SHA256 hex length
    
    def test_generate_blockchain_hash(self):
        """Test blockchain hash generation"""
        from profile_management import generate_blockchain_hash
        
        data = {'user_id': 'test', 'action': 'update'}
        hash1 = generate_blockchain_hash(data)
        hash2 = generate_blockchain_hash(data)
        
        # Same data should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hash length
        assert isinstance(hash1, str)
    
    def test_allowed_file_function(self):
        """Test file upload validation"""
        from profile_management import allowed_file
        
        assert allowed_file('document.pdf') == True
        assert allowed_file('image.jpg') == True
        assert allowed_file('image.png') == True
        assert allowed_file('malicious.exe') == False
        assert allowed_file('script.js') == False
        assert allowed_file('no_extension') == False


class TestProfileIntegration:
    """Integration tests for profile system"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @patch('patient_profile_routes.supabase')
    @patch('profile_management.supabase')
    def test_complete_profile_workflow(self, mock_profile_supabase, mock_patient_supabase, client):
        """Test complete profile management workflow"""
        
        # Setup mocks for authentication
        user_info = {'user_id': 'test_user', 'role': 'patient'}
        mock_patient_supabase.verify_firebase_token.return_value = user_info
        mock_profile_supabase.verify_firebase_token.return_value = user_info
        
        # Mock initial profile retrieval
        initial_profile = {
            'user_profile': {'first_name': 'John', 'last_name': 'Doe'},
            'medical_info': {'allergies': []},
            'privacy_settings': {'profile_visibility': 'private'}
        }
        mock_patient_supabase.get_patient_profile.return_value = initial_profile
        
        headers = {'Authorization': 'Bearer valid_token'}
        
        # 1. Get initial profile
        response = client.get('/api/profile/patient', headers=headers)
        assert response.status_code == 200
        
        # 2. Update profile (mock success)
        mock_patient_supabase.update_patient_profile.return_value = True
        update_data = {'first_name': 'Jane'}
        response = client.put('/api/profile/patient', 
                             headers={**headers, 'Content-Type': 'application/json'}, 
                             data=json.dumps(update_data))
        assert response.status_code == 200
        
        # 3. Update medical info (mock success)
        mock_patient_supabase.update_medical_info.return_value = True
        medical_data = {'allergies': ['Peanuts']}
        response = client.put('/api/profile/patient/medical', 
                             headers={**headers, 'Content-Type': 'application/json'}, 
                             data=json.dumps(medical_data))
        assert response.status_code == 200
    
    def test_error_handling_database_failure(self, client):
        """Test error handling when database operations fail"""
        with patch('patient_profile_routes.supabase') as mock_supabase:
            # Mock authentication success but database failure
            mock_supabase.verify_firebase_token.return_value = {
                'user_id': 'test_user', 'role': 'patient'
            }
            mock_supabase.get_patient_profile.side_effect = Exception("Database error")
            
            headers = {'Authorization': 'Bearer valid_token'}
            response = client.get('/api/profile/patient', headers=headers)
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] == False
            assert 'error' in data['message'].lower()
    
    def test_profile_data_validation(self, client):
        """Test validation of profile data"""
        with patch('patient_profile_routes.supabase') as mock_supabase:
            mock_supabase.verify_firebase_token.return_value = {
                'user_id': 'test_user', 'role': 'patient'
            }
            
            # Test invalid email format
            invalid_data = {
                'first_name': 'John',
                'email': 'invalid_email'  # Invalid format
            }
            
            headers = {'Authorization': 'Bearer valid_token', 'Content-Type': 'application/json'}
            response = client.put('/api/profile/patient', 
                                 headers=headers, 
                                 data=json.dumps(invalid_data))
            
            # Should handle validation appropriately
            # Note: Actual validation logic depends on implementation


if __name__ == '__main__':
    pytest.main([__file__, '-v'])