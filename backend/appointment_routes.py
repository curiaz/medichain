"""
Appointments API Routes
Handles appointment scheduling and management
"""

from flask import Blueprint, jsonify, request

from auth.firebase_auth import firebase_auth_required
from db.supabase_client import SupabaseClient

appointments_bp = Blueprint("appointments", __name__, url_prefix="/api/appointments")
# Initialize Supabase client with error handling
try:
    supabase = SupabaseClient()
    print("✅ Supabase client initialized for appointments")
except Exception as e:
    print(f"⚠️  Warning: Supabase client initialization failed in appointments: {e}")
    supabase = None


# Test route to debug
@appointments_bp.route("/test", methods=["GET"])
def test_route():
    """Test route to verify API is working"""
    return jsonify({"success": True, "message": "Appointments API is working"}), 200


@appointments_bp.route("/doctors/approved", methods=["GET"])
@firebase_auth_required
def get_approved_doctors():
    """Get list of approved doctors for appointment booking with availability"""
    try:
        print("📋 Fetching approved doctors...")
        # Fetch approved doctors from database using service_client to bypass RLS
        response = (
            supabase.service_client.table("user_profiles")
            .select("id, firebase_uid, first_name, last_name, email, verification_status")
            .eq("role", "doctor")
            .eq("verification_status", "approved")
            .execute()
        )
        print(f"✅ Found {len(response.data) if response.data else 0} approved doctors")

        if not response.data:
            return jsonify({"success": True, "doctors": [], "message": "No approved doctors available"}), 200

        # Fetch doctor profiles with specializations and availability
        doctors = []
        for user in response.data:
            try:
                doctor_profile_response = (
                    supabase.service_client.table("doctor_profiles")
                    .select("specialization, availability")
                    .eq("firebase_uid", user["firebase_uid"])
                    .execute()
                )
                
                specialization = "General Practitioner"
                availability = []
                has_availability = False
                
                if doctor_profile_response.data and len(doctor_profile_response.data) > 0:
                    specialization = doctor_profile_response.data[0].get("specialization", "General Practitioner")
                    availability = doctor_profile_response.data[0].get("availability", [])
                    # Check if doctor has any future available time slots
                    has_availability = len(availability) > 0 if isinstance(availability, list) else False
            except Exception as profile_error:
                print(f"⚠️  Error fetching profile for {user.get('email')}: {profile_error}")
                # Continue with default values if profile fetch fails
                specialization = "General Practitioner"
                availability = []
                has_availability = False

            doctors.append(
                {
                    "id": user["id"],
                    "firebase_uid": user["firebase_uid"],
                    "name": f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
                    "first_name": user.get("first_name", ""),
                    "last_name": user.get("last_name", ""),
                    "email": user.get("email", ""),
                    "specialization": specialization,
                    "verification_status": user.get("verification_status", "approved"),
                    "availability": availability,
                    "has_availability": has_availability,
                }
            )

        return jsonify({"success": True, "doctors": doctors, "count": len(doctors)}), 200

    except Exception as e:
        print(f"Error fetching approved doctors: {str(e)}")
        return jsonify({"success": False, "error": "Failed to fetch doctors", "message": str(e)}), 500


@appointments_bp.route("", methods=["GET"])
@firebase_auth_required
def get_appointments():
    """Get user's appointments"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user["uid"]

        # Get user profile to determine role
        user_response = supabase.client.table("user_profiles").select("role").eq("firebase_uid", uid).execute()
        if not user_response.data:
            return jsonify({"success": False, "error": "User profile not found"}), 404

        user_role = user_response.data[0]["role"]

        if user_role == "patient":
            # Patients see their own appointments
            response = supabase.client.table("appointments").select("*").eq("patient_firebase_uid", uid).execute()
        elif user_role == "doctor":
            # Doctors see their appointments
            response = supabase.client.table("appointments").select("*").eq("doctor_firebase_uid", uid).execute()
        else:
            return jsonify({"success": False, "error": "Unauthorized role"}), 403

        return jsonify({"success": True, "appointments": response.data}), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@appointments_bp.route("", methods=["POST"])
@firebase_auth_required
def create_appointment():
    """Create a new appointment and remove booked time from doctor availability"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user["uid"]
        data = request.get_json()

        # Validate required fields
        required_fields = ["doctor_firebase_uid", "appointment_date", "appointment_time"]
        for field in required_fields:
            if field not in data:
                return (
                    jsonify({"success": False, "error": f"Missing required field: {field}"}),
                    400,
                )

        # Get user role
        user_response = supabase.client.table("user_profiles").select("role, first_name, last_name").eq("firebase_uid", uid).execute()
        if not user_response.data:
            return jsonify({"success": False, "error": "User profile not found"}), 404

        user_role = user_response.data[0]["role"]

        if user_role != "patient":
            return jsonify({"success": False, "error": "Only patients can book appointments"}), 403

        # Check if the time slot is available in doctor's availability
        doctor_profile = (
            supabase.client.table("doctor_profiles")
            .select("availability")
            .eq("firebase_uid", data["doctor_firebase_uid"])
            .execute()
        )

        if not doctor_profile.data:
            return jsonify({"success": False, "error": "Doctor not found"}), 404

        availability = doctor_profile.data[0].get("availability", [])
        appointment_date = data["appointment_date"]
        appointment_time = data["appointment_time"]

        # Find the date in availability
        date_slot = next((slot for slot in availability if slot["date"] == appointment_date), None)
        
        if not date_slot or appointment_time not in date_slot.get("time_slots", []):
            return jsonify({"success": False, "error": "Selected time slot is not available"}), 400

        # Check if appointment already exists for this time slot
        existing_appointment = (
            supabase.client.table("appointments")
            .select("id")
            .eq("doctor_firebase_uid", data["doctor_firebase_uid"])
            .eq("appointment_date", appointment_date)
            .eq("appointment_time", appointment_time)
            .eq("status", "scheduled")
            .execute()
        )

        if existing_appointment.data:
            return jsonify({"success": False, "error": "This time slot has already been booked"}), 400

        # Create the appointment
        appointment_data = {
            "patient_firebase_uid": uid,
            "doctor_firebase_uid": data["doctor_firebase_uid"],
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "appointment_type": data.get("appointment_type", "general-practitioner"),
            "notes": data.get("notes", ""),
            "status": "scheduled"
        }

        response = supabase.client.table("appointments").insert(appointment_data).execute()

        if not response.data:
            return jsonify({"success": False, "error": "Failed to create appointment"}), 500

        # Remove the booked time slot from doctor's availability
        updated_availability = []
        for slot in availability:
            if slot["date"] == appointment_date:
                # Remove the booked time
                remaining_times = [t for t in slot["time_slots"] if t != appointment_time]
                # Only keep the date if there are remaining time slots
                if remaining_times:
                    updated_availability.append({
                        "date": slot["date"],
                        "time_slots": remaining_times
                    })
            else:
                updated_availability.append(slot)

        # Update doctor's availability
        supabase.client.table("doctor_profiles").update({
            "availability": updated_availability
        }).eq("firebase_uid", data["doctor_firebase_uid"]).execute()

        return (
            jsonify(
                {
                    "success": True,
                    "appointment": response.data[0] if response.data else None,
                    "message": "Appointment booked successfully!"
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Error creating appointment: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@appointments_bp.route("/<appointment_id>", methods=["PUT"])
@firebase_auth_required
def update_appointment(appointment_id):
    """Update an appointment"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user["uid"]
        data = request.get_json()

        # Update appointment (RLS ensures users can only update their own appointments)
        response = (
            supabase.client.table("appointments")
            .update(data)
            .eq("id", appointment_id)
            .or_(f"patient_firebase_uid.eq.{uid},doctor_firebase_uid.eq.{uid}")
            .execute()
        )

        if response.data:
            return jsonify({"success": True, "appointment": response.data[0]}), 200
        else:
            return jsonify({"success": False, "error": "Appointment not found or unauthorized"}), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Doctor Availability Routes
@appointments_bp.route("/availability", methods=["GET"])
@firebase_auth_required
def get_doctor_availability():
    """Get current doctor's availability schedule"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user["uid"]

        # Verify user is a doctor
        user_response = supabase.client.table("user_profiles").select("role").eq("firebase_uid", uid).execute()
        if not user_response.data or user_response.data[0]["role"] != "doctor":
            return jsonify({"success": False, "error": "Only doctors can access this endpoint"}), 403

        # Get doctor's availability
        response = (
            supabase.client.table("doctor_profiles")
            .select("availability")
            .eq("firebase_uid", uid)
            .execute()
        )

        if not response.data:
            return jsonify({"success": False, "error": "Doctor profile not found"}), 404

        availability = response.data[0].get("availability", [])
        return jsonify({"success": True, "availability": availability}), 200

    except Exception as e:
        print(f"Error fetching availability: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@appointments_bp.route("/availability", methods=["PUT"])
@firebase_auth_required
def update_doctor_availability():
    """Update doctor's availability schedule"""
    try:
        firebase_user = request.firebase_user
        uid = firebase_user["uid"]
        data = request.get_json()

        # Verify user is a doctor
        user_response = supabase.client.table("user_profiles").select("role").eq("firebase_uid", uid).execute()
        if not user_response.data or user_response.data[0]["role"] != "doctor":
            return jsonify({"success": False, "error": "Only doctors can update availability"}), 403

        # Validate availability data
        availability = data.get("availability", [])
        if not isinstance(availability, list):
            return jsonify({"success": False, "error": "Availability must be an array"}), 400

        # Update doctor's availability
        response = (
            supabase.client.table("doctor_profiles")
            .update({"availability": availability})
            .eq("firebase_uid", uid)
            .execute()
        )

        if not response.data:
            return jsonify({"success": False, "error": "Failed to update availability"}), 400

        return jsonify({"success": True, "availability": availability, "message": "Availability updated successfully"}), 200

    except Exception as e:
        print(f"Error updating availability: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@appointments_bp.route("/availability/<doctor_firebase_uid>", methods=["GET"])
@firebase_auth_required
def get_doctor_availability_by_uid(doctor_firebase_uid):
    """Get specific doctor's availability (for patients booking appointments)"""
    try:
        # Get doctor's availability
        response = (
            supabase.client.table("doctor_profiles")
            .select("availability")
            .eq("firebase_uid", doctor_firebase_uid)
            .execute()
        )

        if not response.data:
            return jsonify({"success": False, "error": "Doctor not found"}), 404

        availability = response.data[0].get("availability", [])
        return jsonify({"success": True, "availability": availability}), 200

    except Exception as e:
        print(f"Error fetching doctor availability: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
