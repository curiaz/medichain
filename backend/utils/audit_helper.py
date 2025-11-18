"""
Audit Helper - Simple, foolproof audit logging
This module provides a simple function that ALWAYS logs to the audit ledger
"""

from services.audit_service import audit_service
from flask import request
import traceback


def log_audit(action_type, entity_type, entity_id=None, data_before=None, data_after=None, 
              user_id=None, user_email=None, user_name=None, description=None):
    """
    Simple, foolproof audit logging function
    
    This function will ALWAYS try to log, and prints clear messages if it fails
    """
    try:
        # Print that we're trying to log
        print(f"[AUDIT] Attempting to log: {action_type} on {entity_type}")
        
        # Get user info from request if not provided
        if not user_id:
            try:
                firebase_user = getattr(request, 'firebase_user', None)
                if firebase_user:
                    user_id = firebase_user.get('uid')
                    user_email = firebase_user.get('email')
                    user_name = firebase_user.get('name')
            except:
                pass
        
        # If still no user info, try to get from request data
        if not user_id:
            try:
                data = request.get_json() if request.is_json else {}
                user_id = data.get('firebase_uid') or data.get('uid')
            except:
                pass
        
        # Default values
        user_id = user_id or "unknown"
        user_email = user_email or "unknown"
        user_name = user_name or "Unknown User"
        
        # Create description if not provided
        if not description:
            description = f"{action_type.replace('_', ' ').title()} on {entity_type}"
            if entity_id:
                description += f" (ID: {entity_id})"
        
        # Check if audit_service is available
        if not audit_service:
            print("[AUDIT ERROR] audit_service is None!")
            return None
        
        if not audit_service.supabase:
            print("[AUDIT ERROR] audit_service.supabase is None!")
            return None
        
        if not audit_service.supabase.service_client:
            print("[AUDIT ERROR] audit_service.supabase.service_client is None!")
            return None
        
        # Log the action
        print(f"[AUDIT] Calling audit_service.log_action...")
        print(f"[AUDIT]   user_id: {user_id}")
        print(f"[AUDIT]   action_type: {action_type}")
        print(f"[AUDIT]   entity_type: {entity_type}")
        print(f"[AUDIT]   entity_id: {entity_id}")
        
        result = audit_service.log_action(
            admin_id=user_id,
            admin_email=user_email,
            admin_name=user_name,
            action_type=action_type,
            action_description=description,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id else None,
            data_before=data_before,
            data_after=data_after,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        
        if result:
            print(f"[AUDIT SUCCESS] ✅ Logged to audit ledger: {result.get('id', 'unknown')}")
            return result
        else:
            print(f"[AUDIT ERROR] ❌ audit_service.log_action returned None!")
            return None
            
    except Exception as e:
        print(f"[AUDIT ERROR] ❌❌❌ EXCEPTION in log_audit: {e} ❌❌❌")
        traceback.print_exc()
        return None


