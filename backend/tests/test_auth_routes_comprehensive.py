"""
Comprehensive unit tests for Authentication Routes
Tests login, signup, password reset, and token verification
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

# Add backend to path
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


class TestAuthRoutes:
    """Test cases for authentication routes"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app for testing"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        
        # Register auth blueprint
        with patch('auth.auth_routes.supabase') as mock_supabase:
            from auth.auth_routes import auth_bp
            app.register_blueprint(auth_bp)
            yield app
    
    @pytest.fixture
    def client(self, app):
        """Create test client"""
        return app.test_client()
    
    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client"""
        mock = MagicMock()
        mock.service_client = MagicMock()
        mock.service_client.table.return_value = MagicMock()
        return mock
    
    @pytest.fixture
    def mock_firebase_auth(self):
        """Mock Firebase auth"""
        mock = MagicMock()
        mock.get_user.return_value = Mock(uid='test-uid', email='test@test.com')
        mock.create_user.return_value = Mock(uid='new-uid', email='new@test.com')
        return mock
    
    def test_login_success(self, client, mock_supabase, mock_firebase_auth):
        """Test successful login"""
        with patch('auth.auth_routes.supabase', mock_supabase):
            with patch('auth.auth_routes.firebase_auth_service', mock_firebase_auth):
                # Mock user lookup
                mock_table = MagicMock()
                mock_table.select.return_value = mock_table
                mock_table.eq.return_value = mock_table
                mock_table.single.return_value = mock_table
                mock_table.execute.return_value = Mock(data={
                    'id': 'user-123',
                    'email': 'test@test.com',
                    'role': 'doctor',
                    'first_name': 'John',
                    'last_name': 'Doe'
                }, error=None)
                mock_supabase.service_client.table.return_value = mock_table
                
                # Mock token generation
                with patch('auth.auth_utils.auth_utils.generate_token') as mock_token:
                    mock_token.return_value = 'test-jwt-token'
                    
                    login_data = {
                        'email': 'test@test.com',
                        'password': 'password123'
                    }
                    
                    response = client.post(
                        '/api/auth/login',
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(login_data)
                    )
                    
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert data['success'] is True
                    assert 'token' in data
                    assert 'user' in data
    
    def test_login_invalid_credentials(self, client, mock_firebase_auth):
        """Test login with invalid credentials"""
        with patch('auth.auth_routes.firebase_auth_service', mock_firebase_auth):
            mock_firebase_auth.get_user_by_email.side_effect = Exception('Invalid credentials')
            
            login_data = {
                'email': 'wrong@test.com',
                'password': 'wrongpassword'
            }
            
            response = client.post(
                '/api/auth/login',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(login_data)
            )
            
            assert response.status_code in [400, 401]
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_signup_success(self, client, mock_supabase, mock_firebase_auth):
        """Test successful user signup"""
        with patch('auth.auth_routes.supabase', mock_supabase):
            with patch('auth.auth_routes.firebase_auth_service', mock_firebase_auth):
                # Mock user creation
                mock_firebase_auth.create_user.return_value = Mock(
                    uid='new-uid-123',
                    email='newuser@test.com'
                )
                
                # Mock profile creation
                mock_table = MagicMock()
                mock_table.insert.return_value = mock_table
                mock_table.execute.return_value = Mock(data=[{
                    'id': 'user-123',
                    'email': 'newuser@test.com'
                }], error=None)
                mock_supabase.service_client.table.return_value = mock_table
                
                # Mock token generation
                with patch('auth.auth_utils.auth_utils.generate_token') as mock_token:
                    mock_token.return_value = 'test-jwt-token'
                    
                    signup_data = {
                        'email': 'newuser@test.com',
                        'password': 'password123',
                        'first_name': 'Jane',
                        'last_name': 'Smith',
                        'role': 'patient'
                    }
                    
                    response = client.post(
                        '/api/auth/signup',
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(signup_data)
                    )
                    
                    assert response.status_code == 201
                    data = json.loads(response.data)
                    assert data['success'] is True
                    assert 'token' in data
                    assert 'user' in data
    
    def test_signup_duplicate_email(self, client, mock_firebase_auth):
        """Test signup with duplicate email"""
        with patch('auth.auth_routes.firebase_auth_service', mock_firebase_auth):
            mock_firebase_auth.get_user_by_email.return_value = Mock(
                uid='existing-uid',
                email='existing@test.com'
            )
            
            signup_data = {
                'email': 'existing@test.com',
                'password': 'password123',
                'first_name': 'Jane',
                'last_name': 'Smith'
            }
            
            response = client.post(
                '/api/auth/signup',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(signup_data)
            )
            
            assert response.status_code in [400, 409]
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_password_reset_request(self, client, mock_supabase, mock_firebase_auth):
        """Test password reset request"""
        with patch('auth.auth_routes.supabase', mock_supabase):
            with patch('auth.auth_routes.firebase_auth_service', mock_firebase_auth):
                # Mock user lookup
                mock_table = MagicMock()
                mock_table.select.return_value = mock_table
                mock_table.eq.return_value = mock_table
                mock_table.single.return_value = mock_table
                mock_table.execute.return_value = Mock(data={
                    'id': 'user-123',
                    'email': 'test@test.com'
                }, error=None)
                mock_supabase.service_client.table.return_value = mock_table
                
                # Mock OTP service
                with patch('auth.auth_routes.otp_service') as mock_otp:
                    mock_otp.generate_otp.return_value = '123456'
                    mock_otp.store_otp.return_value = True
                    
                    reset_data = {
                        'email': 'test@test.com'
                    }
                    
                    response = client.post(
                        '/api/auth/reset-password',
                        headers={'Content-Type': 'application/json'},
                        data=json.dumps(reset_data)
                    )
                    
                    assert response.status_code in [200, 201]
                    data = json.loads(response.data)
                    assert data['success'] is True
    
    def test_password_reset_verify_otp(self, client, mock_supabase):
        """Test OTP verification for password reset"""
        with patch('auth.auth_routes.supabase', mock_supabase):
            # Mock OTP service
            with patch('auth.auth_routes.otp_service') as mock_otp:
                mock_otp.verify_otp.return_value = True
                
                verify_data = {
                    'email': 'test@test.com',
                    'otp': '123456'
                }
                
                response = client.post(
                    '/api/auth/verify-otp',
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps(verify_data)
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
    
    def test_password_reset_verify_otp_invalid(self, client):
        """Test OTP verification with invalid OTP"""
        with patch('auth.auth_routes.otp_service') as mock_otp:
            mock_otp.verify_otp.return_value = False
            
            verify_data = {
                'email': 'test@test.com',
                'otp': 'wrong-otp'
            }
            
            response = client.post(
                '/api/auth/verify-otp',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(verify_data)
            )
            
            assert response.status_code in [400, 401]
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_verify_password(self, client, mock_firebase_auth):
        """Test password verification"""
        with patch('auth.auth_routes.firebase_auth_service', mock_firebase_auth):
            mock_firebase_auth.verify_password.return_value = True
            
            verify_data = {
                'email': 'test@test.com',
                'password': 'correctpassword'
            }
            
            response = client.post(
                '/api/auth/verify-password',
                headers={'Content-Type': 'application/json'},
                data=json.loads(json.dumps(verify_data))
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
    
    def test_verify_password_incorrect(self, client, mock_firebase_auth):
        """Test password verification with incorrect password"""
        with patch('auth.auth_routes.firebase_auth_service', mock_firebase_auth):
            mock_firebase_auth.verify_password.return_value = False
            
            verify_data = {
                'email': 'test@test.com',
                'password': 'wrongpassword'
            }
            
            response = client.post(
                '/api/auth/verify-password',
                headers={'Content-Type': 'application/json'},
                data=json.dumps(verify_data)
            )
            
            assert response.status_code in [400, 401]
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_token_verification_success(self, client, mock_firebase_auth):
        """Test successful token verification"""
        with patch('auth.auth_routes.firebase_auth_service', mock_firebase_auth):
            mock_firebase_auth.verify_token.return_value = {
                'success': True,
                'uid': 'test-uid',
                'email': 'test@test.com'
            }
            
            response = client.get(
                '/api/auth/verify-token',
                headers={'Authorization': 'Bearer valid-token'}
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'user' in data
    
    def test_token_verification_invalid(self, client, mock_firebase_auth):
        """Test token verification with invalid token"""
        with patch('auth.auth_routes.firebase_auth_service', mock_firebase_auth):
            mock_firebase_auth.verify_token.return_value = {
                'success': False,
                'error': 'Invalid token'
            }
            
            response = client.get(
                '/api/auth/verify-token',
                headers={'Authorization': 'Bearer invalid-token'}
            )
            
            assert response.status_code in [401, 403]
            data = json.loads(response.data)
            assert data['success'] is False
    
    def test_logout(self, client):
        """Test logout endpoint"""
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'message' in data
    
    def test_validation_errors(self, client):
        """Test request validation"""
        # Missing email
        login_data = {
            'password': 'password123'
        }
        
        response = client.post(
            '/api/auth/login',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(login_data)
        )
        
        assert response.status_code in [400, 422]
        data = json.loads(response.data)
        assert data['success'] is False







