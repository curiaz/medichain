"""
Notification Routes for Supabase
Handles notification CRUD operations using Supabase
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime
from auth.firebase_auth import firebase_auth_required
from db.supabase_client import SupabaseClient
from services.notification_service import notification_service

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

# Initialize Supabase client
try:
    supabase = SupabaseClient()
    print("✅ Supabase client initialized for notifications")
except Exception as e:
    print(f"❌ Error initializing Supabase client for notifications: {e}")
    supabase = None

def auth_required(f):
    """Decorator that accepts both Firebase and Supabase tokens"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return jsonify({"error": "No authorization header provided"}), 401
        
        try:
            token = auth_header.split(" ")[1]  # Remove 'Bearer ' prefix
        except IndexError:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Try Firebase token first, but don't fail if it's not a Firebase token
        from auth.firebase_auth import firebase_auth_service
        try:
            firebase_result = firebase_auth_service.verify_token(token)
            if firebase_result.get("success"):
                request.firebase_user = firebase_result
                return f(*args, **kwargs)
            else:
                # Firebase verification failed, continue to JWT fallbacks
                error_msg = firebase_result.get('error', '')
                if 'kid' in error_msg.lower():
                    print(f"⚠️  Token is JWT (no 'kid' claim), trying JWT fallbacks...")
        except Exception as firebase_error:
            error_str = str(firebase_error)
            if "kid" in error_str.lower():
                print(f"⚠️  Token is not a Firebase token (likely JWT), trying JWT fallbacks...")
        
        # Try Supabase-style JWT
        try:
            import jwt
            decoded = jwt.decode(token, options={"verify_signature": False})
            if 'sub' in decoded and 'email' in decoded:
                request.firebase_user = {
                    "success": True,
                    "uid": decoded.get('sub'),
                    "email": decoded.get('email')
                }
                return f(*args, **kwargs)
        except Exception:
            pass
        
        # Try app-issued JWT (medichain_token)
        try:
            from auth.auth_utils import auth_utils
            app_payload = auth_utils.decode_token(token)
            if app_payload and app_payload.get('email'):
                # The JWT has user_id which is the database ID, not Firebase UID
                # We need to look up the user profile to get the firebase_uid
                user_id = app_payload.get('user_id')
                
                if user_id and supabase and supabase.service_client:
                    try:
                        user_profile_response = (
                            supabase.service_client.table("user_profiles")
                            .select("firebase_uid, email, role")
                            .eq("id", user_id)
                            .execute()
                        )
                        
                        if user_profile_response.data:
                            user_profile = user_profile_response.data[0]
                            firebase_uid = user_profile.get('firebase_uid')
                            
                            if firebase_uid:
                                request.firebase_user = {
                                    "success": True,
                                    "uid": firebase_uid,
                                    "email": app_payload.get('email'),
                                    "role": app_payload.get('role')
                                }
                                return f(*args, **kwargs)
                        else:
                            # Fallback: try to find by email
                            user_profile_response = (
                                supabase.service_client.table("user_profiles")
                                .select("firebase_uid, email, role")
                                .eq("email", app_payload.get('email'))
                                .execute()
                            )
                            
                            if user_profile_response.data:
                                user_profile = user_profile_response.data[0]
                                firebase_uid = user_profile.get('firebase_uid')
                                
                                if firebase_uid:
                                    request.firebase_user = {
                                        "success": True,
                                        "uid": firebase_uid,
                                        "email": app_payload.get('email'),
                                        "role": app_payload.get('role')
                                    }
                                    return f(*args, **kwargs)
                    except Exception as db_error:
                        print(f"⚠️  Database lookup failed for JWT user_id: {db_error}")
                
                # Fallback: use user_id directly
                uid = app_payload.get('user_id') or app_payload.get('uid') or app_payload.get('sub')
                request.firebase_user = {
                    "success": True,
                    "uid": uid,
                    "email": app_payload.get('email'),
                    "role": app_payload.get('role')
                }
                return f(*args, **kwargs)
        except Exception:
            pass
        
        return jsonify({"error": "Invalid or expired token"}), 401
    
    return decorated_function

@notifications_bp.route("", methods=["GET"])
@auth_required
def get_notifications():
    """Get notifications for the authenticated user"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user["uid"]
        
        print(f"📥 Fetching notifications for user: {uid}")
        
        # Get query parameters
        is_read = request.args.get('is_read')
        category = request.args.get('category')
        limit = request.args.get('limit', type=int) or 50
        
        print(f"   Query params: is_read={is_read}, category={category}, limit={limit}")
        
        # Check if supabase client is available
        if not supabase or not supabase.service_client:
            print("❌ Supabase client not available")
            return jsonify({"success": False, "error": "Database connection unavailable"}), 500
        
        # Build query - use service_client to bypass RLS
        query = supabase.service_client.table("notifications").select("*").eq("user_id", uid)
        
        if is_read is not None:
            query = query.eq("is_read", is_read.lower() == 'true')
        
        if category:
            query = query.eq("category", category)
        
        query = query.order("created_at", desc=True).limit(limit)
        
        print(f"   Executing query...")
        response = query.execute()
        print(f"   Query response: {response}")
        print(f"   Response data type: {type(response.data)}")
        print(f"   Response data length: {len(response.data) if response.data else 0}")
        
        # Parse metadata JSON strings or dicts
        notifications = []
        if response.data:
            for notif in response.data:
                # Handle metadata - it might be a dict (JSONB) or a string
                if notif.get('metadata'):
                    if isinstance(notif['metadata'], str):
                        try:
                            import json
                            notif['metadata'] = json.loads(notif['metadata'])
                        except:
                            pass
                    # If it's already a dict, keep it as is
                notifications.append(notif)
        
        print(f"   Processed {len(notifications)} notifications")
        
        # Get unread count - use service_client to bypass RLS
        unread_response = supabase.service_client.table("notifications").select("id", count="exact").eq("user_id", uid).eq("is_read", False).execute()
        unread_count = unread_response.count if hasattr(unread_response, 'count') else 0
        
        print(f"   Unread count: {unread_count}")
        print(f"✅ Successfully fetched {len(notifications)} notifications for user {uid}")
        
        return jsonify({
            "success": True,
            "notifications": notifications,
            "unread_count": unread_count,
            "total": len(notifications)
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching notifications: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        return jsonify({"success": False, "error": str(e)}), 500

@notifications_bp.route("/<notification_id>", methods=["DELETE"])
@auth_required
def delete_notification(notification_id):
    """Delete a notification"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user["uid"]
        
        # Delete notification - use service_client to bypass RLS
        response = (
            supabase.service_client.table("notifications")
            .delete()
            .eq("id", notification_id)
            .eq("user_id", uid)
            .execute()
        )
        
        return jsonify({
            "success": True,
            "message": "Notification deleted"
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@notifications_bp.route("/<notification_id>", methods=["PUT"])
@auth_required
def update_notification(notification_id):
    """Update a notification (mark as read, etc.)"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user["uid"]
        data = request.get_json()
        
        # Build update data
        update_data = {}
        if 'is_read' in data:
            update_data['is_read'] = data['is_read']
            if data['is_read']:
                update_data['read_at'] = datetime.utcnow().isoformat()
        
        if 'is_archived' in data:
            update_data['is_archived'] = data['is_archived']
        
        update_data['updated_at'] = datetime.utcnow().isoformat()
        
        # Update notification - use service_client to bypass RLS
        response = (
            supabase.service_client.table("notifications")
            .update(update_data)
            .eq("id", notification_id)
            .eq("user_id", uid)
            .execute()
        )
        
        if response.data:
            return jsonify({"success": True, "notification": response.data[0]}), 200
        else:
            return jsonify({"success": False, "error": "Notification not found"}), 404
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@notifications_bp.route("/read-all", methods=["POST"])
@auth_required
def mark_all_read():
    """Mark all notifications as read for the user"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user["uid"]
        
        # Use service_client to bypass RLS
        response = (
            supabase.service_client.table("notifications")
            .update({
                "is_read": True,
                "read_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            })
            .eq("user_id", uid)
            .eq("is_read", False)
            .execute()
        )
        
        return jsonify({
            "success": True,
            "message": "All notifications marked as read",
            "updated_count": len(response.data) if response.data else 0
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@notifications_bp.route("/stats", methods=["GET"])
@auth_required
def get_notification_stats():
    """Get notification statistics for the user"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user["uid"]
        
        # Get total count - use service_client to bypass RLS
        total_response = supabase.service_client.table("notifications").select("id", count="exact").eq("user_id", uid).execute()
        total_count = total_response.count if hasattr(total_response, 'count') else 0
        
        # Get unread count - use service_client to bypass RLS
        unread_response = supabase.service_client.table("notifications").select("id", count="exact").eq("user_id", uid).eq("is_read", False).execute()
        unread_count = unread_response.count if hasattr(unread_response, 'count') else 0
        
        return jsonify({
            "success": True,
            "stats": {
                "total": total_count,
                "unread": unread_count,
                "read": total_count - unread_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


        firebase_user = request.firebase_user
        uid = firebase_user["uid"]
        
        # Get total count - use service_client to bypass RLS
        total_response = supabase.service_client.table("notifications").select("id", count="exact").eq("user_id", uid).execute()
        total_count = total_response.count if hasattr(total_response, 'count') else 0
        
        # Get unread count - use service_client to bypass RLS
        unread_response = supabase.service_client.table("notifications").select("id", count="exact").eq("user_id", uid).eq("is_read", False).execute()
        unread_count = unread_response.count if hasattr(unread_response, 'count') else 0
        
        return jsonify({
            "success": True,
            "stats": {
                "total": total_count,
                "unread": unread_count,
                "read": total_count - unread_count
            }
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

