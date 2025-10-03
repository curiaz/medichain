"""
Complete Settings Management Backend Routes
Full implementation with comprehensive error handling, security features,
and audit logging for MediChain Settings Page
"""
from flask import Blueprint, request, jsonify
from auth.firebase_auth import firebase_auth_required
from db.supabase_client import SupabaseClient
from firebase_admin import auth as firebase_auth
from datetime import datetime, timedelta
import hashlib
import re
import logging
import traceback
import json
from typing import Dict, Any, Optional, Tuple
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Blueprint and Supabase
settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')
supabase = SupabaseClient()

# Constants
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_HISTORY_LIMIT = 5
ACCOUNT_DELETION_GRACE_PERIOD = 30  # days
MAX_AUDIT_LOG_ENTRIES = 100
AUDIT_LOG_RETENTION_DAYS = 90

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_client_ip() -> str:
    """Extract client IP address from request headers"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr or 'Unknown'

def get_user_agent() -> str:
    """Extract user agent from request headers"""
    return request.headers.get('User-Agent', 'Unknown')

def log_security_event(
    user_id: str,
    action: str,
    status: str = 'success',
    description: str = None,
    error_message: str = None,
    metadata: Dict[str, Any] = None
) -> Optional[str]:
    """
    Log security events to audit trail
    
    Args:
        user_id: Firebase UID of the user
        action: Type of security action performed
        status: Status of the action (success, failed, blocked)
        description: Human-readable description
        error_message: Error message if action failed
        metadata: Additional metadata as dict
        
    Returns:
        ID of the created audit log entry, or None if failed
    """
    try:
        audit_data = {
            'user_firebase_uid': user_id,
            'action': action,
            'action_type': 'security',
            'description': description or f"User performed {action}",
            'ip_address': get_client_ip(),
            'user_agent': get_user_agent(),
            'status': status,
            'error_message': error_message,
            'metadata': json.dumps(metadata or {}),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        result = supabase.service_client.table('security_audit_log').insert(audit_data).execute()
        
        if result.data:
            logger.info(f"Security event logged: {action} for user {user_id} - {status}")
            return result.data[0].get('id')
        
        logger.warning(f"Failed to log security event: No data returned")
        return None
        
    except Exception as e:
        logger.error(f"Failed to log security event: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password meets security requirements
    
    Returns:
        (is_valid, error_message)
    """
    if not password:
        return False, "Password cannot be empty"
    
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
    
    if len(password) > PASSWORD_MAX_LENGTH:
        return False, f"Password must not exceed {PASSWORD_MAX_LENGTH} characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    # Check for common weak passwords
    weak_passwords = [
        'password', 'password123', '12345678', 'qwerty123', 
        'admin123', 'welcome123', 'letmein123'
    ]
    if password.lower() in weak_passwords:
        return False, "Password is too common. Please choose a stronger password"
    
    # Check for sequential characters
    sequential_patterns = [
        '012', '123', '234', '345', '456', '567', '678', '789',
        'abc', 'bcd', 'cde', 'def', 'efg', 'fgh'
    ]
    if any(pattern in password.lower() for pattern in sequential_patterns):
        return False, "Password should not contain sequential characters"
    
    return True, None

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def check_password_in_history(user_id: str, new_password_hash: str) -> bool:
    """
    Check if password was used recently
    
    Returns:
        True if password is in history (should be rejected), False otherwise
    """
    try:
        response = supabase.service_client.table('password_history')\
            .select('password_hash')\
            .eq('user_firebase_uid', user_id)\
            .order('changed_at', desc=True)\
            .limit(PASSWORD_HISTORY_LIMIT)\
            .execute()
        
        if response.data:
            for entry in response.data:
                if entry.get('password_hash') == new_password_hash:
                    return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking password history: {str(e)}")
        return False

def save_password_to_history(user_id: str, password_hash: str) -> None:
    """Save password hash to history"""
    try:
        history_data = {
            'user_firebase_uid': user_id,
            'password_hash': password_hash,
            'changed_at': datetime.utcnow().isoformat(),
            'ip_address': get_client_ip()
        }
        
        supabase.service_client.table('password_history').insert(history_data).execute()
        logger.info(f"Password saved to history for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to save password to history: {str(e)}")

def sanitize_input(text: str, max_length: int = 500) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not text:
        return ""
    # Remove null bytes and limit length
    sanitized = text.replace('\x00', '').strip()
    return sanitized[:max_length]

def validate_notification_preferences(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate notification preference data"""
    valid_fields = ['email_notifications', 'sms_notifications', 'appointment_reminders', 'diagnosis_alerts']
    
    for key, value in data.items():
        if key not in valid_fields:
            return False, f"Invalid field: {key}"
        if not isinstance(value, bool):
            return False, f"{key} must be a boolean value"
    
    return True, None

# =============================================================================
# NOTIFICATION PREFERENCES ENDPOINTS
# =============================================================================

@settings_bp.route('/notifications', methods=['GET'])
@firebase_auth_required
def get_notification_preferences():
    """
    Get user's notification preferences
    Returns default values if no preferences are set
    """
    firebase_user = request.firebase_user
    user_id = firebase_user['uid']
    
    try:
        logger.info(f"Fetching notification preferences for user: {user_id}")
        
        # Query notification preferences
        response = supabase.service_client.table('notification_preferences')\
            .select('*')\
            .eq('user_firebase_uid', user_id)\
            .execute()
        
        if response.data and len(response.data) > 0:
            preferences = response.data[0]
            
            result = {
                'success': True,
                'preferences': {
                    'email_notifications': preferences.get('email_notifications', True),
                    'sms_notifications': preferences.get('sms_notifications', False),
                    'appointment_reminders': preferences.get('appointment_reminders', True),
                    'diagnosis_alerts': preferences.get('diagnosis_alerts', True)
                },
                'last_updated': preferences.get('updated_at'),
                'created_at': preferences.get('created_at')
            }
            
            logger.info(f"Notification preferences retrieved for user: {user_id}")
            return jsonify(result), 200
        
        else:
            # Return default preferences
            logger.info(f"No preferences found for user {user_id}, returning defaults")
            
            default_result = {
                'success': True,
                'preferences': {
                    'email_notifications': True,
                    'sms_notifications': False,
                    'appointment_reminders': True,
                    'diagnosis_alerts': True
                },
                'last_updated': None,
                'created_at': None,
                'is_default': True
            }
            
            return jsonify(default_result), 200
    
    except Exception as e:
        logger.error(f"Error fetching notification preferences: {str(e)}")
        logger.error(traceback.format_exc())
        
        log_security_event(
            user_id=user_id,
            action='get_notification_preferences',
            status='failed',
            error_message=str(e)
        )
        
        return jsonify({
            'success': False,
            'error': 'Failed to fetch notification preferences',
            'message': 'An error occurred while retrieving your notification settings'
        }), 500

@settings_bp.route('/notifications', methods=['PUT'])
@firebase_auth_required
def update_notification_preferences():
    """
    Update user's notification preferences
    Creates new entry if none exists
    """
    firebase_user = request.firebase_user
    user_id = firebase_user['uid']
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body is empty'
            }), 400
        
        # Validate notification preferences
        is_valid, error_message = validate_notification_preferences(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error_message
            }), 400
        
        logger.info(f"Updating notification preferences for user: {user_id}")
        
        # Prepare update data
        preferences_data = {
            'user_firebase_uid': user_id,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        # Add only provided fields
        valid_fields = ['email_notifications', 'sms_notifications', 'appointment_reminders', 'diagnosis_alerts']
        for field in valid_fields:
            if field in data:
                preferences_data[field] = data[field]
        
        # Check if preferences exist
        existing = supabase.service_client.table('notification_preferences')\
            .select('*')\
            .eq('user_firebase_uid', user_id)\
            .execute()
        
        if existing.data:
            # Update existing preferences
            response = supabase.service_client.table('notification_preferences')\
                .update(preferences_data)\
                .eq('user_firebase_uid', user_id)\
                .execute()
            
            action_desc = "Updated notification preferences"
        else:
            # Create new preferences
            preferences_data['created_at'] = datetime.utcnow().isoformat()
            response = supabase.service_client.table('notification_preferences')\
                .insert(preferences_data)\
                .execute()
            
            action_desc = "Created notification preferences"
        
        # Log the change
        log_security_event(
            user_id=user_id,
            action='update_notification_preferences',
            status='success',
            description=action_desc,
            metadata=data
        )
        
        logger.info(f"Notification preferences updated successfully for user: {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Notification preferences updated successfully',
            'preferences': response.data[0] if response.data else preferences_data
        }), 200
    
    except Exception as e:
        logger.error(f"Error updating notification preferences: {str(e)}")
        logger.error(traceback.format_exc())
        
        log_security_event(
            user_id=user_id,
            action='update_notification_preferences',
            status='failed',
            error_message=str(e)
        )
        
        return jsonify({
            'success': False,
            'error': 'Failed to update notification preferences',
            'message': 'An error occurred while saving your settings'
        }), 500

# =============================================================================
# SECURITY & PASSWORD ENDPOINTS
# =============================================================================

@settings_bp.route('/security/password', methods=['POST'])
@firebase_auth_required
def change_password():
    """
    Change user password with validation and history checking
    """
    firebase_user = request.firebase_user
    user_id = firebase_user['uid']
    user_email = firebase_user.get('email')
    
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['current_password', 'new_password', 'confirm_password']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        current_password = sanitize_input(data['current_password'], 128)
        new_password = sanitize_input(data['new_password'], 128)
        confirm_password = sanitize_input(data['confirm_password'], 128)
        
        # Validate passwords match
        if new_password != confirm_password:
            return jsonify({
                'success': False,
                'error': 'New password and confirm password do not match'
            }), 400
        
        # Validate password strength
        is_strong, strength_error = validate_password_strength(new_password)
        if not is_strong:
            log_security_event(
                user_id=user_id,
                action='password_change',
                status='failed',
                error_message=f"Weak password: {strength_error}"
            )
            
            return jsonify({
                'success': False,
                'error': strength_error
            }), 400
        
        # Check if new password is same as current
        new_password_hash = hash_password(new_password)
        current_password_hash = hash_password(current_password)
        
        if new_password_hash == current_password_hash:
            return jsonify({
                'success': False,
                'error': 'New password must be different from current password'
            }), 400
        
        # Check password history
        if check_password_in_history(user_id, new_password_hash):
            log_security_event(
                user_id=user_id,
                action='password_change',
                status='blocked',
                description='Password was used recently'
            )
            
            return jsonify({
                'success': False,
                'error': f'Cannot reuse passwords from your last {PASSWORD_HISTORY_LIMIT} password changes'
            }), 400
        
        # Update password in Firebase
        try:
            firebase_auth.update_user(
                user_id,
                password=new_password
            )
            logger.info(f"Password updated in Firebase for user: {user_id}")
        except Exception as firebase_error:
            logger.error(f"Firebase password update failed: {str(firebase_error)}")
            
            log_security_event(
                user_id=user_id,
                action='password_change',
                status='failed',
                error_message=f"Firebase error: {str(firebase_error)}"
            )
            
            return jsonify({
                'success': False,
                'error': 'Failed to update password',
                'message': 'Please try again later'
            }), 500
        
        # Save to password history
        save_password_to_history(user_id, new_password_hash)
        
        # Log successful password change
        log_security_event(
            user_id=user_id,
            action='password_change',
            status='success',
            description='Password changed successfully'
        )
        
        logger.info(f"Password changed successfully for user: {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        logger.error(traceback.format_exc())
        
        log_security_event(
            user_id=user_id,
            action='password_change',
            status='failed',
            error_message=str(e)
        )
        
        return jsonify({
            'success': False,
            'error': 'Failed to change password',
            'message': 'An unexpected error occurred'
        }), 500

@settings_bp.route('/security/account/deactivate', methods=['POST'])
@firebase_auth_required
def deactivate_account():
    """
    Deactivate user account (soft delete)
    Account can be reactivated by logging in again
    """
    firebase_user = request.firebase_user
    user_id = firebase_user['uid']
    
    try:
        data = request.get_json()
        
        # Require password confirmation
        if 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Password confirmation required for account deactivation'
            }), 400
        
        password = sanitize_input(data['password'], 128)
        reason = sanitize_input(data.get('reason', ''), 500)
        
        logger.info(f"Deactivating account for user: {user_id}")
        
        # Update user profile to deactivated status
        deactivation_data = {
            'account_status': 'deactivated',
            'deactivated_at': datetime.utcnow().isoformat(),
            'deactivation_reason': reason,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        response = supabase.service_client.table('user_profiles')\
            .update(deactivation_data)\
            .eq('firebase_uid', user_id)\
            .execute()
        
        # Disable Firebase account
        try:
            firebase_auth.update_user(user_id, disabled=True)
            logger.info(f"Firebase account disabled for user: {user_id}")
        except Exception as firebase_error:
            logger.error(f"Failed to disable Firebase account: {str(firebase_error)}")
        
        # Log account deactivation
        log_security_event(
            user_id=user_id,
            action='account_deactivation',
            status='success',
            description='Account deactivated by user',
            metadata={'reason': reason}
        )
        
        logger.info(f"Account deactivated successfully for user: {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Account deactivated successfully. You can reactivate it by logging in again.'
        }), 200
    
    except Exception as e:
        logger.error(f"Error deactivating account: {str(e)}")
        logger.error(traceback.format_exc())
        
        log_security_event(
            user_id=user_id,
            action='account_deactivation',
            status='failed',
            error_message=str(e)
        )
        
        return jsonify({
            'success': False,
            'error': 'Failed to deactivate account',
            'message': 'An error occurred while deactivating your account'
        }), 500

@settings_bp.route('/security/account/delete', methods=['DELETE'])
@firebase_auth_required
def delete_account():
    """
    Request permanent account deletion
    Account will be deleted after 30-day grace period
    """
    firebase_user = request.firebase_user
    user_id = firebase_user['uid']
    
    try:
        data = request.get_json()
        
        # Require password confirmation
        if 'password' not in data:
            return jsonify({
                'success': False,
                'error': 'Password confirmation required for account deletion'
            }), 400
        
        password = sanitize_input(data['password'], 128)
        reason = sanitize_input(data.get('reason', ''), 500)
        
        logger.info(f"Initiating account deletion for user: {user_id}")
        
        # Create deletion request
        scheduled_deletion = datetime.utcnow() + timedelta(days=ACCOUNT_DELETION_GRACE_PERIOD)
        
        deletion_request = {
            'user_firebase_uid': user_id,
            'requested_at': datetime.utcnow().isoformat(),
            'scheduled_deletion_at': scheduled_deletion.isoformat(),
            'reason': reason,
            'status': 'pending'
        }
        
        # Check if deletion request already exists
        existing_request = supabase.service_client.table('account_deletion_requests')\
            .select('*')\
            .eq('user_firebase_uid', user_id)\
            .eq('status', 'pending')\
            .execute()
        
        if existing_request.data:
            logger.info(f"Deletion request already exists for user: {user_id}")
            existing = existing_request.data[0]
            
            return jsonify({
                'success': True,
                'message': 'Account deletion already scheduled',
                'scheduled_deletion_at': existing.get('scheduled_deletion_at'),
                'days_remaining': ACCOUNT_DELETION_GRACE_PERIOD
            }), 200
        
        # Insert new deletion request
        response = supabase.service_client.table('account_deletion_requests')\
            .insert(deletion_request)\
            .execute()
        
        # Update user profile status
        supabase.service_client.table('user_profiles')\
            .update({
                'account_status': 'pending_deletion',
                'deletion_requested_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })\
            .eq('firebase_uid', user_id)\
            .execute()
        
        # Log account deletion request
        log_security_event(
            user_id=user_id,
            action='account_deletion_request',
            status='success',
            description='Account deletion scheduled',
            metadata={
                'reason': reason,
                'scheduled_deletion_at': scheduled_deletion.isoformat(),
                'grace_period_days': ACCOUNT_DELETION_GRACE_PERIOD
            }
        )
        
        logger.info(f"Account deletion scheduled for user: {user_id}")
        
        return jsonify({
            'success': True,
            'message': f'Account deletion scheduled. Your account will be permanently deleted in {ACCOUNT_DELETION_GRACE_PERIOD} days.',
            'scheduled_deletion_at': scheduled_deletion.isoformat(),
            'grace_period_days': ACCOUNT_DELETION_GRACE_PERIOD
        }), 200
    
    except Exception as e:
        logger.error(f"Error requesting account deletion: {str(e)}")
        logger.error(traceback.format_exc())
        
        log_security_event(
            user_id=user_id,
            action='account_deletion_request',
            status='failed',
            error_message=str(e)
        )
        
        return jsonify({
            'success': False,
            'error': 'Failed to schedule account deletion',
            'message': 'An error occurred while processing your request'
        }), 500

@settings_bp.route('/security/account/delete/cancel', methods=['POST'])
@firebase_auth_required
def cancel_account_deletion():
    """
    Cancel a pending account deletion request
    """
    firebase_user = request.firebase_user
    user_id = firebase_user['uid']
    
    try:
        logger.info(f"Cancelling account deletion for user: {user_id}")
        
        # Update deletion request status
        response = supabase.service_client.table('account_deletion_requests')\
            .update({
                'status': 'cancelled',
                'cancelled_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            })\
            .eq('user_firebase_uid', user_id)\
            .eq('status', 'pending')\
            .execute()
        
        if not response.data:
            return jsonify({
                'success': False,
                'error': 'No pending deletion request found'
            }), 404
        
        # Update user profile status
        supabase.service_client.table('user_profiles')\
            .update({
                'account_status': 'active',
                'deletion_requested_at': None,
                'updated_at': datetime.utcnow().isoformat()
            })\
            .eq('firebase_uid', user_id)\
            .execute()
        
        # Log cancellation
        log_security_event(
            user_id=user_id,
            action='account_deletion_cancelled',
            status='success',
            description='User cancelled account deletion'
        )
        
        logger.info(f"Account deletion cancelled for user: {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Account deletion cancelled successfully'
        }), 200
    
    except Exception as e:
        logger.error(f"Error cancelling account deletion: {str(e)}")
        logger.error(traceback.format_exc())
        
        log_security_event(
            user_id=user_id,
            action='account_deletion_cancelled',
            status='failed',
            error_message=str(e)
        )
        
        return jsonify({
            'success': False,
            'error': 'Failed to cancel account deletion',
            'message': 'An error occurred while processing your request'
        }), 500

@settings_bp.route('/security/audit-log', methods=['GET'])
@firebase_auth_required
def get_security_audit_log():
    """
    Get user's security audit log with pagination
    """
    firebase_user = request.firebase_user
    user_id = firebase_user['uid']
    
    try:
        # Get pagination parameters
        limit = min(int(request.args.get('limit', 50)), MAX_AUDIT_LOG_ENTRIES)
        offset = int(request.args.get('offset', 0))
        
        logger.info(f"Fetching audit log for user: {user_id} (limit: {limit}, offset: {offset})")
        
        # Query audit log
        response = supabase.service_client.table('security_audit_log')\
            .select('*')\
            .eq('user_firebase_uid', user_id)\
            .order('timestamp', desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        # Get total count
        count_response = supabase.service_client.table('security_audit_log')\
            .select('id', count='exact')\
            .eq('user_firebase_uid', user_id)\
            .execute()
        
        total_count = len(count_response.data) if count_response.data else 0
        
        logger.info(f"Retrieved {len(response.data) if response.data else 0} audit log entries for user: {user_id}")
        
        return jsonify({
            'success': True,
            'audit_log': response.data if response.data else [],
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': total_count,
                'has_more': (offset + limit) < total_count
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching audit log: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': 'Failed to fetch audit log',
            'message': 'An error occurred while retrieving your security history'
        }), 500

@settings_bp.route('/security/sessions', methods=['GET'])
@firebase_auth_required
def get_active_sessions():
    """
    Get user's active sessions
    """
    firebase_user = request.firebase_user
    user_id = firebase_user['uid']
    
    try:
        logger.info(f"Fetching active sessions for user: {user_id}")
        
        # Query active sessions
        response = supabase.service_client.table('user_sessions')\
            .select('*')\
            .eq('user_firebase_uid', user_id)\
            .eq('is_active', True)\
            .order('last_activity_at', desc=True)\
            .execute()
        
        logger.info(f"Retrieved {len(response.data) if response.data else 0} active sessions for user: {user_id}")
        
        return jsonify({
            'success': True,
            'sessions': response.data if response.data else []
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching active sessions: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': 'Failed to fetch active sessions',
            'message': 'An error occurred while retrieving your sessions'
        }), 500

# =============================================================================
# HEALTH CHECK ENDPOINT
# =============================================================================

@settings_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for settings service"""
    return jsonify({
        'success': True,
        'service': 'settings',
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    }), 200
