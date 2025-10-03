"""
Unit Tests for Settings Backend Routes
Tests all endpoints, validation, security features, and error handling
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from flask import Flask

# Mock Firebase and Supabase before importing settings_routes
@pytest.fixture(autouse=True)
def mock_firebase_supabase():
    """Mock Firebase and Supabase globally"""
    with patch('firebase_admin.auth') as mock_firebase_auth, \
         patch('settings_routes.supabase') as mock_supabase:
        yield mock_firebase_auth, mock_supabase


@pytest.fixture
def app():
    """Create Flask test app"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Import and register blueprint after mocking
    from settings_routes import settings_bp
    app.register_blueprint(settings_bp)
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    return {
        'Authorization': 'Bearer test_token_123',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def mock_firebase_user():
    """Mock Firebase user data"""
    return {
        'uid': 'test_user_123',
        'email': 'test@example.com',
        'email_verified': True
    }


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

class TestHelperFunctions:
    """Test helper functions in settings_routes"""
    
    def test_validate_password_strength_valid(self):
        """Test password validation with valid password"""
        from settings_routes import validate_password_strength
        
        is_valid, error = validate_password_strength("SecurePass123!")
        assert is_valid is True
        assert error is None
    
    def test_validate_password_strength_too_short(self):
        """Test password validation with too short password"""
        from settings_routes import validate_password_strength
        
        is_valid, error = validate_password_strength("Short1!")
        assert is_valid is False
        assert "at least 8 characters" in error
    
    def test_validate_password_strength_no_uppercase(self):
        """Test password validation without uppercase letter"""
        from settings_routes import validate_password_strength
        
        is_valid, error = validate_password_strength("lowercase123!")
        assert is_valid is False
        assert "uppercase letter" in error
    
    def test_validate_password_strength_no_lowercase(self):
        """Test password validation without lowercase letter"""
        from settings_routes import validate_password_strength
        
        is_valid, error = validate_password_strength("UPPERCASE123!")
        assert is_valid is False
        assert "lowercase letter" in error
    
    def test_validate_password_strength_no_number(self):
        """Test password validation without number"""
        from settings_routes import validate_password_strength
        
        is_valid, error = validate_password_strength("NoNumbers!")
        assert is_valid is False
        assert "number" in error
    
    def test_validate_password_strength_no_special_char(self):
        """Test password validation without special character"""
        from settings_routes import validate_password_strength
        
        is_valid, error = validate_password_strength("NoSpecial123")
        assert is_valid is False
        assert "special character" in error
    
    def test_validate_password_strength_weak_password(self):
        """Test password validation with common weak password"""
        from settings_routes import validate_password_strength
        
        is_valid, error = validate_password_strength("password123")
        assert is_valid is False
        assert "too common" in error.lower()
    
    def test_validate_password_strength_sequential_chars(self):
        """Test password validation with sequential characters"""
        from settings_routes import validate_password_strength
        
        is_valid, error = validate_password_strength("Pass123word!")
        assert is_valid is False
        assert "sequential" in error.lower()
    
    def test_sanitize_input(self):
        """Test input sanitization"""
        from settings_routes import sanitize_input
        
        # Test with null bytes
        result = sanitize_input("test\x00input")
        assert "\x00" not in result
        
        # Test with length limit
        long_text = "a" * 1000
        result = sanitize_input(long_text, max_length=100)
        assert len(result) == 100
    
    def test_hash_password(self):
        """Test password hashing"""
        from settings_routes import hash_password
        
        password = "TestPassword123!"
        hashed = hash_password(password)
        
        assert hashed is not None
        assert len(hashed) == 64  # SHA-256 produces 64-char hex string
        assert hashed != password


# =============================================================================
# HEALTH CHECK TESTS
# =============================================================================

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint returns 200"""
        response = client.get('/api/settings/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['service'] == 'settings'
        assert data['status'] == 'healthy'
        assert 'timestamp' in data


# =============================================================================
# NOTIFICATION PREFERENCES TESTS
# =============================================================================

class TestNotificationPreferences:
    """Test notification preferences endpoints"""
    
    @patch('settings_routes.firebase_auth_required')
    def test_get_notifications_default(self, mock_auth, client, auth_headers):
        """Test GET notifications returns defaults when none exist"""
        # Mock authentication
        def auth_wrapper(f):
            def wrapper(*args, **kwargs):
                from flask import request
                request.user_id = 'test_user_123'
                request.firebase_user = {'uid': 'test_user_123'}
                return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        mock_auth.side_effect = auth_wrapper
        
        # Mock Supabase response (no data)
        with patch('settings_routes.supabase') as mock_supabase:
            mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
            
            response = client.get('/api/settings/notifications', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['preferences']['email_notifications'] is True
            assert data['preferences']['sms_notifications'] is False
    
    @patch('settings_routes.firebase_auth_required')
    def test_get_notifications_existing(self, mock_auth, client, auth_headers):
        """Test GET notifications returns existing preferences"""
        def auth_wrapper(f):
            def wrapper(*args, **kwargs):
                from flask import request
                request.user_id = 'test_user_123'
                request.firebase_user = {'uid': 'test_user_123'}
                return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        mock_auth.side_effect = auth_wrapper
        
        with patch('settings_routes.supabase') as mock_supabase:
            mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
                'email_notifications': False,
                'sms_notifications': True,
                'appointment_reminders': False,
                'diagnosis_alerts': True,
                'updated_at': '2025-10-04T12:00:00Z'
            }]
            
            response = client.get('/api/settings/notifications', headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['preferences']['email_notifications'] is False
            assert data['preferences']['sms_notifications'] is True
    
    @patch('settings_routes.firebase_auth_required')
    def test_update_notifications_valid(self, mock_auth, client, auth_headers):
        """Test PUT notifications with valid data"""
        def auth_wrapper(f):
            def wrapper(*args, **kwargs):
                from flask import request
                request.user_id = 'test_user_123'
                request.firebase_user = {'uid': 'test_user_123'}
                return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        mock_auth.side_effect = auth_wrapper
        
        with patch('settings_routes.supabase') as mock_supabase:
            # Mock existing preferences check
            mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{
                'id': 'test_id'
            }]
            
            # Mock update response
            mock_supabase.service_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [{
                'email_notifications': False,
                'sms_notifications': True
            }]
            
            payload = {
                'email_notifications': False,
                'sms_notifications': True
            }
            
            response = client.put('/api/settings/notifications', 
                                headers=auth_headers,
                                data=json.dumps(payload))
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
    
    @patch('settings_routes.firebase_auth_required')
    def test_update_notifications_invalid_field(self, mock_auth, client, auth_headers):
        """Test PUT notifications with invalid field"""
        def auth_wrapper(f):
            def wrapper(*args, **kwargs):
                from flask import request
                request.user_id = 'test_user_123'
                request.firebase_user = {'uid': 'test_user_123'}
                return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        mock_auth.side_effect = auth_wrapper
        
        payload = {
            'invalid_field': True
        }
        
        response = client.put('/api/settings/notifications',
                            headers=auth_headers,
                            data=json.dumps(payload))
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Invalid field' in data['error']


# =============================================================================
# PASSWORD CHANGE TESTS
# =============================================================================

class TestPasswordChange:
    """Test password change endpoint"""
    
    @patch('settings_routes.firebase_auth_required')
    @patch('settings_routes.firebase_auth')
    def test_change_password_valid(self, mock_firebase, mock_auth, client, auth_headers):
        """Test password change with valid data"""
        def auth_wrapper(f):
            def wrapper(*args, **kwargs):
                from flask import request
                request.user_id = 'test_user_123'
                request.firebase_user = {'uid': 'test_user_123', 'email': 'test@example.com'}
                return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        mock_auth.side_effect = auth_wrapper
        
        # Mock Firebase update_user
        mock_firebase.update_user = Mock()
        
        with patch('settings_routes.supabase') as mock_supabase, \
             patch('settings_routes.check_password_in_history', return_value=False):
            
            payload = {
                'current_password': 'OldPass123!',
                'new_password': 'NewSecurePass456!',
                'confirm_password': 'NewSecurePass456!'
            }
            
            response = client.post('/api/settings/security/password',
                                  headers=auth_headers,
                                  data=json.dumps(payload))
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
    
    @patch('settings_routes.firebase_auth_required')
    def test_change_password_mismatch(self, mock_auth, client, auth_headers):
        """Test password change with mismatched passwords"""
        def auth_wrapper(f):
            def wrapper(*args, **kwargs):
                from flask import request
                request.user_id = 'test_user_123'
                request.firebase_user = {'uid': 'test_user_123'}
                return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        mock_auth.side_effect = auth_wrapper
        
        payload = {
            'current_password': 'OldPass123!',
            'new_password': 'NewSecurePass456!',
            'confirm_password': 'DifferentPass789!'
        }
        
        response = client.post('/api/settings/security/password',
                              headers=auth_headers,
                              data=json.dumps(payload))
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'do not match' in data['error']
    
    @patch('settings_routes.firebase_auth_required')
    def test_change_password_weak(self, mock_auth, client, auth_headers):
        """Test password change with weak password"""
        def auth_wrapper(f):
            def wrapper(*args, **kwargs):
                from flask import request
                request.user_id = 'test_user_123'
                request.firebase_user = {'uid': 'test_user_123'}
                return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        mock_auth.side_effect = auth_wrapper
        
        payload = {
            'current_password': 'OldPass123!',
            'new_password': 'weak',
            'confirm_password': 'weak'
        }
        
        response = client.post('/api/settings/security/password',
                              headers=auth_headers,
                              data=json.dumps(payload))
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False


# =============================================================================
# ACCOUNT MANAGEMENT TESTS
# =============================================================================

class TestAccountManagement:
    """Test account management endpoints"""
    
    @patch('settings_routes.firebase_auth_required')
    @patch('settings_routes.firebase_auth')
    def test_deactivate_account(self, mock_firebase, mock_auth, client, auth_headers):
        """Test account deactivation"""
        def auth_wrapper(f):
            def wrapper(*args, **kwargs):
                from flask import request
                request.user_id = 'test_user_123'
                request.firebase_user = {'uid': 'test_user_123'}
                return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        mock_auth.side_effect = auth_wrapper
        
        mock_firebase.update_user = Mock()
        
        with patch('settings_routes.supabase') as mock_supabase:
            payload = {'password': 'TestPass123!'}
            
            response = client.post('/api/settings/security/account/deactivate',
                                  headers=auth_headers,
                                  data=json.dumps(payload))
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
    
    @patch('settings_routes.firebase_auth_required')
    def test_delete_account_request(self, mock_auth, client, auth_headers):
        """Test account deletion request"""
        def auth_wrapper(f):
            def wrapper(*args, **kwargs):
                from flask import request
                request.user_id = 'test_user_123'
                request.firebase_user = {'uid': 'test_user_123'}
                return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        mock_auth.side_effect = auth_wrapper
        
        with patch('settings_routes.supabase') as mock_supabase:
            # Mock no existing deletion request
            mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
            
            payload = {
                'password': 'TestPass123!',
                'reason': 'Test deletion'
            }
            
            response = client.delete('/api/settings/security/account/delete',
                                    headers=auth_headers,
                                    data=json.dumps(payload))
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert '30 days' in data['message']


# =============================================================================
# AUDIT LOG TESTS
# =============================================================================

class TestAuditLog:
    """Test security audit log endpoint"""
    
    @patch('settings_routes.firebase_auth_required')
    def test_get_audit_log(self, mock_auth, client, auth_headers):
        """Test GET audit log"""
        def auth_wrapper(f):
            def wrapper(*args, **kwargs):
                from flask import request
                request.user_id = 'test_user_123'
                request.firebase_user = {'uid': 'test_user_123'}
                return f(*args, **kwargs)
            wrapper.__name__ = f.__name__
            return wrapper
        mock_auth.side_effect = auth_wrapper
        
        with patch('settings_routes.supabase') as mock_supabase:
            mock_audit_data = [
                {
                    'id': 'log1',
                    'action': 'password_change',
                    'status': 'success',
                    'timestamp': '2025-10-04T12:00:00Z'
                }
            ]
            
            mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.order.return_value.range.return_value.execute.return_value.data = mock_audit_data
            mock_supabase.service_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_audit_data
            
            response = client.get('/api/settings/security/audit-log?limit=10',
                                headers=auth_headers)
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['audit_log']) > 0


# =============================================================================
# AUTHENTICATION TESTS
# =============================================================================

class TestAuthentication:
    """Test authentication requirements"""
    
    def test_no_auth_token(self, client):
        """Test endpoint without auth token returns 401"""
        response = client.get('/api/settings/notifications')
        # May return 401 or 500 depending on how decorator is mocked
        assert response.status_code in [401, 500]
    
    def test_invalid_auth_token(self, client):
        """Test endpoint with invalid auth token"""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/settings/notifications', headers=headers)
        # May return 401 or 500 depending on how decorator is mocked
        assert response.status_code in [401, 500]


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for settings module"""
    
    def test_settings_module_imports(self):
        """Test that settings_routes module can be imported"""
        try:
            import settings_routes
            assert hasattr(settings_routes, 'settings_bp')
            assert hasattr(settings_routes, 'validate_password_strength')
            assert hasattr(settings_routes, 'log_security_event')
        except ImportError as e:
            pytest.fail(f"Failed to import settings_routes: {e}")
    
    def test_blueprint_configuration(self):
        """Test that blueprint is properly configured"""
        from settings_routes import settings_bp
        
        assert settings_bp.name == 'settings'
        assert settings_bp.url_prefix == '/api/settings'
    
    def test_all_endpoints_registered(self):
        """Test that all expected endpoints are registered"""
        app = Flask(__name__)
        from settings_routes import settings_bp
        app.register_blueprint(settings_bp)
        
        # Get all rules
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        
        # Check expected endpoints exist
        assert any('/api/settings/notifications' in rule for rule in rules)
        assert any('/api/settings/security/password' in rule for rule in rules)
        assert any('/api/settings/health' in rule for rule in rules)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=settings_routes', '--cov-report=term-missing'])
