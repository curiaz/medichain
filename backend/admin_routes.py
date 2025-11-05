"""
Admin Routes for User Management
Admin-only endpoints for managing users, roles, and system statistics
"""

from flask import Blueprint, jsonify, request
from auth.firebase_auth import firebase_role_required
from db.supabase_client import SupabaseClient
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Initialize Supabase client
try:
    supabase = SupabaseClient()
    print("✅ Supabase client initialized for admin routes")
except Exception as e:
    print(f"⚠️  Warning: Supabase client initialization failed in admin routes: {e}")
    supabase = None


@admin_bp.route('/users', methods=['GET'])
@firebase_role_required(["admin"])
def get_all_users():
    """Get all users with optional filtering and pagination (admin only)"""
    try:
        # Get query parameters
        role = request.args.get('role')
        search = request.args.get('search', '').strip()
        is_active = request.args.get('is_active')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit

        # Build query
        query = supabase.service_client.table("user_profiles").select("*", count="exact")

        # Apply filters
        if role:
            query = query.eq("role", role)
        if is_active is not None:
            query = query.eq("is_active", is_active.lower() == "true")
        if search:
            # Search in name, email, or phone
            query = query.or_(
                f"first_name.ilike.%{search}%,last_name.ilike.%{search}%,email.ilike.%{search}%,phone.ilike.%{search}%"
            )

        # Apply pagination
        query = query.order("created_at", desc=True).range(offset, offset + limit - 1)

        response = query.execute()

        return jsonify({
            "success": True,
            "users": response.data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": response.count,
                "total_pages": (response.count + limit - 1) // limit if response.count else 0
            }
        }), 200

    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/users/<user_id>', methods=['GET'])
@firebase_role_required(["admin"])
def get_user(user_id):
    """Get single user details by ID (admin only)"""
    try:
        # Get user profile
        user_response = supabase.service_client.table("user_profiles").select("*").eq("firebase_uid", user_id).execute()

        if not user_response.data:
            return jsonify({"success": False, "error": "User not found"}), 404

        user = user_response.data[0]

        # Get doctor profile if user is a doctor
        doctor_profile = None
        if user.get("role") == "doctor":
            doctor_response = supabase.service_client.table("doctor_profiles").select("*").eq("firebase_uid", user_id).execute()
            if doctor_response.data:
                doctor_profile = doctor_response.data[0]

        return jsonify({
            "success": True,
            "user": {
                **user,
                "doctor_profile": doctor_profile
            }
        }), 200

    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/users', methods=['POST'])
@firebase_role_required(["admin"])
def create_user():
    """Create a new user (admin only)"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["email", "first_name", "last_name", "role"]
        for field in required_fields:
            if not data.get(field):
                return jsonify({"success": False, "error": f"{field} is required"}), 400

        # Validate role
        if data.get("role") not in ["patient", "doctor", "admin"]:
            return jsonify({"success": False, "error": "Invalid role"}), 400

        # Check if user already exists
        existing = supabase.service_client.table("user_profiles").select("*").eq("email", data["email"]).execute()
        if existing.data:
            return jsonify({"success": False, "error": "User with this email already exists"}), 409

        # Create user in Firebase (requires Firebase Admin SDK)
        # For now, we'll create the profile and let admin create Firebase account separately
        # Or generate a placeholder firebase_uid
        import uuid
        firebase_uid = data.get("firebase_uid") or f"admin_created_{uuid.uuid4().hex}"

        # Prepare user data
        user_data = {
            "firebase_uid": firebase_uid,
            "email": data["email"].lower().strip(),
            "first_name": data["first_name"].strip(),
            "last_name": data["last_name"].strip(),
            "phone": data.get("phone", "").strip(),
            "role": data["role"],
            "gender": data.get("gender"),
            "date_of_birth": data.get("date_of_birth"),
            "is_active": data.get("is_active", True),
            "is_verified": data.get("is_verified", False)
        }

        # Create user profile
        response = supabase.service_client.table("user_profiles").insert(user_data).execute()

        if response.data:
            return jsonify({
                "success": True,
                "user": response.data[0],
                "message": "User created successfully. Note: Firebase account must be created separately."
            }), 201
        else:
            return jsonify({"success": False, "error": "Failed to create user"}), 500

    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/users/<user_id>', methods=['PUT'])
@firebase_role_required(["admin"])
def update_user(user_id):
    """Update user details (admin only)"""
    try:
        data = request.get_json()

        # Get existing user
        existing = supabase.service_client.table("user_profiles").select("*").eq("firebase_uid", user_id).execute()
        if not existing.data:
            return jsonify({"success": False, "error": "User not found"}), 404

        # Prepare update data (only allow certain fields to be updated)
        update_data = {}
        allowed_fields = ["first_name", "last_name", "phone", "gender", "date_of_birth", "is_active", "is_verified"]
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]

        # Update user profile
        response = supabase.service_client.table("user_profiles").update(update_data).eq("firebase_uid", user_id).execute()

        if response.data:
            return jsonify({
                "success": True,
                "user": response.data[0]
            }), 200
        else:
            return jsonify({"success": False, "error": "Failed to update user"}), 500

    except Exception as e:
        print(f"❌ Error updating user: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/users/<user_id>/role', methods=['PUT'])
@firebase_role_required(["admin"])
def change_user_role(user_id):
    """Change user role (admin only)"""
    try:
        data = request.get_json()
        new_role = data.get("role")

        if not new_role or new_role not in ["patient", "doctor", "admin"]:
            return jsonify({"success": False, "error": "Invalid role"}), 400

        # Update role
        response = supabase.service_client.table("user_profiles").update({"role": new_role}).eq("firebase_uid", user_id).execute()

        if response.data:
            return jsonify({
                "success": True,
                "user": response.data[0],
                "message": f"User role changed to {new_role}"
            }), 200
        else:
            return jsonify({"success": False, "error": "User not found or update failed"}), 404

    except Exception as e:
        print(f"❌ Error changing user role: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/users/<user_id>/status', methods=['PUT'])
@firebase_role_required(["admin"])
def update_user_status(user_id):
    """Activate or deactivate user account (admin only)"""
    try:
        data = request.get_json()
        is_active = data.get("is_active")

        if is_active is None:
            return jsonify({"success": False, "error": "is_active field is required"}), 400

        # Update status
        response = supabase.service_client.table("user_profiles").update({"is_active": bool(is_active)}).eq("firebase_uid", user_id).execute()

        if response.data:
            return jsonify({
                "success": True,
                "user": response.data[0],
                "message": f"User account {'activated' if is_active else 'deactivated'}"
            }), 200
        else:
            return jsonify({"success": False, "error": "User not found or update failed"}), 404

    except Exception as e:
        print(f"❌ Error updating user status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/stats', methods=['GET'])
@firebase_role_required(["admin"])
def get_stats():
    """Get admin dashboard statistics (admin only)"""
    try:
        # Get total users
        total_users = supabase.service_client.table("user_profiles").select("*", count="exact").execute()
        
        # Get users by role
        patients = supabase.service_client.table("user_profiles").select("*", count="exact").eq("role", "patient").execute()
        doctors = supabase.service_client.table("user_profiles").select("*", count="exact").eq("role", "doctor").execute()
        admins = supabase.service_client.table("user_profiles").select("*", count="exact").eq("role", "admin").execute()
        
        # Get active users
        active_users = supabase.service_client.table("user_profiles").select("*", count="exact").eq("is_active", True).execute()
        
        # Get verified doctors
        verified_doctors = supabase.service_client.table("doctor_profiles").select("*", count="exact").eq("is_verified", True).execute()
        
        # Get recent registrations (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
        recent_users = supabase.service_client.table("user_profiles").select("*", count="exact").gte("created_at", thirty_days_ago).execute()

        return jsonify({
            "success": True,
            "stats": {
                "total_users": total_users.count or 0,
                "patients": patients.count or 0,
                "doctors": doctors.count or 0,
                "admins": admins.count or 0,
                "active_users": active_users.count or 0,
                "inactive_users": (total_users.count or 0) - (active_users.count or 0),
                "verified_doctors": verified_doctors.count or 0,
                "recent_registrations": recent_users.count or 0
            }
        }), 200

    except Exception as e:
        print(f"❌ Error fetching stats: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

# IMPORTANT: Static routes must be defined BEFORE dynamic routes!
# /doctors/pending must come before /doctors/<doctor_id>/approve
# Otherwise Flask will match "pending" as a doctor_id parameter

@admin_bp.route('/doctors/pending', methods=['GET'])
@firebase_role_required(["admin"])
def get_pending_doctors():
    """Get all pending doctor verification requests (admin only)"""
    try:
        print("📋 Starting get_pending_doctors endpoint...")
        
        # Query doctor_profiles directly - get all doctors first
        print("📋 Fetching all doctors from doctor_profiles table...")
        all_response = supabase.service_client.table("doctor_profiles").select("*").execute()
        print(f"📊 Total doctors in database: {len(all_response.data)}")
        
        # Filter for pending status (including NULL)
        pending_doctors = []
        for doc in all_response.data:
            status = doc.get("verification_status")
            print(f"  🔍 Checking doctor: firebase_uid={doc.get('firebase_uid')}, status={status}, type={type(status)}")
            if status == "pending" or status is None:
                pending_doctors.append(doc)
                print(f"    ✅ Added to pending list")
            else:
                print(f"    ❌ Skipped (status={status})")
        
        print(f"✅ Found {len(pending_doctors)} pending doctors (status='pending' or NULL) out of {len(all_response.data)} total")
        
        # Sort by created_at descending
        pending_doctors.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        
        # Create a response-like object
        response_data = pending_doctors

        # Format the data properly and join with user_profiles
        doctors = []
        print(f"📝 Processing {len(response_data)} doctors from database...")
        
        for idx, doctor in enumerate(response_data):
            firebase_uid = doctor.get("firebase_uid")
            print(f"  [{idx+1}] Processing doctor with firebase_uid: {firebase_uid}")
            
            # Get user profile info
            user_info = {}
            if firebase_uid:
                try:
                    user_response = supabase.service_client.table("user_profiles").select(
                        "first_name, last_name, email, phone, created_at"
                    ).eq("firebase_uid", firebase_uid).execute()
                    
                    if user_response.data:
                        user_info = user_response.data[0]
                        print(f"      ✅ Found user: {user_info.get('first_name')} {user_info.get('last_name')} ({user_info.get('email')})")
                    else:
                        print(f"      ⚠️ No user profile found for firebase_uid: {firebase_uid}")
                except Exception as e:
                    print(f"      ❌ Error fetching user profile: {e}")
            
            # Get doctor ID - check multiple possible fields
            # The view might have NULL doctor_id, so use UUID id or firebase_uid as fallback
            doctor_id = doctor.get("id") or doctor.get("doctor_id") or doctor.get("firebase_uid")
            
            # If we still don't have an ID, try to get it from doctor_profiles table
            if not doctor_id and firebase_uid:
                try:
                    doctor_profile_check = supabase.service_client.table("doctor_profiles").select("id").eq("firebase_uid", firebase_uid).execute()
                    if doctor_profile_check.data:
                        doctor_id = doctor_profile_check.data[0].get("id")
                        print(f"      ✅ Found doctor ID from doctor_profiles: {doctor_id}")
                except Exception as e:
                    print(f"      ⚠️ Error fetching doctor ID: {e}")
            
            # Only include doctors with user info (valid accounts)
            if user_info:
                doctors.append({
                    **doctor,
                    "id": doctor_id,  # Ensure id field is set for approve/decline actions
                    "doctor_id": doctor_id,  # Also set doctor_id for consistency
                    "user_info": user_info
                })
                print(f"      ✅ Added doctor to list")
            else:
                print(f"      ⚠️ Skipping doctor {doctor_id or firebase_uid} - no user profile found")

        print(f"✅ Returning {len(doctors)} doctors with user info")
        print(f"📊 Final response: success=True, count={len(doctors)}, doctors={[d.get('user_info', {}).get('email', 'unknown') for d in doctors]}")
        
        return jsonify({
            "success": True,
            "doctors": doctors,
            "count": len(doctors)
        }), 200

    except Exception as e:
        print(f"❌ Error fetching pending doctors: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/doctors', methods=['GET'])
@firebase_role_required(["admin"])
def get_all_doctors():
    """Get all doctors with optional filtering (admin only)"""
    try:
        search = request.args.get('search', '').strip()
        verified = request.args.get('verified')

        # Build query with join to user_profiles
        query = supabase.service_client.table("doctor_profiles").select(
            "*, user_profiles:user_id(first_name, last_name, email, phone, is_active, created_at)"
        )

        if verified is not None:
            query = query.eq("is_verified", verified.lower() == "true")

        if search:
            query = query.or_(
                f"specialization.ilike.%{search}%,license_number.ilike.%{search}%"
            )

        query = query.order("created_at", desc=True)
        response = query.execute()

        return jsonify({
            "success": True,
            "doctors": response.data
        }), 200

    except Exception as e:
        print(f"❌ Error fetching doctors: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/doctors/<doctor_id>/approve', methods=['POST'])
@firebase_role_required(["admin"])
def approve_doctor_admin(doctor_id):
    """Approve doctor verification from admin dashboard (admin only)"""
    try:
        from auth.firebase_auth import firebase_auth_service
        from doctor_verification import send_doctor_notification_email
        
        # Get doctor profile - try multiple methods to find the doctor
        # First try by UUID id
        response = supabase.service_client.table("doctor_profiles").select("*").eq("id", doctor_id).execute()
        
        if not response.data:
            # Try with doctor_id field
            response = supabase.service_client.table("doctor_profiles").select("*").eq("doctor_id", doctor_id).execute()
        
        if not response.data:
            # Try with firebase_uid (in case doctor_id is actually firebase_uid)
            response = supabase.service_client.table("doctor_profiles").select("*").eq("firebase_uid", doctor_id).execute()
        
        if not response.data:
            return jsonify({"success": False, "error": "Doctor not found"}), 404
        
        doctor_profile = response.data[0]
        
        if doctor_profile.get("verification_status") != "pending":
            return jsonify({
                "success": False, 
                "error": f"Doctor verification status is already {doctor_profile.get('verification_status')}"
            }), 400
        
        # Update doctor status to approved - use the actual ID from the database
        doctor_db_id = doctor_profile.get("id") or doctor_id
        supabase.service_client.table("doctor_profiles").update({
            "verification_status": "approved",
            "verified_at": datetime.utcnow().isoformat(),
            "verification_token": None,
        }).eq("id", doctor_db_id).execute()
        
        # Update user profile
        supabase.service_client.table("user_profiles").update({
            "verification_status": "approved",
            "is_verified": True
        }).eq("firebase_uid", doctor_profile["firebase_uid"]).execute()
        
        # Get user email for notification
        user_response = supabase.service_client.table("user_profiles").select(
            "email, first_name, last_name"
        ).eq("firebase_uid", doctor_profile["firebase_uid"]).execute()
        
        if user_response.data:
            user_data = user_response.data[0]
            doctor_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            
            # Send approval email to doctor
            send_doctor_notification_email(
                user_data["email"],
                doctor_name,
                "approved",
                "Your medical credentials have been verified. Welcome to MediChain!",
            )
        
        return jsonify({
            "success": True,
            "message": "Doctor approved successfully",
            "doctor": doctor_profile
        }), 200
        
    except Exception as e:
        print(f"❌ Error approving doctor: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/doctors/<doctor_id>/decline', methods=['POST'])
@firebase_role_required(["admin"])
def decline_doctor_admin(doctor_id):
    """Decline doctor verification from admin dashboard (admin only)"""
    try:
        from doctor_verification import send_doctor_notification_email
        
        print(f"❌ Declining doctor: {doctor_id}")
        
        data = request.get_json() or {}
        reason = data.get("reason", "Application did not meet verification requirements")
        
        print(f"📝 Decline reason: {reason}")
        
        # Get doctor profile - try multiple methods to find the doctor
        # First try by UUID id
        response = supabase.service_client.table("doctor_profiles").select("*").eq("id", doctor_id).execute()
        
        if not response.data:
            # Try with doctor_id field
            response = supabase.service_client.table("doctor_profiles").select("*").eq("doctor_id", doctor_id).execute()
        
        if not response.data:
            # Try with firebase_uid (in case doctor_id is actually firebase_uid)
            response = supabase.service_client.table("doctor_profiles").select("*").eq("firebase_uid", doctor_id).execute()
        
        if not response.data:
            print(f"❌ Doctor not found: {doctor_id}")
            return jsonify({"success": False, "error": "Doctor not found"}), 404
        
        doctor_profile = response.data[0]
        print(f"✅ Found doctor: {doctor_profile.get('firebase_uid')}, status: {doctor_profile.get('verification_status')}")
        
        if doctor_profile.get("verification_status") != "pending":
            return jsonify({
                "success": False,
                "error": f"Doctor verification status is already {doctor_profile.get('verification_status')}"
            }), 400
        
        # Update doctor status to declined - use the actual ID from the database
        doctor_db_id = doctor_profile.get("id") or doctor_id
        
        # Build update data - don't include decline_reason as column doesn't exist
        update_data = {
            "verification_status": "declined",
            "declined_at": datetime.utcnow().isoformat(),
            "verification_token": None
        }
        # Note: decline_reason column doesn't exist in database, so we don't include it
        
        print(f"📝 Updating doctor_profiles with: {update_data}")
        supabase.service_client.table("doctor_profiles").update(update_data).eq("id", doctor_db_id).execute()
        print(f"✅ Doctor profile updated")
        
        # Update user profile
        print(f"📝 Updating user_profiles for firebase_uid: {doctor_profile['firebase_uid']}")
        supabase.service_client.table("user_profiles").update({
            "verification_status": "declined"
        }).eq("firebase_uid", doctor_profile["firebase_uid"]).execute()
        print(f"✅ User profile updated")
        
        # Get user email for notification
        user_response = supabase.service_client.table("user_profiles").select(
            "email, first_name, last_name"
        ).eq("firebase_uid", doctor_profile["firebase_uid"]).execute()
        
        if user_response.data:
            user_data = user_response.data[0]
            doctor_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
            
            print(f"📧 Sending decline email to: {user_data['email']}")
            # Send decline email to doctor
            try:
                send_doctor_notification_email(
                    user_data["email"],
                    doctor_name,
                    "declined",
                    reason
                )
                print(f"✅ Decline email sent")
            except Exception as email_error:
                print(f"⚠️ Error sending email: {email_error}")
                # Don't fail the request if email fails
        
        return jsonify({
            "success": True,
            "message": "Doctor application declined",
            "doctor": doctor_profile
        }), 200
        
    except Exception as e:
        print(f"❌ Error declining doctor: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


@admin_bp.route('/doctors/<doctor_id>/document', methods=['GET'])
@firebase_role_required(["admin"])
def get_doctor_document(doctor_id):
    """Get doctor verification document (admin only)"""
    try:
        import os
        from flask import send_file
        
        print(f"📄 Getting document for doctor_id: {doctor_id}")
        
        # Get doctor profile - try multiple methods to find the doctor
        response = supabase.service_client.table("doctor_profiles").select(
            "verification_file_path, firebase_uid"
        ).eq("id", doctor_id).execute()
        
        if not response.data:
            # Try with doctor_id field instead
            response = supabase.service_client.table("doctor_profiles").select(
                "verification_file_path, firebase_uid"
            ).eq("doctor_id", doctor_id).execute()
        
        if not response.data:
            # Try with firebase_uid (in case doctor_id is actually firebase_uid)
            response = supabase.service_client.table("doctor_profiles").select(
                "verification_file_path, firebase_uid"
            ).eq("firebase_uid", doctor_id).execute()
        
        if not response.data:
            print(f"❌ Doctor not found: {doctor_id}")
            return jsonify({"success": False, "error": "Doctor not found"}), 404
        
        doctor = response.data[0]
        file_path = doctor.get("verification_file_path")
        
        print(f"📄 File path from DB: {file_path}")
        
        if not file_path:
            print(f"❌ No file path found for doctor: {doctor_id}")
            return jsonify({"success": False, "error": "Document path not found"}), 404
        
        # Resolve file path - handle both relative and absolute paths
        if not os.path.isabs(file_path):
            # If relative path, resolve relative to backend directory
            # admin_routes.py is in backend/, so __file__ is backend/admin_routes.py
            # We want backend/ as the base directory
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(backend_dir, file_path)
            file_path = os.path.normpath(file_path)
        
        print(f"📄 Resolved file path: {file_path}")
        print(f"📄 File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found at path: {file_path}")
            return jsonify({"success": False, "error": f"Document not found at path: {file_path}"}), 404
        
        # Get file extension for proper MIME type
        file_ext = os.path.splitext(file_path)[1].lower()
        mimetype = None
        if file_ext == '.pdf':
            mimetype = 'application/pdf'
        elif file_ext in ['.jpg', '.jpeg']:
            mimetype = 'image/jpeg'
        elif file_ext == '.png':
            mimetype = 'image/png'
        
        return send_file(file_path, as_attachment=True, mimetype=mimetype)
        
    except Exception as e:
        print(f"❌ Error getting doctor document: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)}), 500


print("✅ Admin routes loaded!")
print("📋 Available endpoints:")
print("   - GET /api/admin/users - List all users")
print("   - GET /api/admin/users/<id> - Get user details")
print("   - POST /api/admin/users - Create user")
print("   - PUT /api/admin/users/<id> - Update user")
print("   - PUT /api/admin/users/<id>/role - Change user role")
print("   - PUT /api/admin/users/<id>/status - Update user status")
print("   - GET /api/admin/stats - Get dashboard statistics")
print("   - GET /api/admin/doctors - Get all doctors")
print("   - GET /api/admin/doctors/pending - Get pending doctor verifications")
print("   - POST /api/admin/doctors/<id>/approve - Approve doctor")
print("   - POST /api/admin/doctors/<id>/decline - Decline doctor")
print("   - GET /api/admin/doctors/<id>/document - Get verification document")
print("🔐 All endpoints require admin role")

