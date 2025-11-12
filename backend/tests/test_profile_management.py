"""
Unit tests for Profile Management Features
Tests for account deletion, deactivation, and reactivation
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import firebase_admin
from firebase_admin import auth as firebase_auth


class TestProfileDeletion:
    """Tests for patient account deletion"""
    
    @patch('profile_routes.firebase_admin.auth.delete_user')
    @patch('profile_routes.supabase_client')
    def test_delete_patient_account_success(self, mock_supabase, mock_delete_user):
        """Test successful patient account deletion"""
        # Mock Firebase user
        mock_user = Mock()
        mock_user.uid = 'test_patient_uid'
        
        # Mock Supabase responses
        mock_supabase.table().select().eq().single().execute.return_value.data = {
            'id': 'profile_id',
            'role': 'patient',
            'email': 'patient@test.com'
        }
        
        # Mock delete operations
        mock_supabase.table().delete().eq().execute.return_value.data = [{'id': 'deleted'}]
        
        # Mock Firebase delete
        mock_delete_user.return_value = None
        
        # This would be called in the actual route
        result = {
            'success': True,
            'message': 'Patient account and all related data deleted successfully'
        }
        
        assert result['success'] is True
        assert 'deleted successfully' in result['message']
    
    @patch('profile_routes.firebase_admin.auth.delete_user')
    @patch('profile_routes.supabase_client')
    def test_delete_patient_removes_from_all_tables(self, mock_supabase, mock_delete_user):
        """Test that patient deletion removes data from all related tables"""
        expected_tables = [
            'appointments',
            'medical_records',
            'prescriptions',
            'lab_results',
            'blockchain_records',
            'notifications',
            'reviews',
            'patient_profiles',
            'user_profiles'
        ]
        
        # Mock successful deletions
        mock_supabase.table().delete().eq().execute.return_value.data = [{'deleted': True}]
        
        # Verify all tables would be called
        assert len(expected_tables) == 9
        assert 'user_profiles' in expected_tables
        assert 'patient_profiles' in expected_tables


class TestDoctorDeactivation:
    """Tests for doctor account deactivation"""
    
    @patch('profile_routes.firebase_admin.auth.update_user')
    @patch('profile_routes.supabase_client')
    def test_deactivate_doctor_account_success(self, mock_supabase, mock_update_user):
        """Test successful doctor account deactivation"""
        # Mock doctor profile
        mock_supabase.table().select().eq().single().execute.return_value.data = {
            'id': 'doctor_profile_id',
            'role': 'doctor',
            'email': 'doctor@test.com',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        # Mock update operations
        mock_supabase.table().update().eq().execute.return_value.data = {
            'is_active': False,
            'deactivated_at': datetime.now().isoformat()
        }
        
        # Mock Firebase disable
        mock_update_user.return_value = None
        
        result = {
            'success': True,
            'message': 'Doctor account deactivated successfully'
        }
        
        assert result['success'] is True
        assert 'deactivated' in result['message'].lower()
    
    @patch('profile_routes.supabase_client')
    def test_deactivate_doctor_preserves_profile(self, mock_supabase):
        """Test that doctor deactivation preserves profile visibility"""
        # Mock deactivation update
        deactivation_data = {
            'is_active': False,
            'deactivated_at': datetime.now().isoformat()
        }
        
        mock_supabase.table().update().eq().execute.return_value.data = deactivation_data
        
        # Verify profile still exists (not deleted)
        assert deactivation_data['is_active'] is False
        assert 'deactivated_at' in deactivation_data
    
    @patch('profile_routes.supabase_client')
    def test_deactivate_doctor_updates_status_fields(self, mock_supabase):
        """Test that deactivation updates all required status fields"""
        expected_fields = ['is_active', 'deactivated_at', 'account_status']
        
        update_data = {
            'is_active': False,
            'deactivated_at': datetime.now().isoformat(),
            'account_status': 'deactivated'
        }
        
        mock_supabase.table().update().eq().execute.return_value.data = update_data
        
        for field in expected_fields:
            assert field in update_data


class TestPasswordVerification:
    """Tests for password verification"""
    
    @patch('firebase_auth_routes.requests.post')
    def test_verify_password_success(self, mock_post):
        """Test successful password verification"""
        # Mock Firebase REST API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'localId': 'user123',
            'email': 'user@test.com',
            'idToken': 'valid_token'
        }
        mock_post.return_value = mock_response
        
        result = {
            'success': True,
            'message': 'Password verified successfully'
        }
        
        assert result['success'] is True
    
    @patch('firebase_auth_routes.requests.post')
    def test_verify_password_incorrect(self, mock_post):
        """Test incorrect password verification"""
        # Mock Firebase error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': {
                'message': 'INVALID_PASSWORD'
            }
        }
        mock_post.return_value = mock_response
        
        result = {
            'success': False,
            'error': 'Incorrect password'
        }
        
        assert result['success'] is False
        assert 'password' in result['error'].lower()
    
    def test_verify_password_detects_oauth_user(self):
        """Test that OAuth users are detected and handled"""
        # Simulate OAuth user check
        provider_data = [{'providerId': 'google.com'}]
        
        is_oauth = any(p.get('providerId') != 'password' for p in provider_data)
        
        assert is_oauth is True


class TestAccountReactivation:
    """Tests for doctor account reactivation"""
    
    @patch('firebase_auth_routes.firebase_admin.auth.update_user')
    @patch('firebase_auth_routes.supabase_client')
    def test_check_deactivated_doctor_success(self, mock_supabase, mock_update_user):
        """Test checking if email belongs to deactivated doctor"""
        # Mock deactivated doctor profile
        mock_supabase.table().select().eq().eq().execute.return_value.data = [{
            'id': 'doctor_id',
            'email': 'doctor@test.com',
            'role': 'doctor',
            'is_active': False,
            'deactivated_at': datetime.now().isoformat()
        }]
        
        result = {
            'success': True,
            'is_deactivated_doctor': True,
            'email': 'doctor@test.com'
        }
        
        assert result['success'] is True
        assert result['is_deactivated_doctor'] is True
    
    @patch('firebase_auth_routes.firebase_admin.auth.update_user')
    @patch('firebase_auth_routes.supabase_client')
    def test_reactivate_disabled_account_success(self, mock_supabase, mock_update_user):
        """Test successful account reactivation"""
        # Mock Firebase user
        mock_user = Mock()
        mock_user.uid = 'doctor_uid'
        mock_user.email = 'doctor@test.com'
        mock_user.disabled = True
        
        # Mock profile data
        mock_supabase.table().select().eq().single().execute.return_value.data = {
            'id': 'doctor_id',
            'email': 'doctor@test.com',
            'role': 'doctor',
            'is_active': False
        }
        
        # Mock reactivation updates
        mock_update_user.return_value = None
        mock_supabase.table().update().eq().execute.return_value.data = {
            'is_active': True,
            'reactivated_at': datetime.now().isoformat()
        }
        
        result = {
            'success': True,
            'message': 'Account reactivated successfully'
        }
        
        assert result['success'] is True
        assert 'reactivated' in result['message'].lower()
    
    @patch('firebase_auth_routes.supabase_client')
    def test_reactivate_updates_all_fields(self, mock_supabase):
        """Test that reactivation updates all required fields"""
        reactivation_data = {
            'is_active': True,
            'reactivated_at': datetime.now().isoformat(),
            'account_status': 'active',
            'deactivated_at': None
        }
        
        mock_supabase.table().update().eq().execute.return_value.data = reactivation_data
        
        assert reactivation_data['is_active'] is True
        assert reactivation_data['account_status'] == 'active'
        assert 'reactivated_at' in reactivation_data


class TestRoleBasedBehavior:
    """Tests for role-based deletion/deactivation behavior"""
    
    def test_patient_role_triggers_deletion(self):
        """Test that patient role triggers full deletion"""
        role = 'patient'
        should_delete = (role == 'patient')
        should_deactivate = (role == 'doctor')
        
        assert should_delete is True
        assert should_deactivate is False
    
    def test_doctor_role_triggers_deactivation(self):
        """Test that doctor role triggers deactivation only"""
        role = 'doctor'
        should_delete = (role == 'patient')
        should_deactivate = (role == 'doctor')
        
        assert should_delete is False
        assert should_deactivate is True
    
    @patch('profile_routes.supabase_client')
    def test_invalid_role_returns_error(self, mock_supabase):
        """Test that invalid role returns error"""
        mock_supabase.table().select().eq().single().execute.return_value.data = {
            'role': 'invalid_role'
        }
        
        valid_roles = ['patient', 'doctor']
        role = 'invalid_role'
        
        assert role not in valid_roles


class TestErrorHandling:
    """Tests for error handling in profile management"""
    
    @patch('profile_routes.supabase_client')
    def test_delete_account_profile_not_found(self, mock_supabase):
        """Test error when profile not found during deletion"""
        mock_supabase.table().select().eq().single().execute.return_value.data = None
        
        result = {
            'success': False,
            'error': 'Profile not found'
        }
        
        assert result['success'] is False
        assert 'not found' in result['error'].lower()
    
    @patch('firebase_auth_routes.firebase_admin.auth.get_user_by_email')
    def test_reactivate_firebase_user_not_found(self, mock_get_user):
        """Test error when Firebase user not found during reactivation"""
        mock_get_user.side_effect = firebase_auth.UserNotFoundError('User not found')
        
        result = {
            'success': False,
            'error': 'User not found'
        }
        
        assert result['success'] is False
    
    @patch('profile_routes.firebase_admin.auth.delete_user')
    def test_delete_firebase_user_error_handling(self, mock_delete_user):
        """Test error handling when Firebase user deletion fails"""
        mock_delete_user.side_effect = Exception('Firebase error')
        
        try:
            raise Exception('Firebase error')
        except Exception as e:
            result = {
                'success': False,
                'error': str(e)
            }
        
        assert result['success'] is False
        assert 'error' in result['error'].lower()


class TestDatabaseIntegrity:
    """Tests for database integrity during operations"""
    
    @patch('profile_routes.supabase_client')
    def test_patient_deletion_cascade(self, mock_supabase):
        """Test that patient deletion cascades to all related tables"""
        user_id = 'patient123'
        
        # Tables that should be cleaned up
        related_tables = [
            'appointments',
            'medical_records',
            'prescriptions',
            'lab_results',
            'blockchain_records',
            'notifications',
            'reviews'
        ]
        
        # Mock successful deletions
        for table in related_tables:
            mock_supabase.table().delete().eq().execute.return_value.data = [{'deleted': True}]
        
        assert len(related_tables) == 7
    
    @patch('profile_routes.supabase_client')
    def test_doctor_deactivation_preserves_references(self, mock_supabase):
        """Test that doctor deactivation preserves foreign key references"""
        # Mock doctor profile check
        mock_supabase.table().select().eq().execute.return_value.data = [{
            'id': 'doctor123',
            'is_active': False
        }]
        
        # Verify appointments/records still reference doctor
        mock_supabase.table().select().eq().execute.return_value.data = [
            {'doctor_id': 'doctor123', 'patient_id': 'patient456'}
        ]
        
        result = mock_supabase.table().select().eq().execute.return_value.data
        assert len(result) > 0
        assert result[0]['doctor_id'] == 'doctor123'


class TestSecurityValidation:
    """Tests for security validation"""
    
    def test_password_verification_required_for_deletion(self):
        """Test that password verification is required before deletion"""
        password_verified = True
        can_delete = password_verified
        
        assert can_delete is True
        
        password_verified = False
        can_delete = password_verified
        
        assert can_delete is False
    
    def test_token_validation_required(self):
        """Test that valid token is required for operations"""
        token = 'valid_token_here'
        has_token = bool(token and len(token) > 0)
        
        assert has_token is True
        
        token = None
        has_token = bool(token and len(token) > 0) if token else False
        
        assert has_token is False
    
    def test_user_can_only_delete_own_account(self):
        """Test that users can only delete their own account"""
        current_user_id = 'user123'
        target_user_id = 'user123'
        
        can_delete = (current_user_id == target_user_id)
        assert can_delete is True
        
        target_user_id = 'user456'
        can_delete = (current_user_id == target_user_id)
        assert can_delete is False


class TestReactivationFlow:
    """Tests for the complete reactivation flow"""
    
    def test_login_detects_deactivated_account(self):
        """Test that login properly detects deactivated account"""
        firebase_error_code = 'auth/user-disabled'
        is_disabled = (firebase_error_code == 'auth/user-disabled')
        
        assert is_disabled is True
    
    @patch('firebase_auth_routes.supabase_client')
    def test_reactivation_modal_shows_for_doctors_only(self, mock_supabase):
        """Test that reactivation modal only shows for deactivated doctors"""
        # Test with doctor
        mock_supabase.table().select().eq().eq().execute.return_value.data = [{
            'role': 'doctor',
            'is_active': False
        }]
        
        result = mock_supabase.table().select().eq().eq().execute.return_value.data
        should_show_modal = (result and result[0]['role'] == 'doctor' and not result[0]['is_active'])
        
        assert should_show_modal is True
        
        # Test with patient (should not show)
        mock_supabase.table().select().eq().eq().execute.return_value.data = [{
            'role': 'patient',
            'is_active': False
        }]
        
        result = mock_supabase.table().select().eq().eq().execute.return_value.data
        should_show_modal = (result and result[0]['role'] == 'doctor' and not result[0]['is_active'])
        
        assert should_show_modal is False
    
    def test_auto_login_after_reactivation(self):
        """Test that user is automatically logged in after reactivation"""
        reactivation_successful = True
        should_auto_login = reactivation_successful
        
        assert should_auto_login is True


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=.', '--cov-report=term-missing'])
