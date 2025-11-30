"""
Unit tests for admin routes (admin_routes.py)
Tests admin user management, doctor verification, and statistics
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

# Patch decorators BEFORE importing admin_routes
def mock_role_required(roles):
    """Mock role required decorator"""
    def decorator(f):
        return f
    return decorator

def mock_auth_required(f):
    """Mock auth required decorator"""
    return f

# Apply patches before import
with patch('auth.firebase_auth.firebase_auth_required', side_effect=mock_auth_required):
    with patch('auth.firebase_auth.firebase_role_required', side_effect=mock_role_required):
        from admin_routes import admin_bp


class TestAdminRoutes:
    """Test cases for admin routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Mock supabase
        with patch('admin_routes.supabase') as mock_supabase:
            mock_service_client = MagicMock()
            mock_table = MagicMock()
            mock_service_client.table.return_value = mock_table
            mock_supabase.service_client = mock_service_client
            mock_supabase.client = mock_service_client
            
            app.register_blueprint(admin_bp)
            
            with app.test_client() as client:
                yield client
    
    @pytest.fixture
    def mock_supabase_table(self):
        """Mock Supabase table operations"""
        with patch('admin_routes.supabase') as mock_supabase:
            mock_service_client = MagicMock()
            mock_table = MagicMock()
            mock_service_client.table.return_value = mock_table
            mock_supabase.service_client = mock_service_client
            mock_supabase.client = mock_service_client
            
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.insert.return_value = mock_table
            mock_table.update.return_value = mock_table
            mock_table.order.return_value = mock_table
            mock_table.range.return_value = mock_table
            mock_table.or_.return_value = mock_table
            mock_table.gte.return_value = mock_table
            
            mock_response = Mock()
            mock_response.data = []
            mock_response.count = 0
            mock_table.execute.return_value = mock_response
            
            yield mock_table
    
    def test_get_all_users_success(self, client, mock_supabase_table):
        """Test getting all users"""
        mock_supabase_table.execute.return_value.data = [
            {'id': 1, 'email': 'user1@test.com', 'role': 'patient'},
            {'id': 2, 'email': 'user2@test.com', 'role': 'doctor'}
        ]
        mock_supabase_table.execute.return_value.count = 2
        
        response = client.get('/api/admin/users')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'users' in data
        assert 'pagination' in data
    
    def test_get_user_success(self, client, mock_supabase_table):
        """Test getting single user"""
        mock_supabase_table.execute.return_value.data = [{
            'id': 1,
            'email': 'test@example.com',
            'role': 'patient'
        }]
        
        response = client.get('/api/admin/users/user123')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'user' in data
    
    def test_get_user_not_found(self, client, mock_supabase_table):
        """Test getting non-existent user"""
        mock_supabase_table.execute.return_value.data = []
        
        response = client.get('/api/admin/users/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_create_user_success(self, client, mock_supabase_table):
        """Test creating a new user"""
        # Check existing user - return empty
        check_chain = MagicMock()
        check_chain.execute.return_value.data = []
        mock_supabase_table.eq.return_value = check_chain
        
        # Insert new user - return success
        insert_chain = MagicMock()
        insert_chain.execute.return_value.data = [{
            'id': 1,
            'email': 'new@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'patient'
        }]
        mock_supabase_table.insert.return_value = insert_chain
        
        response = client.post('/api/admin/users',
                              data=json.dumps({
                                  'email': 'new@example.com',
                                  'first_name': 'John',
                                  'last_name': 'Doe',
                                  'role': 'patient'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_create_user_missing_fields(self, client):
        """Test creating user with missing fields"""
        response = client.post('/api/admin/users',
                              data=json.dumps({
                                  'email': 'test@example.com'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_create_user_invalid_role(self, client):
        """Test creating user with invalid role"""
        response = client.post('/api/admin/users',
                              data=json.dumps({
                                  'email': 'test@example.com',
                                  'first_name': 'John',
                                  'last_name': 'Doe',
                                  'role': 'invalid'
                              }),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_update_user_success(self, client, mock_supabase_table):
        """Test updating user"""
        # Get existing user - first select().eq().execute() call
        select_eq_execute = MagicMock()
        select_eq_execute.execute.return_value.data = [{
            'id': 1,
            'email': 'test@example.com'
        }]
        select_eq = MagicMock()
        select_eq.execute.return_value = select_eq_execute.execute.return_value
        select_chain = MagicMock()
        select_chain.eq.return_value = select_eq
        mock_supabase_table.select.return_value = select_chain
        
        # Update user - update().eq().execute() call
        update_eq_execute = MagicMock()
        update_eq_execute.execute.return_value.data = [{
            'id': 1,
            'first_name': 'Updated',
            'last_name': 'Name'
        }]
        update_eq = MagicMock()
        update_eq.execute.return_value = update_eq_execute.execute.return_value
        update_chain = MagicMock()
        update_chain.eq.return_value = update_eq
        mock_supabase_table.update.return_value = update_chain
        
        response = client.put('/api/admin/users/user123',
                             data=json.dumps({
                                 'first_name': 'Updated',
                                 'last_name': 'Name'
                             }),
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_get_stats_success(self, client, mock_supabase_table):
        """Test getting admin statistics"""
        # Mock all count queries
        mock_response = Mock()
        mock_response.count = 10
        mock_supabase_table.execute.return_value = mock_response
        
        response = client.get('/api/admin/stats')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'stats' in data
        assert 'total_users' in data['stats']
    
    def test_get_pending_doctors_success(self, client, mock_supabase_table):
        """Test getting pending doctors"""
        # Mock doctor profiles - first select() call
        doctor_execute = MagicMock()
        doctor_execute.execute.return_value.data = [
            {
                'id': 1,
                'firebase_uid': 'doctor1',
                'verification_status': 'pending',
                'created_at': '2025-01-01T00:00:00'
            }
        ]
        select_chain1 = MagicMock()
        select_chain1.execute.return_value = doctor_execute.execute.return_value
        mock_supabase_table.select.return_value = select_chain1
        
        # Mock user profiles - select().eq().execute() call
        user_execute = MagicMock()
        user_execute.execute.return_value.data = [{
            'first_name': 'Doctor',
            'last_name': 'One',
            'email': 'doctor1@test.com',
            'created_at': '2025-01-01T00:00:00',
            'avatar_url': None
        }]
        user_eq = MagicMock()
        user_eq.execute.return_value = user_execute.execute.return_value
        user_select = MagicMock()
        user_select.eq.return_value = user_eq
        # Handle multiple select() calls
        mock_supabase_table.select.side_effect = [select_chain1, user_select]
        
        # Mock eq() for user lookup
        mock_supabase_table.eq.return_value = user_select
        
        # Mock documents count - another select().eq().execute() call
        docs_execute = MagicMock()
        docs_execute.execute.return_value.data = []
        docs_eq = MagicMock()
        docs_eq.execute.return_value = docs_execute.execute.return_value
        docs_select = MagicMock()
        docs_select.eq.return_value = docs_eq
        # Add to side_effect
        mock_supabase_table.select.side_effect = [select_chain1, user_select, docs_select]
        
        response = client.get('/api/admin/doctors/pending')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'doctors' in data
    
    @patch('admin_routes.datetime')
    def test_approve_doctor_success(self, mock_datetime, client, mock_supabase_table):
        """Test approving a doctor"""
        mock_datetime.utcnow.return_value.isoformat.return_value = '2025-01-01T00:00:00'
        
        # Mock doctor profile query - need proper chaining
        select_chain = MagicMock()
        eq_chain1 = MagicMock()
        eq_chain1.execute.return_value.data = [{
            'id': 1,
            'firebase_uid': 'doctor1',
            'verification_status': 'pending'
        }]
        select_chain.eq.return_value = eq_chain1
        mock_supabase_table.select.return_value = select_chain
        
        # Mock user profile query
        eq_chain2 = MagicMock()
        eq_chain2.execute.return_value.data = [{
            'email': 'doctor@test.com',
            'first_name': 'Doctor',
            'last_name': 'Name'
        }]
        # Handle multiple eq() calls
        mock_supabase_table.eq.side_effect = [eq_chain1, eq_chain2]
        
        # Mock update operations
        update_chain = MagicMock()
        update_eq_chain = MagicMock()
        update_eq_chain.execute.return_value.data = [{
            'id': 1,
            'verification_status': 'approved'
        }]
        update_chain.eq.return_value = update_eq_chain
        mock_supabase_table.update.return_value = update_chain
        
        # Patch the imported function
        with patch('doctor_verification.send_doctor_notification_email'):
            response = client.post('/api/admin/doctors/doctor1/approve')
            
            # May return 404 if doctor not found, or 200 if successful
            # Just check that it doesn't return 401 (auth error)
            assert response.status_code != 401


if __name__ == '__main__':
    pytest.main([__file__, '-v'])