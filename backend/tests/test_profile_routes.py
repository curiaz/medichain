"""
Unit tests for Profile Routes API
Tests doctor and patient profile management endpoints
These tests verify the actual implementation behavior
"""
import pytest
import json
from flask import Flask

# Add backend to path
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


class TestProfileRoutes:
    """Test cases for profile routes"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Register profile blueprint
        from profile_routes import profile_bp
        app.register_blueprint(profile_bp)
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    def test_update_doctor_profile_missing_token(self, client):
        """Test profile update without token - should return 401"""
        response = client.put(
            '/api/profile/doctor/update',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'first_name': 'Jane'})
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data or 'details' in data
    
    def test_get_doctor_profile_missing_token(self, client):
        """Test getting doctor profile without token - should return 401"""
        response = client.get('/api/profile/doctor/details')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_documents_missing_token(self, client):
        """Test getting documents without token - should return 401"""
        response = client.get('/api/profile/doctor/documents')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_upload_document_missing_token(self, client):
        """Test uploading document without token - should return 401"""
        response = client.post(
            '/api/profile/doctor/documents/upload',
            headers={'Content-Type': 'multipart/form-data'}
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_update_privacy_missing_token(self, client):
        """Test updating privacy settings without token - should return 401"""
        response = client.put(
            '/api/profile/doctor/privacy',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'profile_visibility': 'private'})
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_activity_missing_token(self, client):
        """Test getting activity log without token - should return 401"""
        response = client.get('/api/profile/doctor/activity')
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_invalid_json_format(self, client):
        """Test with invalid JSON format"""
        response = client.put(
            '/api/profile/doctor/update',
            headers={
                'Authorization': 'Bearer test-token',
                'Content-Type': 'application/json'
            },
            data='invalid json'
        )
        
        # Should handle invalid JSON gracefully
        assert response.status_code in [400, 401, 500]
    
    def test_missing_content_type(self, client):
        """Test without Content-Type header"""
        response = client.put(
            '/api/profile/doctor/update',
            headers={'Authorization': 'Bearer test-token'},
            data=json.dumps({'first_name': 'Jane'})
        )
        
        # Should handle missing content type
        assert response.status_code in [400, 401, 415]
    
    def test_empty_request_body(self, client):
        """Test with empty request body"""
        response = client.put(
            '/api/profile/doctor/update',
            headers={
                'Authorization': 'Bearer test-token',
                'Content-Type': 'application/json'
            },
            data=json.dumps({})
        )
        
        # Should handle empty body - may return 401 (auth) or 400 (validation)
        assert response.status_code in [400, 401]
