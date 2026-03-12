"""
Admin Routes
API endpoints for admin user management, doctor verification, and statistics
"""
from flask import Blueprint, request, jsonify
from auth.firebase_auth import firebase_role_required
from db.supabase_client import SupabaseClient
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Initialize Supabase client
try:
    supabase = SupabaseClient()
    print("[OK] Supabase client initialized for admin routes")
except Exception as e:
    print(f"[WARNING] Supabase client initialization failed in admin routes: {e}")
    supabase = None


@admin_bp.route('/users', methods=['GET'])
@firebase_role_required(["admin"])
def get_all_users():
    """Get all users with pagination (admin only)"""
    try:
        if not supabase:
            return jsonify({"success": False, "error": "Database not available"}), 500
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        
        response = supabase.service_client.table("user_profiles")\
            .select("*", count="exact")\
            .order("created_at", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        return jsonify({
            "success": True,
            "users": response.data or [],
            "pagination": {
                "page": page,
                "limit": limit,
                "total": response.count or 0,
                "total_pages": (response.count + limit - 1) // limit if response.count else 0
            }
        }), 200
    except Exception as e:
        print(f"[ERROR] Error getting users: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/users/<user_id>', methods=['GET'])
@firebase_role_required(["admin"])
def get_user(user_id):
    """Get single user by ID (admin only)"""
    try:
        if not supabase:
            return jsonify({"success": False, "error": "Database not available"}), 500
        
        response = supabase.service_client.table("user_profiles")\
            .select("*")\
            .eq("firebase_uid", user_id)\
            .execute()
        
        if not response.data:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        return jsonify({
            "success": True,
            "user": response.data[0]
        }), 200
    except Exception as e:
        print(f"[ERROR] Error getting user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/users', methods=['POST'])
@firebase_role_required(["admin"])
def create_user():
    """Create a new user (admin only)"""
    try:
        if not supabase:
            return jsonify({"success": False, "error": "Database not available"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        required_fields = ['email', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        valid_roles = ['patient', 'doctor', 'admin']
        if data.get('role') not in valid_roles:
            return jsonify({"success": False, "error": f"Invalid role. Must be one of: {', '.join(valid_roles)}"}), 400
        
        # Check if user already exists
        existing = supabase.service_client.table("user_profiles")\
            .select("id")\
            .eq("email", data['email'])\
            .execute()
        
        if existing.data:
            return jsonify({"success": False, "error": "User with this email already exists"}), 400
        
        # Insert new user
        response = supabase.service_client.table("user_profiles")\
            .insert(data)\
            .execute()
        
        return jsonify({
            "success": True,
            "user": response.data[0] if response.data else None
        }), 201
    except Exception as e:
        print(f"[ERROR] Error creating user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/users/<user_id>', methods=['PUT'])
@firebase_role_required(["admin"])
def update_user(user_id):
    """Update user by ID (admin only)"""
    try:
        if not supabase:
            return jsonify({"success": False, "error": "Database not available"}), 500
        
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400
        
        # Check if user exists
        existing = supabase.service_client.table("user_profiles")\
            .select("id")\
            .eq("firebase_uid", user_id)\
            .execute()
        
        if not existing.data:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Update user
        response = supabase.service_client.table("user_profiles")\
            .update(data)\
            .eq("firebase_uid", user_id)\
            .execute()
        
        return jsonify({
            "success": True,
            "user": response.data[0] if response.data else None
        }), 200
    except Exception as e:
        print(f"[ERROR] Error updating user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/stats', methods=['GET'])
@firebase_role_required(["admin"])
def get_stats():
    """Get admin statistics (admin only)"""
    try:
        if not supabase:
            return jsonify({"success": False, "error": "Database not available"}), 500
        
        # Get total users
        users_response = supabase.service_client.table("user_profiles")\
            .select("*", count="exact")\
            .limit(1)\
            .execute()
        total_users = users_response.count or 0
        
        # Get total doctors
        doctors_response = supabase.service_client.table("doctor_profiles")\
            .select("*", count="exact")\
            .limit(1)\
            .execute()
        total_doctors = doctors_response.count or 0
        
        # Get pending doctors
        pending_doctors_response = supabase.service_client.table("doctor_profiles")\
            .select("*", count="exact")\
            .eq("verification_status", "pending")\
            .limit(1)\
            .execute()
        pending_doctors = pending_doctors_response.count or 0
        
        return jsonify({
            "success": True,
            "stats": {
                "total_users": total_users,
                "total_doctors": total_doctors,
                "pending_doctors": pending_doctors
            }
        }), 200
    except Exception as e:
        print(f"[ERROR] Error getting stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/doctors/pending', methods=['GET'])
@firebase_role_required(["admin"])
def get_pending_doctors():
    """Get all pending doctor verification requests (admin only)"""
    try:
        if not supabase:
            return jsonify({"success": False, "error": "Database not available"}), 500
        
        doctors_response = supabase.service_client.table("doctor_profiles")\
            .select("*")\
            .eq("verification_status", "pending")\
            .order("created_at", desc=True)\
            .execute()
        
        doctors = []
        for doctor in (doctors_response.data or []):
            # Get user profile for each doctor
            user_response = supabase.service_client.table("user_profiles")\
                .select("first_name, last_name, email, created_at, avatar_url")\
                .eq("firebase_uid", doctor.get("firebase_uid"))\
                .execute()
            
            user_data = user_response.data[0] if user_response.data else {}
            
            # Get document count
            docs_response = supabase.service_client.table("doctor_verification_documents")\
                .select("*", count="exact")\
                .eq("doctor_id", doctor.get("firebase_uid"))\
                .limit(1)\
                .execute()
            
            doctor_data = {
                **doctor,
                **user_data,
                "document_count": docs_response.count or 0
            }
            doctors.append(doctor_data)
        
        return jsonify({
            "success": True,
            "doctors": doctors
        }), 200
    except Exception as e:
        print(f"[ERROR] Error getting pending doctors: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/doctors/<doctor_id>/approve', methods=['POST'])
@firebase_role_required(["admin"])
def approve_doctor(doctor_id):
    """Approve a doctor verification request (admin only)"""
    try:
        if not supabase:
            return jsonify({"success": False, "error": "Database not available"}), 500
        
        # Get doctor profile
        doctor_response = supabase.service_client.table("doctor_profiles")\
            .select("*")\
            .eq("firebase_uid", doctor_id)\
            .execute()
        
        if not doctor_response.data:
            return jsonify({"success": False, "error": "Doctor not found"}), 404
        
        doctor = doctor_response.data[0]
        if doctor.get("verification_status") != "pending":
            return jsonify({"success": False, "error": f"Doctor is already {doctor.get('verification_status')}"}), 400
        
        # Get user profile for email
        user_response = supabase.service_client.table("user_profiles")\
            .select("email, first_name, last_name")\
            .eq("firebase_uid", doctor_id)\
            .execute()
        
        user_data = user_response.data[0] if user_response.data else {}
        
        # Update doctor status
        update_response = supabase.service_client.table("doctor_profiles")\
            .update({
                "verification_status": "approved",
                "verified_at": datetime.utcnow().isoformat()
            })\
            .eq("firebase_uid", doctor_id)\
            .execute()
        
        # Send notification email if available
        try:
            from doctor_verification import send_doctor_notification_email
            if user_data.get("email"):
                doctor_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
                send_doctor_notification_email(
                    user_data["email"],
                    doctor_name,
                    "approved",
                    "Your doctor account has been approved. You can now log in and start using the platform."
                )
        except Exception as email_error:
            print(f"[WARNING] Could not send approval email: {email_error}")
        
        return jsonify({
            "success": True,
            "doctor": update_response.data[0] if update_response.data else None
        }), 200
    except Exception as e:
        print(f"[ERROR] Error approving doctor: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


print("[OK] Admin routes loaded!")
