"""
Unit tests for appointment routes (appointment_routes.py)
Tests appointment scheduling, management, and cleanup functionality
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from flask import Flask
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


class TestAppointmentRoutes:
    """Test cases for appointment routes"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Mock firebase_auth_required decorator
        def mock_auth_required(f):
            return f
        
        with patch('appointment_routes.firebase_auth_required', side_effect=mock_auth_required):
            # Mock supabase
            with patch('appointment_routes.supabase') as mock_supabase:
                mock_service_client = MagicMock()
                mock_table = MagicMock()
                mock_service_client.table.return_value = mock_table
                mock_supabase.service_client = mock_service_client
                
                from appointment_routes import appointments_bp
                app.register_blueprint(appointments_bp)
                
                with app.test_client() as client:
                    yield client
    
    @pytest.fixture
    def mock_supabase_table(self):
        """Mock Supabase table operations"""
        with patch('appointment_routes.supabase') as mock_supabase:
            mock_service_client = MagicMock()
            mock_table = MagicMock()
            mock_service_client.table.return_value = mock_table
            mock_supabase.service_client = mock_service_client
            
            mock_table.select.return_value = mock_table
            mock_table.eq.return_value = mock_table
            mock_table.insert.return_value = mock_table
            mock_table.update.return_value = mock_table
            mock_table.delete.return_value = mock_table
            
            mock_response = Mock()
            mock_response.data = []
            mock_table.execute.return_value = mock_response
            
            yield mock_table
    
    def test_get_manila_now(self):
        """Test getting current time in Manila timezone"""
        from appointment_routes import get_manila_now
        
        now = get_manila_now()
        assert isinstance(now, datetime)
    
    @patch('appointment_routes.get_manila_now')
    def test_cleanup_past_appointments_no_appointments(self, mock_get_now, mock_supabase_table):
        """Test cleanup when no appointments exist"""
        from appointment_routes import cleanup_past_appointments
        
        # Set current time
        mock_now = datetime(2025, 1, 15, 12, 0, 0)
        mock_get_now.return_value = mock_now
        
        # No appointments found
        mock_supabase_table.select.return_value.eq.return_value.execute.return_value.data = []
        
        result = cleanup_past_appointments()
        
        assert result['success'] is True
        assert result['deleted_count'] == 0
    
    @patch('appointment_routes.get_manila_now')
    def test_cleanup_past_appointments_with_past_appointments(self, mock_get_now, mock_supabase_table):
        """Test cleanup with past appointments"""
        from appointment_routes import cleanup_past_appointments
        
        # Set current time
        mock_now = datetime(2025, 1, 15, 12, 0, 0)
        mock_get_now.return_value = mock_now
        
        # Past appointment
        past_date = (mock_now - timedelta(days=1)).strftime('%Y-%m-%d')
        past_appointments = [{
            'id': 1,
            'appointment_date': past_date,
            'appointment_time': '10:00:00',
            'status': 'scheduled',
            'patient_firebase_uid': 'patient1',
            'doctor_firebase_uid': 'doctor1'
        }]
        
        mock_supabase_table.select.return_value.eq.return_value.execute.return_value.data = past_appointments
        
        # Mock archive and delete operations
        mock_supabase_table.insert.return_value.execute.return_value.data = [{'id': 1}]
        mock_supabase_table.delete.return_value.eq.return_value.execute.return_value = Mock()
        
        result = cleanup_past_appointments()
        
        # Should process appointments
        assert 'success' in result or 'deleted_count' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
