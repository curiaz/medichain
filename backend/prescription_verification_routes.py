"""
Prescription Verification API Routes
Handles QR code verification for e-prescriptions
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from db.supabase_client import SupabaseClient
import secrets
import hashlib

prescription_verification_bp = Blueprint("prescription_verification", __name__, url_prefix="/api/prescription")

# Initialize Supabase client
try:
    supabase = SupabaseClient()
    print("✅ Supabase client initialized for prescription verification routes")
except Exception as e:
    print(f"⚠️  Warning: Supabase client initialization failed: {e}")
    supabase = None


def generate_secure_token(appointment_id: str) -> str:
    """Generate a secure token for prescription verification"""
    # Create a hash of appointment_id + timestamp + random secret
    secret_key = secrets.token_urlsafe(32)
    timestamp = datetime.utcnow().isoformat()
    data = f"{appointment_id}:{timestamp}:{secret_key}"
    token = hashlib.sha256(data.encode()).hexdigest()[:16]  # 16 char token
    return token


@prescription_verification_bp.route("/verify/<appointment_id>", methods=["GET"])
def verify_prescription(appointment_id):
    """
    Verify prescription by appointment ID
    Checks:
    - Does prescription ID exist?
    - Is it marked as active?
    - Has it already been claimed/dispensed?
    - Is the doctor ID valid?
    """
    try:
        if not supabase or not supabase.service_client:
            return jsonify({
                "success": False,
                "valid": False,
                "error": "Database connection not available"
            }), 503

        # Get medical record (prescription) by appointment_id
        medical_record_response = (
            supabase.service_client.table("medical_records")
            .select("*")
            .eq("appointment_id", appointment_id)
            .execute()
        )

        # Check 1: Does prescription exist?
        if not medical_record_response.data or len(medical_record_response.data) == 0:
            return jsonify({
                "success": True,
                "valid": False,
                "error": "INVALID_PRESCRIPTION",
                "message": "Prescription not found",
                "details": "This prescription ID does not exist in our system."
            }), 200

        medical_record = medical_record_response.data[0]

        # Check 2: Is it marked as active?
        status = medical_record.get("status", "active")
        if status not in ["active", "resolved"]:
            return jsonify({
                "success": True,
                "valid": False,
                "error": "NOT_ACTIVE",
                "message": "Prescription is not active",
                "details": f"This prescription has been {status}."
            }), 200

        # Check 3: Has it been claimed/dispensed?
        # Check if there's a dispensed_at field or status indicating it's been used
        dispensed_at = medical_record.get("dispensed_at")
        if dispensed_at:
            return jsonify({
                "success": True,
                "valid": False,
                "error": "ALREADY_DISPENSED",
                "message": "Prescription already dispensed",
                "details": f"This prescription was already dispensed on {dispensed_at}.",
                "dispensed_at": dispensed_at
            }), 200

        # Check expiry date if exists
        expiry_date = medical_record.get("expiry_date")
        if expiry_date:
            try:
                expiry = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                if expiry < datetime.now(expiry.tzinfo):
                    return jsonify({
                        "success": True,
                        "valid": False,
                        "error": "EXPIRED",
                        "message": "Prescription expired",
                        "details": f"This prescription expired on {expiry_date}.",
                        "expiry_date": expiry_date
                    }), 200
            except (ValueError, AttributeError):
                # If date parsing fails, continue with other checks
                pass

        # Check 4: Is the doctor ID valid?
        doctor_uid = medical_record.get("doctor_firebase_uid")
        if doctor_uid:
            doctor_response = (
                supabase.service_client.table("user_profiles")
                .select("firebase_uid, first_name, last_name, verification_status, role")
                .eq("firebase_uid", doctor_uid)
                .execute()
            )

            if not doctor_response.data:
                return jsonify({
                    "success": True,
                    "valid": False,
                    "error": "INVALID_DOCTOR",
                    "message": "Invalid doctor",
                    "details": "The prescribing doctor is not found in our system."
                }), 200

            doctor = doctor_response.data[0]
            if doctor.get("role") != "doctor":
                return jsonify({
                    "success": True,
                    "valid": False,
                    "error": "INVALID_DOCTOR",
                    "message": "Invalid doctor",
                    "details": "The prescriber is not a verified doctor."
                }), 200

            if doctor.get("verification_status") != "approved":
                return jsonify({
                    "success": True,
                    "valid": False,
                    "error": "DOCTOR_NOT_VERIFIED",
                    "message": "Doctor not verified",
                    "details": "The prescribing doctor is not verified."
                }), 200

            doctor_name = f"Dr. {doctor.get('first_name', '')} {doctor.get('last_name', '')}".strip()
        else:
            doctor_name = "Unknown Doctor"

        # Get patient information
        patient_uid = medical_record.get("patient_firebase_uid")
        patient_name = "Unknown Patient"
        if patient_uid:
            patient_response = (
                supabase.service_client.table("user_profiles")
                .select("first_name, last_name")
                .eq("firebase_uid", patient_uid)
                .execute()
            )
            if patient_response.data:
                patient = patient_response.data[0]
                patient_name = f"{patient.get('first_name', '')} {patient.get('last_name', '')}".strip()

        # Get appointment for date information
        appointment_response = (
            supabase.service_client.table("appointments")
            .select("appointment_date, appointment_time")
            .eq("id", appointment_id)
            .execute()
        )

        appointment_date = None
        if appointment_response.data:
            appointment = appointment_response.data[0]
            appointment_date = f"{appointment.get('appointment_date')} {appointment.get('appointment_time', '')}"

        # All checks passed - prescription is valid
        return jsonify({
            "success": True,
            "valid": True,
            "prescription": {
                "appointment_id": appointment_id,
                "patient_name": patient_name,
                "doctor_name": doctor_name,
                "medications": medical_record.get("medications", []),
                "diagnosis": medical_record.get("diagnosis", ""),
                "instructions": medical_record.get("treatment_plan", ""),
                "date": appointment_date or medical_record.get("created_at", ""),
                "expiry_date": expiry_date,
                "status": status
            }
        }), 200

    except Exception as e:
        print(f"❌ Error verifying prescription: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "valid": False,
            "error": "SYSTEM_ERROR",
            "message": "System error",
            "details": str(e)
        }), 500


@prescription_verification_bp.route("/mark-dispensed/<appointment_id>", methods=["POST"])
def mark_prescription_dispensed(appointment_id):
    """
    Mark prescription as dispensed (for pharmacy use)
    """
    try:
        if not supabase or not supabase.service_client:
            return jsonify({
                "success": False,
                "error": "Database connection not available"
            }), 503

        # Update medical record to mark as dispensed
        update_data = {
            "dispensed_at": datetime.utcnow().isoformat() + "Z",
            "status": "completed",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }

        response = (
            supabase.service_client.table("medical_records")
            .update(update_data)
            .eq("appointment_id", appointment_id)
            .execute()
        )

        if response.data:
            return jsonify({
                "success": True,
                "message": "Prescription marked as dispensed"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Prescription not found"
            }), 404

    except Exception as e:
        print(f"❌ Error marking prescription as dispensed: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

