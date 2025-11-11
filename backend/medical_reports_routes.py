"""
Medical Reports API Routes
Handles medical reports (final diagnosis and prescription) linked to appointments
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
from auth.firebase_auth import firebase_auth_required, firebase_role_required
from db.supabase_client import SupabaseClient

medical_reports_bp = Blueprint("medical_reports", __name__, url_prefix="/api/medical-reports")

# Initialize Supabase client
try:
    supabase = SupabaseClient()
    print("✅ Supabase client initialized for medical reports routes")
except Exception as e:
    print(f"⚠️  Warning: Supabase client initialization failed in medical reports routes: {e}")
    supabase = None


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
            # No medical report found - this is normal for new appointments
            return jsonify({
                "success": False,
                "error": "Medical report not found",
                "medical_report": None
            }), 404

    except Exception as e:
        print(f"❌ Error fetching medical report: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@medical_reports_bp.route("/patient", methods=["GET"])
@firebase_auth_required
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
