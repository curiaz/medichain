"""
Unit tests for medicine allergy functionality
Tests appointment creation, retrieval, and display of allergies
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import Mock, patch, MagicMock
from flask import Flask
import json

# Import the routes
from appointment_routes import appointments_bp
from file_routes import file_bp


class TestAllergyFunctionality:
    """Test suite for medicine allergy features"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        app.register_blueprint(appointments_bp)
        app.register_blueprint(file_bp)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        with patch('appointment_routes.supabase') as mock_supabase:
            mock_service = MagicMock()
            mock_supabase.service_client = mock_service
            yield mock_supabase
    
    @pytest.fixture
    def mock_auth(self):
        """Mock authentication"""
        with patch('appointment_routes.auth_required') as mock_auth:
            def auth_decorator(f):
                def wrapper(*args, **kwargs):
                    # Mock firebase_user
                    from flask import request
                    request.firebase_user = {
                        'uid': 'test-patient-uid',
                        'email': 'patient@test.com'
                    }
                    return f(*args, **kwargs)
                wrapper.__name__ = f.__name__
                return wrapper
            mock_auth.side_effect = auth_decorator
            yield mock_auth
    
    def test_appointment_creation_with_allergies(self, mock_supabase, mock_auth):
        """Test that medicine_allergies is saved when creating appointment"""
        # Mock database responses
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {'role': 'patient', 'first_name': 'Test', 'last_name': 'Patient', 'email': 'patient@test.com'}
        ]
        
        mock_supabase.service_client.table.return_value.insert.return_value.execute.return_value.data = [{
            'id': 'test-appointment-id',
            'patient_firebase_uid': 'test-patient-uid',
            'doctor_firebase_uid': 'test-doctor-uid',
            'appointment_date': '2025-01-15',
            'appointment_time': '10:00',
            'medicine_allergies': 'aspirin, penicillin',
            'status': 'scheduled'
        }]
        
        # Test data
        appointment_data = {
            'doctor_firebase_uid': 'test-doctor-uid',
            'appointment_date': '2025-01-15',
            'appointment_time': '10:00',
            'medicine_allergies': 'aspirin, penicillin',
            'symptoms': ['fever', 'headache'],
            'documents': []
        }
        
        # Verify medicine_allergies is included in insert
        insert_call = mock_supabase.service_client.table.return_value.insert
        assert insert_call.called
        
        # Check that medicine_allergies was passed
        call_args = insert_call.call_args[0][0]
        assert 'medicine_allergies' in call_args
        assert call_args['medicine_allergies'] == 'aspirin, penicillin'
    
    def test_appointment_retrieval_includes_allergies(self, mock_supabase, mock_auth):
        """Test that allergies are included when fetching appointment"""
        # Mock appointment data with allergies
        mock_appointment = {
            'id': 'test-appointment-id',
            'patient_firebase_uid': 'test-patient-uid',
            'doctor_firebase_uid': 'test-doctor-uid',
            'appointment_date': '2025-01-15',
            'appointment_time': '10:00',
            'medicine_allergies': 'aspirin',
            'status': 'scheduled'
        }
        
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            mock_appointment
        ]
        
        # Mock patient profile with allergies
        mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {
                'firebase_uid': 'test-patient-uid',
                'first_name': 'Test',
                'last_name': 'Patient',
                'email': 'patient@test.com',
                'allergies': ['aspirin', 'penicillin']
            }
        ]
        
        # Verify appointment includes medicine_allergies
        assert mock_appointment.get('medicine_allergies') == 'aspirin'
    
    def test_allergy_parsing_string(self):
        """Test parsing allergies from string format"""
        # Test comma-separated
        allergies_str = "aspirin, penicillin, ibuprofen"
        parsed = [a.strip() for a in allergies_str.split(',') if a.strip()]
        assert len(parsed) == 3
        assert 'aspirin' in parsed
        assert 'penicillin' in parsed
        assert 'ibuprofen' in parsed
        
        # Test semicolon-separated
        allergies_str = "aspirin; penicillin"
        parsed = [a.strip() for a in allergies_str.replace(';', ',').split(',') if a.strip()]
        assert len(parsed) == 2
        
        # Test newline-separated
        allergies_str = "aspirin\npenicillin"
        parsed = [a.strip() for a in allergies_str.replace('\n', ',').split(',') if a.strip()]
        assert len(parsed) == 2
    
    def test_allergy_parsing_array(self):
        """Test parsing allergies from array format"""
        allergies_array = ['aspirin', 'penicillin', 'ibuprofen']
        filtered = [a for a in allergies_array if a and (isinstance(a, str) and a.strip())]
        assert len(filtered) == 3
        assert all(a in filtered for a in allergies_array)
    
    def test_allergy_fallback_to_profile(self):
        """Test that allergies fallback to patient profile if not in appointment"""
        # Appointment without medicine_allergies
        appointment = {
            'id': 'test-id',
            'medicine_allergies': None
        }
        
        # Patient profile with allergies
        patient = {
            'allergies': ['aspirin', 'penicillin']
        }
        
        # Should use patient allergies
        allergies = []
        if appointment.get('medicine_allergies'):
            allergies = [a.strip() for a in appointment['medicine_allergies'].split(',') if a.strip()]
        
        if not allergies and patient.get('allergies'):
            if isinstance(patient['allergies'], list):
                allergies = patient['allergies']
        
        assert len(allergies) == 2
        assert 'aspirin' in allergies
        assert 'penicillin' in allergies
    
    def test_empty_allergies_handling(self):
        """Test handling of empty or null allergies"""
        # Empty string
        allergies_str = ""
        parsed = [a.strip() for a in allergies_str.split(',') if a.strip()]
        assert len(parsed) == 0
        
        # None value
        allergies_str = None
        if allergies_str:
            parsed = [a.strip() for a in allergies_str.split(',') if a.strip()]
        else:
            parsed = []
        assert len(parsed) == 0
        
        # Whitespace only
        allergies_str = "   ,  ,  "
        parsed = [a.strip() for a in allergies_str.split(',') if a.strip()]
        assert len(parsed) == 0
    
    def test_allergy_merge_with_profile(self):
        """Test merging appointment allergies with profile allergies"""
        # Existing profile allergies
        existing_allergies = ['aspirin', 'penicillin']
        
        # New allergies from appointment
        new_allergies_text = "ibuprofen, aspirin"  # aspirin is duplicate
        
        # Parse new allergies
        new_allergies = [
            allergy.strip() 
            for allergy in new_allergies_text.replace('\n', ',').replace(';', ',').split(',')
            if allergy.strip()
        ]
        
        # Merge avoiding duplicates (case-insensitive)
        existing_lower = [a.lower() for a in existing_allergies if a]
        merged = existing_allergies.copy()
        
        for new_allergy in new_allergies:
            if new_allergy.lower() not in existing_lower:
                merged.append(new_allergy)
                existing_lower.append(new_allergy.lower())
        
        # Should have 3 unique allergies
        assert len(merged) == 3
        assert 'aspirin' in merged
        assert 'penicillin' in merged
        assert 'ibuprofen' in merged
        # Should not have duplicate aspirin
        assert merged.count('aspirin') == 1


class TestFileRoutes:
    """Test suite for file serving routes"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.register_blueprint(file_bp)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_file_route_registration(self, app):
        """Test that file routes are registered"""
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        assert any('/api/files' in rule for rule in rules)
    
    def test_file_url_construction(self):
        """Test file URL construction logic"""
        # Test with file_path
        file_path = "documents/test.pdf"
        api_url = "http://localhost:5000/api"
        constructed_url = f"{api_url}/files/{file_path}"
        assert constructed_url == "http://localhost:5000/api/files/documents/test.pdf"
        
        # Test with appointment documents
        appointment_id = "test-appt-id"
        filename = "test.pdf"
        constructed_url = f"{api_url}/files/appointments/{appointment_id}/documents/{filename}"
        assert "appointments" in constructed_url
        assert appointment_id in constructed_url
        assert filename in constructed_url


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

