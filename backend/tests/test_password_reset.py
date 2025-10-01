#!/usr/bin/env python3
"""
Unit tests for Password Reset functionality
"""
import pytest
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import Mock, patch, MagicMock
import json


class TestPasswordResetSystem:
    """Test suite for password reset functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.test_email = "test@medichain.com"
        self.test_otp = "123456"

    def test_otp_manager_store_otp(self):
        """Test OTP storage functionality"""
        from services.simple_otp_manager import simple_otp_manager
        
        result = simple_otp_manager.store_otp(self.test_email, "https://test.firebase.com")
        
        assert result["success"] == True
        assert "otp_code" in result
        assert "session_token" in result
        assert len(result["otp_code"]) == 6
        assert result["otp_code"].isdigit()

    def test_otp_manager_verify_otp(self):
        """Test OTP verification functionality"""
        from services.simple_otp_manager import simple_otp_manager
        
        # Store OTP first
        store_result = simple_otp_manager.store_otp(self.test_email, "https://test.firebase.com")
        assert store_result["success"] == True
        
        otp_code = store_result["otp_code"]
        
        # Verify OTP
        verify_result = simple_otp_manager.verify_otp(self.test_email, otp_code)
        assert verify_result["success"] == True

    def test_otp_manager_invalid_otp(self):
        """Test OTP verification with invalid code"""
        from services.simple_otp_manager import simple_otp_manager
        
        # Store OTP first
        simple_otp_manager.store_otp(self.test_email, "https://test.firebase.com")
        
        # Try to verify with wrong OTP
        verify_result = simple_otp_manager.verify_otp(self.test_email, "000000")
        assert verify_result["success"] == False
        assert "invalid" in verify_result["error"].lower()

    def test_otp_expiration(self):
        """Test OTP expiration functionality"""
        from services.simple_otp_manager import simple_otp_manager
        import time
        
        # Mock time to simulate expiration
        with patch('time.time') as mock_time:
            mock_time.return_value = 1000
            
            # Store OTP
            result = simple_otp_manager.store_otp(self.test_email, "https://test.firebase.com")
            otp_code = result["otp_code"]
            
            # Simulate time passing (more than 5 minutes = 300 seconds)
            mock_time.return_value = 1400  # 400 seconds later
            
            # Try to verify expired OTP
            verify_result = simple_otp_manager.verify_otp(self.test_email, otp_code)
            assert verify_result["success"] == False
            assert "expired" in verify_result["error"].lower()

    @patch('smtplib.SMTP')
    def test_firebase_auth_email_sending(self, mock_smtp):
        """Test Firebase auth service email sending"""
        from auth.firebase_auth import firebase_auth_service
        
        # Mock SMTP server
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Mock environment variables
        with patch.dict(os.environ, {
            'GMAIL_USER': 'test@gmail.com',
            'GMAIL_APP_PASSWORD': 'test_password'
        }):
            # Test email sending
            result = firebase_auth_service._send_reset_link_email(
                self.test_email, 
                "https://test.firebase.com/reset",
                "123456"
            )
            
            # Verify email was attempted to be sent
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once()
            mock_server.send_message.assert_called_once()

    def test_firebase_auth_service_password_reset(self):
        """Test Firebase auth service password reset functionality"""
        from auth.firebase_auth import firebase_auth_service
        
        with patch('firebase_admin.auth.generate_password_reset_link') as mock_generate:
            mock_generate.return_value = "https://test.firebase.com/reset"
            
            with patch.object(firebase_auth_service, '_send_reset_link_email') as mock_send:
                mock_send.return_value = True
                
                result = firebase_auth_service.send_password_reset_email(self.test_email)
                
                assert result["success"] == True
                assert "message" in result
                assert "verification_code" in result

    def test_auth_routes_import(self):
        """Test that auth routes can be imported successfully"""
        try:
            from auth.auth_routes import auth_bp
            assert auth_bp is not None
            print("✅ Auth routes imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import auth routes: {e}")

    def test_firebase_auth_import(self):
        """Test that Firebase auth service can be imported"""
        try:
            from auth.firebase_auth import firebase_auth_service
            assert firebase_auth_service is not None
            print("✅ Firebase auth service imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import Firebase auth service: {e}")

    def test_simple_otp_manager_import(self):
        """Test that Simple OTP Manager can be imported"""
        try:
            from services.simple_otp_manager import simple_otp_manager
            assert simple_otp_manager is not None
            print("✅ Simple OTP Manager imported successfully")
        except ImportError as e:
            pytest.fail(f"Failed to import Simple OTP Manager: {e}")


class TestPasswordResetAPI:
    """Test password reset API endpoints"""
    
    def setup_method(self):
        """Set up Flask test client"""
        from app import app
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.test_email = "test@medichain.com"

    @patch('auth.firebase_auth.firebase_auth_service.send_password_reset_email')
    @patch('db.supabase_client.SupabaseClient')
    def test_password_reset_request_endpoint(self, mock_supabase, mock_firebase):
        """Test password reset request endpoint"""
        # Mock Supabase response
        mock_supabase_instance = Mock()
        mock_supabase.return_value = mock_supabase_instance
        mock_supabase_instance.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"email": self.test_email, "full_name": "Test User"}
        ]
        
        # Mock Firebase response
        mock_firebase.return_value = {
            "success": True,
            "verification_code": "123456",
            "message": "Reset email sent"
        }
        
        response = self.client.post('/api/auth/password-reset-request', 
                                   json={"email": self.test_email},
                                   headers={"Content-Type": "application/json"})
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] == True
        assert "session_token" in data

    def test_password_reset_request_invalid_email(self):
        """Test password reset with invalid email format"""
        response = self.client.post('/api/auth/password-reset-request',
                                   json={"email": "invalid-email"},
                                   headers={"Content-Type": "application/json"})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Invalid email format" in data["error"]

    def test_password_reset_request_missing_email(self):
        """Test password reset without email"""
        response = self.client.post('/api/auth/password-reset-request',
                                   json={},
                                   headers={"Content-Type": "application/json"})
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "Email is required" in data["error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])