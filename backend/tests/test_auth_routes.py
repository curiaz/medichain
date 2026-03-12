"""
Unit tests for auth routes (auth/auth_routes.py)
Tests authentication, signup, login, and password reset functionality
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


class TestAuthRoutes:
    """Test cases for authentication routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Mock supabase initialization
        with patch('auth.auth_routes.supabase') as mock_supabase:
            # Import and register blueprint
            from auth.auth_routes import auth_bp
            app.register_blueprint(auth_bp)
            
            with app.test_client() as client:
                yield client
    
    @pytest.fixture
    def mock_supabase_client(self):
        """Mock Supabase client"""
        with patch('auth.auth_routes.supabase') as mock_supabase:
            mock_client = MagicMock()
            mock_table = MagicMock()
            mock_client.table.return_value = mock_table
            mock_supabase.client = mock_client
            mock_table.select.return_value = mock_table
            mock_table.insert.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.execute.return_value = Mock(data=None, error=None)
            
            yield mock_supabase
    
    def test_validate_password_weak(self):
        """Test password validation with weak passwords"""
        from auth.auth_routes import validate_password
        
        assert validate_password("short") is not None
        assert validate_password("NOLOWERCASE123") is not None
        assert validate_password("nouppercase123") is not None
        assert validate_password("NoDigits") is not None
    
    def test_validate_password_strong(self):
        """Test password validation with strong passwords"""
        from auth.auth_routes import validate_password
        
        assert validate_password("Strong123") is None
        assert validate_password("ValidPass1") is None
    
    @patch('auth.auth_routes.supabase')
    @patch('auth.auth_routes.auth_utils')
    @patch('email_validator.validate_email')
    def test_signup_success(self, mock_validate, mock_auth_utils, mock_supabase, client):
        """Test successful user signup"""
        # Setup mocks
        mock_validate.return_value = MagicMock(email='test@test.com')
        
        mock_table = MagicMock()
        mock_supabase.client.table.return_value = mock_table
        
        # Create separate mock chains for different operations
        # First call: check existing user - select().eq().execute() - return empty
        check_execute = MagicMock()
        check_execute.execute.return_value.data = []  # No existing user
        check_eq = MagicMock()
        check_eq.execute.return_value = check_execute.execute.return_value
        check_select = MagicMock()
        check_select.eq.return_value = check_eq
        mock_table.select.return_value = check_select
        mock_table.eq.return_value = check_eq
        
        # Second call: insert new user - insert().execute() - return success  
        insert_execute = MagicMock()
        insert_execute.execute.return_value.data = [{
            'id': 1,
            'email': 'test@test.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'patient'
        }]
        insert_chain = MagicMock()
        insert_chain.execute.return_value = insert_execute.execute.return_value
        mock_table.insert.return_value = insert_chain
        
        mock_auth_utils.hash_password.return_value = 'hashed_password'
        mock_auth_utils.generate_token.return_value = 'test_token'
        
        response = client.post('/api/auth/signup',
                              data=json.dumps({
                                  'email': 'test@test.com',
                                  'password': 'Strong123',
                                  'name': 'John Doe',
                                  'role': 'patient'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'token' in data['data']
    
    @patch('auth.auth_routes.supabase')
    def test_signup_missing_fields(self, mock_supabase, client):
        """Test signup with missing required fields"""
        response = client.post('/api/auth/signup',
                              data=json.dumps({
                                  'email': 'test@example.com'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    @patch('auth.auth_routes.supabase')
    @patch('email_validator.validate_email')
    def test_signup_invalid_email(self, mock_validate, mock_supabase, client):
        """Test signup with invalid email"""
        from email_validator import EmailNotValidError
        mock_validate.side_effect = EmailNotValidError("Invalid email")
        
        response = client.post('/api/auth/signup',
                              data=json.dumps({
                                  'email': 'invalid-email',
                                  'password': 'Strong123',
                                  'name': 'Test User',
                                  'role': 'patient'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    @patch('auth.auth_routes.supabase')
    @patch('email_validator.validate_email')
    def test_signup_invalid_role(self, mock_validate, mock_supabase, client):
        """Test signup with invalid role"""
        mock_validate.return_value = MagicMock(email='test@test.com')
        
        response = client.post('/api/auth/signup',
                              data=json.dumps({
                                  'email': 'test@test.com',
                                  'password': 'Strong123',
                                  'name': 'Test User',
                                  'role': 'invalid_role'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'role' in data['error'].lower()
    
    @patch('auth.auth_routes.supabase')
    @patch('email_validator.validate_email')
    def test_signup_existing_user(self, mock_validate, mock_supabase, client):
        """Test signup with existing email"""
        mock_validate.return_value = MagicMock(email='existing@test.com')
        
        mock_table = MagicMock()
        mock_supabase.client.table.return_value = mock_table
        mock_table.eq.return_value.execute.return_value.data = [{
            'email': 'existing@test.com'
        }]
        
        response = client.post('/api/auth/signup',
                              data=json.dumps({
                                  'email': 'existing@test.com',
                                  'password': 'Strong123',
                                  'name': 'Test User',
                                  'role': 'patient'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_require_auth_decorator_missing_token(self, client):
        """Test require_auth decorator with missing token"""
        from auth.auth_routes import require_auth
        
        @require_auth
        def protected_route():
            return {'success': True}
        
        # Create a mock request without Authorization header
        from flask import request
        with client.application.test_request_context():
            # Manually set request headers
            request.headers = {}
            result = protected_route()
            
            assert isinstance(result, tuple)
            response_data, status_code = result
            assert status_code == 401


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
