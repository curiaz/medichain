"""
Audit Logger Decorator
Automatically logs admin actions to the audit ledger
"""

from functools import wraps
from flask import request, g
from services.audit_service import audit_service


def audit_log(action_type: str, entity_type: str, get_entity_id=None, get_data_before=None, get_data_after=None):
    """
    Decorator to automatically log admin actions to audit ledger
    
    Args:
        action_type: Type of action (CREATE, UPDATE, DELETE, VIEW, etc.)
        entity_type: Type of entity (user, appointment, doctor_profile, etc.)
        get_entity_id: Function to extract entity_id from request/response (optional)
        get_data_before: Function to get data before action (optional)
        get_data_after: Function to get data after action (optional)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get admin info from request (set by firebase_role_required)
            admin_id = None
            admin_email = None
            admin_name = None
            
            # Try to get from request.firebase_user (set by firebase_auth_required)
            firebase_user = getattr(request, 'firebase_user', None)
            if firebase_user:
                admin_id = firebase_user.get('uid')
                admin_email = firebase_user.get('email')
                admin_name = firebase_user.get('name')
            
            # Fallback to Flask g
            if not admin_id:
                admin_id = getattr(g, 'user_id', None) or getattr(g, 'firebase_uid', None) or getattr(g, 'uid', None)
            if not admin_email:
                admin_email = getattr(g, 'user_email', None) or getattr(g, 'email', None)
            if not admin_name:
                admin_name = getattr(g, 'user_name', None) or getattr(g, 'name', None)
            
            # Get data before action (if available)
            data_before = None
            if get_data_before:
                try:
                    data_before = get_data_before(*args, **kwargs)
                except Exception as e:
                    print(f"⚠️  Error getting data_before in audit_log: {e}")
            
            # Execute the actual function
            try:
                response = func(*args, **kwargs)
                
                # Get data after action
                data_after = None
                if get_data_after:
                    try:
                        data_after = get_data_after(response, *args, **kwargs)
                    except Exception as e:
                        print(f"⚠️  Error getting data_after in audit_log: {e}")
                
                # Extract entity_id
                entity_id = None
                if get_entity_id:
                    try:
                        entity_id = get_entity_id(*args, **kwargs)
                    except Exception as e:
                        print(f"⚠️  Error getting entity_id in audit_log: {e}")
                else:
                    # Try to get from kwargs (common pattern: user_id, doctor_id, etc.)
                    for key in ['user_id', 'doctor_id', 'appointment_id', 'id']:
                        if key in kwargs:
                            entity_id = str(kwargs[key])
                            break
                    if not entity_id and args:
                        # Try first argument
                        entity_id = str(args[0]) if args else None
                
                # Log to audit ledger (async-like, don't block response)
                try:
                    audit_service.log_action(
                        admin_id=admin_id or "unknown",
                        admin_email=admin_email,
                        admin_name=admin_name,
                        action_type=action_type,
                        action_description=f"{action_type} {entity_type}",
                        entity_type=entity_type,
                        entity_id=entity_id,
                        data_before=data_before,
                        data_after=data_after,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent'),
                        request_id=getattr(request, 'request_id', None),
                        metadata={
                            "route": request.path,
                            "method": request.method,
                            "endpoint": func.__name__
                        }
                    )
                except Exception as e:
                    # Don't fail the request if audit logging fails
                    print(f"⚠️  Audit logging failed (non-blocking): {e}")
                
                return response
                
            except Exception as e:
                # Log failed action attempt
                try:
                    audit_service.log_action(
                        admin_id=admin_id or "unknown",
                        admin_email=admin_email,
                        action_type=f"{action_type}_FAILED",
                        action_description=f"Failed {action_type} {entity_type}: {str(e)}",
                        entity_type=entity_type,
                        ip_address=request.remote_addr,
                        metadata={
                            "route": request.path,
                            "method": request.method,
                            "error": str(e)
                        }
                    )
                except:
                    pass
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator

