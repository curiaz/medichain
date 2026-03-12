"""
Medical Reports API Routes
Handles medical reports (final diagnosis and prescription) linked to appointments
"""

from flask import Blueprint, jsonify, request
from functools import wraps
from datetime import datetime
from auth.firebase_auth import firebase_auth_required, firebase_role_required, firebase_auth_service
from db.supabase_client import SupabaseClient
from services.audit_service import audit_service

medical_reports_bp = Blueprint("medical_reports", __name__, url_prefix="/api/medical-reports")

# Initialize Supabase client
try:
    supabase = SupabaseClient()
    print("✅ Supabase client initialized for medical reports routes")
except Exception as e:
    print(f"⚠️  Warning: Supabase client initialization failed in medical reports routes: {e}")
    supabase = None


def auth_required(f):
    """Decorator that accepts both Firebase and JWT tokens"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return jsonify({"error": "No authorization header provided"}), 401
        
        try:
            token = auth_header.split(" ")[1]  # Remove 'Bearer ' prefix
        except IndexError:
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        # Try Firebase token first
        try:
            firebase_result = firebase_auth_service.verify_token(token)
            if firebase_result.get("success"):
                request.firebase_user = firebase_result
                print(f"✅ Firebase token verified for user: {firebase_result.get('email', 'unknown')}")
                return f(*args, **kwargs)
            else:
                error_msg = firebase_result.get('error', '')
                print(f"⚠️  Firebase token verification failed: {error_msg}")
                if 'kid' in error_msg.lower():
                    print(f"🔍 Token is JWT (no 'kid' claim), trying JWT fallbacks...")
        except Exception as firebase_error:
            error_str = str(firebase_error)
            print(f"⚠️  Firebase token verification exception: {error_str}")
            if "kid" in error_str.lower() or "invalid" in error_str.lower() or "malformed" in error_str.lower():
                print(f"🔍 Token is not a Firebase token (likely JWT), trying JWT fallbacks...")
        
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
                print(f"✅ Supabase JWT accepted for user: {decoded.get('email')}")
                return f(*args, **kwargs)
        except Exception as e:
            print(f"⚠️  Token decoding failed (supabase-style): {e}")
        
        # Try app-issued JWTs (medichain_token)
        try:
            from auth.auth_utils import auth_utils
            print(f"🔍 Attempting to decode JWT token (length: {len(token)})...")
            app_payload = auth_utils.decode_token(token)
            print(f"🔍 JWT decode result: {app_payload}")
            
            if app_payload and app_payload.get('email'):
                user_id = app_payload.get('user_id')
                print(f"🔍 JWT user_id: {user_id}")
                
                if user_id and supabase and supabase.service_client:
                    try:
                        print(f"🔍 Looking up user profile by id: {user_id}")
                        user_profile_response = (
                            supabase.service_client.table("user_profiles")
                            .select("firebase_uid, email, role")
                            .eq("id", user_id)
                            .execute()
                        )
                        print(f"🔍 User profile lookup result: {user_profile_response.data}")
                        
                        if user_profile_response.data:
                            user_profile = user_profile_response.data[0]
                            firebase_uid = user_profile.get('firebase_uid')
                            
                            if firebase_uid:
                                request.firebase_user = {
                                    "success": True,
                                    "uid": firebase_uid,
                                    "email": app_payload.get('email'),
                                    "role": app_payload.get('role') or user_profile.get('role')
                                }
                                print(f"✅ App JWT accepted for user: {app_payload.get('email')} (firebase_uid: {firebase_uid})")
                                return f(*args, **kwargs)
                            else:
                                print(f"⚠️  User profile found but no firebase_uid for user_id: {user_id}")
                        else:
                            # Fallback: try to find by email if user_id lookup fails
                            print(f"🔍 User profile not found by id, trying email lookup: {app_payload.get('email')}")
                            user_profile_response = (
                                supabase.service_client.table("user_profiles")
                                .select("firebase_uid, email, role")
                                .eq("email", app_payload.get('email'))
                                .execute()
                            )
                            print(f"🔍 User profile lookup by email result: {user_profile_response.data}")
                            
                            if user_profile_response.data:
                                user_profile = user_profile_response.data[0]
                                firebase_uid = user_profile.get('firebase_uid')
                                
                                if firebase_uid:
                                    request.firebase_user = {
                                        "success": True,
                                        "uid": firebase_uid,
                                        "email": app_payload.get('email'),
                                        "role": app_payload.get('role') or user_profile.get('role')
                                    }
                                    print(f"✅ App JWT accepted for user: {app_payload.get('email')} (firebase_uid: {firebase_uid}, found by email)")
                                    return f(*args, **kwargs)
                    except Exception as db_error:
                        print(f"⚠️  Database lookup failed: {db_error}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"⚠️  Missing user_id ({user_id}) or supabase client not available")
                
                # Fallback: use user_id directly if firebase_uid lookup fails
                uid = app_payload.get('user_id') or app_payload.get('uid') or app_payload.get('sub')
                print(f"⚠️  Using direct mapping with uid: {uid}")
                request.firebase_user = {
                    "success": True,
                    "uid": uid,
                    "email": app_payload.get('email'),
                    "role": app_payload.get('role')
                }
                print(f"✅ App JWT accepted for user: {app_payload.get('email')} (uid: {uid}, using direct mapping)")
                return f(*args, **kwargs)
            else:
                print(f"⚠️  JWT decode returned None or missing email: {app_payload}")
        except Exception as e:
            print(f"⚠️  App JWT decoding failed: {e}")
            import traceback
            traceback.print_exc()
        
        # All token verification methods failed
        return jsonify({
            "error": "Invalid or expired token",
            "details": "Token could not be verified as Firebase token or JWT. Please ensure you are logged in and try again."
        }), 401
    
    return decorated_function


@medical_reports_bp.route("", methods=["POST"])
@firebase_auth_required
@firebase_role_required(["doctor"])
def create_medical_report():
    """Create or update a medical report (doctors only)"""
    try:
        firebase_user = request.firebase_user
        doctor_uid = firebase_user["uid"]
        data = request.get_json()

        # Validate required fields
        if not data.get("appointment_id"):
            return jsonify({"success": False, "error": "appointment_id is required"}), 400
        
        if not data.get("patient_firebase_uid"):
            return jsonify({"success": False, "error": "patient_firebase_uid is required"}), 400

        # Check if medical report already exists for this appointment
        existing_response = (
            supabase.service_client.table("medical_records")
            .select("id")
            .eq("appointment_id", data["appointment_id"])
            .execute()
        )

        medical_report_data = {
            "appointment_id": data["appointment_id"],
            "patient_firebase_uid": data["patient_firebase_uid"],
            "doctor_firebase_uid": doctor_uid,
            "record_type": data.get("record_type", "consultation"),
            "title": data.get("title", f"Medical Report - {datetime.now().strftime('%Y-%m-%d')}"),
            "description": data.get("description", ""),
            "symptoms": data.get("symptoms", []),
            "diagnosis": data.get("diagnosis", ""),
            "treatment_plan": data.get("treatment_plan", ""),
            "medications": data.get("medications", []),
            "status": data.get("status", "active"),
            "review_status": "reviewed",  # Mark as reviewed when doctor saves the report
            "updated_at": datetime.utcnow().isoformat() + "Z"  # Ensure UTC timezone format
        }

        if existing_response.data and len(existing_response.data) > 0:
            # Update existing medical report
            report_id = existing_response.data[0]["id"]
            # Ensure review_status is set to 'reviewed' when updating
            medical_report_data["review_status"] = "reviewed"
            response = (
                supabase.service_client.table("medical_records")
                .update(medical_report_data)
                .eq("id", report_id)
                .execute()
            )
            print(f"✅ Updated medical report {report_id} for appointment {data['appointment_id']} (marked as reviewed)")
        else:
            # Create new medical report
            medical_report_data["created_at"] = datetime.utcnow().isoformat()
            # Ensure review_status is set to 'reviewed' when creating
            medical_report_data["review_status"] = "reviewed"
            response = (
                supabase.service_client.table("medical_records")
                .insert(medical_report_data)
                .execute()
            )
            print(f"✅ Created new medical report for appointment {data['appointment_id']} (marked as reviewed)")
        
        # Log to audit ledger - Medical Record Creation/Update
        try:
            doctor_profile = supabase.service_client.table('user_profiles').select('email, first_name, last_name').eq('firebase_uid', doctor_uid).execute()
            if doctor_profile.data:
                doctor_data = doctor_profile.data[0]
                doctor_email = doctor_data.get('email')
                doctor_name = f"{doctor_data.get('first_name', '')} {doctor_data.get('last_name', '')}".strip() or doctor_email
                
                action_type = "UPDATE_MEDICAL_RECORD" if existing_response.data else "CREATE_MEDICAL_RECORD"
                action_desc = f"Doctor {'updated' if existing_response.data else 'created'} medical report for appointment {data['appointment_id']}"
                
                # Get previous report for updates
                data_before = None
                if existing_response.data and existing_response.data[0]:
                    data_before = existing_response.data[0]
                
                audit_service.log_action(
                    admin_id=doctor_uid,
                    admin_email=doctor_email,
                    admin_name=doctor_name,
                    action_type=action_type,
                    action_description=action_desc,
                    entity_type="medical_record",
                    entity_id=response.data[0]['id'] if response.data else None,
                    data_before=data_before,
                    data_after=response.data[0] if response.data else None,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
        except Exception as audit_error:
            print(f"[WARNING] Error logging medical report to audit ledger: {audit_error}")
        
        # Log to audit ledger - Doctor Review of Diagnosis (Health Record Review)
        try:
            # Get doctor info
            doctor_profile = supabase.service_client.table('user_profiles').select('email, first_name, last_name').eq('firebase_uid', doctor_uid).execute()
            doctor_email = None
            doctor_name = "Unknown Doctor"
            if doctor_profile.data:
                doctor_data = doctor_profile.data[0]
                doctor_email = doctor_data.get('email')
                doctor_name = f"{doctor_data.get('first_name', '')} {doctor_data.get('last_name', '')}".strip() or doctor_email
            
            # Get patient info
            patient_profile = supabase.service_client.table('user_profiles').select('email, first_name, last_name').eq('firebase_uid', data['patient_firebase_uid']).execute()
            patient_name = "Unknown Patient"
            if patient_profile.data:
                patient_data = patient_profile.data[0]
                patient_name = f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}".strip() or patient_data.get('email', 'Unknown Patient')
            
            # Get health record ID (medical record ID)
            health_record_id = response.data[0]['id'] if response.data else None
            
            # Get diagnosis from the saved report
            diagnosis = response.data[0].get('diagnosis', '') if response.data else data.get('diagnosis', '')
            
            # Log the review action
            audit_service.log_action(
                admin_id=doctor_uid,
                admin_email=doctor_email or "unknown",
                admin_name=doctor_name,
                action_type="REVIEW_DIAGNOSIS",
                action_description=f"Dr. {doctor_name} reviewed diagnosis for patient {patient_name} (Health Record ID: {health_record_id})",
                entity_type="health_record",
                entity_id=str(health_record_id) if health_record_id else None,
                data_before=None,  # Could fetch previous diagnosis if needed
                data_after={
                    "health_record_id": health_record_id,
                    "doctor_name": doctor_name,
                    "patient_name": patient_name,
                    "diagnosis": diagnosis,
                    "appointment_id": data['appointment_id'],
                    "review_status": "reviewed"
                },
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            print(f"✅ Logged diagnosis review: Dr. {doctor_name} reviewed diagnosis for {patient_name} (Health Record ID: {health_record_id})")
        except Exception as review_audit_error:
            print(f"[WARNING] Error logging diagnosis review to audit ledger: {review_audit_error}")
            import traceback
            traceback.print_exc()

        if response.data and len(response.data) > 0:
            return jsonify({
                "success": True,
                "medical_report": response.data[0],
                "message": "Medical report saved successfully"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Failed to save medical report"
            }), 500

    except Exception as e:
        print(f"❌ Error creating/updating medical report: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@medical_reports_bp.route("/appointment/<appointment_id>", methods=["GET"])
@firebase_auth_required
def get_medical_report_by_appointment(appointment_id):
    """Get medical report for a specific appointment"""
    try:
        if not supabase or not supabase.service_client:
            return jsonify({
                "success": False,
                "error": "Database connection not available"
            }), 503

        firebase_user = request.firebase_user
        uid = firebase_user["uid"]

        # Get medical report
        try:
            response = (
                supabase.service_client.table("medical_records")
                .select("*")
                .eq("appointment_id", appointment_id)
                .execute()
            )
        except Exception as db_error:
            print(f"❌ Database error fetching medical report: {db_error}")
            import traceback
            traceback.print_exc()
            return jsonify({
                "success": False,
                "error": f"Database error: {str(db_error)}"
            }), 500

        if response.data and len(response.data) > 0:
            report = response.data[0]
            
            # Verify access: patient can see their own, doctor can see their reports
            if report.get("patient_firebase_uid") == uid or report.get("doctor_firebase_uid") == uid:
                return jsonify({
                    "success": True,
                    "medical_report": report
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "Unauthorized access to medical report"
                }), 403
        else:
            # No medical report found - this is normal for new/unreviewed appointments
            # Return 200 with success: false instead of 404 to avoid console errors
            # since this is an expected state, not an error condition
            return jsonify({
                "success": False,
                "error": "Medical report not found",
                "medical_report": None
            }), 200

    except Exception as e:
        print(f"❌ Error fetching medical report: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@medical_reports_bp.route("/patient", methods=["GET"])
@auth_required
def get_patient_medical_reports():
    """Get all medical reports for the current patient"""
    try:
        firebase_user = request.firebase_user
        patient_uid = firebase_user["uid"]

        # Get user role to verify they're a patient
        user_response = (
            supabase.service_client.table("user_profiles")
            .select("role")
            .eq("firebase_uid", patient_uid)
            .execute()
        )

        if not user_response.data:
            return jsonify({"success": False, "error": "User profile not found"}), 404

        # Get all medical reports for this patient
        response = (
            supabase.service_client.table("medical_records")
            .select("*")
            .eq("patient_firebase_uid", patient_uid)
            .order("created_at", desc=True)
            .execute()
        )

        return jsonify({
            "success": True,
            "medical_reports": response.data if response.data else []
        }), 200

    except Exception as e:
        print(f"❌ Error fetching patient medical reports: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@medical_reports_bp.route("/doctor", methods=["GET"])
@firebase_auth_required
@firebase_role_required(["doctor"])
def get_doctor_medical_reports():
    """Get all medical reports created by the current doctor with patient names"""
    try:
        firebase_user = request.firebase_user
        doctor_uid = firebase_user["uid"]

        # Get all medical reports created by this doctor
        # Use basic select and fetch patient info directly (more reliable than join)
        response = (
            supabase.service_client.table("medical_records")
            .select("*")
            .eq("doctor_firebase_uid", doctor_uid)
            .order("updated_at", desc=True)
            .order("created_at", desc=True)
            .execute()
        )
        
        # ALWAYS enrich reports with patient info - fetch directly from user_profiles table
        reports_with_patients = []
        if response.data:
            for report in response.data:
                # Fetch patient info directly from user_profiles table
                # This ensures we ALWAYS try to get patient names, never fall back to IDs
                patient_info = None
                if report.get("patient_firebase_uid"):
                    try:
                        patient_response = (
                            supabase.service_client.table("user_profiles")
                            .select("first_name, last_name, email, firebase_uid")
                            .eq("firebase_uid", report["patient_firebase_uid"])
                            .execute()
                        )
                        if patient_response.data and len(patient_response.data) > 0:
                            patient_info = patient_response.data[0]
                            print(f"✅ Fetched patient info for {report['patient_firebase_uid']}: {patient_info.get('first_name')} {patient_info.get('last_name')}")
                    except Exception as patient_err:
                        print(f"⚠️  Could not fetch patient info for {report['patient_firebase_uid']}: {patient_err}")
                        # Continue without patient info - frontend will show "Unknown Patient"
                        patient_info = None
                
                # Store patient info in consistent format for frontend
                if patient_info:
                    report["patient_info"] = patient_info
                    # Also ensure user_profiles is set for backward compatibility
                    report["user_profiles"] = patient_info
                else:
                    # If no patient info found, set to None - frontend will show "Unknown Patient"
                    # NEVER include patient_firebase_uid in the response for display purposes
                    report["patient_info"] = None
                    report["user_profiles"] = None
                
                reports_with_patients.append(report)

        return jsonify({
            "success": True,
            "medical_reports": reports_with_patients if reports_with_patients else []
        }), 200

    except Exception as e:
        print(f"❌ Error fetching doctor medical reports: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
