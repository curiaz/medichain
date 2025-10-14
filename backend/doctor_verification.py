"""
Doctor Verification System
Handles doctor signup, verification, and approval workflow
"""

import os
import secrets
import smtplib
import uuid
from datetime import datetime, timedelta
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from auth.firebase_auth import firebase_auth_service
from db.supabase_client import SupabaseClient

doctor_verification_bp = Blueprint("doctor_verification", __name__, url_prefix="/api/auth")
# Initialize Supabase client with error handling
try:
    supabase = SupabaseClient()
    print("✅ Supabase client initialized for doctor verification")
except Exception as e:
    print(f"⚠️  Warning: Supabase client initialization failed in doctor verification: {e}")
    supabase = None

# Configuration
UPLOAD_FOLDER = "uploads/doctor_verification"
ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_verification_token():
    """Generate a secure verification token"""
    return secrets.token_urlsafe(32)


def send_admin_notification_email(doctor_data, file_path, doctor_id, verification_token):
    """Send email to admin with doctor verification request"""
    try:
        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("ADMIN_EMAIL", "medichain173@gmail.com")
        sender_password = os.getenv("ADMIN_EMAIL_PASSWORD")
        admin_email = os.getenv("ADMIN_NOTIFICATION_EMAIL", "medichain173@gmail.com")

        if not sender_password:
            print("Warning: Admin email password not configured")
            return False

        # Create message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = admin_email
        msg["Subject"] = f"Doctor Verification Request - {doctor_data['firstName']} {doctor_data['lastName']}"

        # Create HTML email body with styled buttons
        base_url = os.getenv("BASE_URL", "http://localhost:5000")
        approve_url = f"{base_url}/api/auth/verify/approve?doctorId={doctor_id}&token={verification_token}"
        decline_url = f"{base_url}/api/auth/verify/decline?doctorId={doctor_id}&token={verification_token}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #0288d1, #0277bd);
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border: 1px solid #ddd;
                }}
                .doctor-info {{
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin: 20px 0;
                    border-left: 4px solid #0288d1;
                }}
                .action-buttons {{
                    text-align: center;
                    margin: 30px 0;
                }}
                .btn {{
                    display: inline-block;
                    padding: 12px 30px;
                    margin: 0 10px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    font-size: 16px;
                    transition: all 0.3s ease;
                }}
                .btn-approve {{
                    background: linear-gradient(135deg, #4caf50, #45a049);
                    color: white;
                    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
                }}
                .btn-approve:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
                }}
                .btn-decline {{
                    background: linear-gradient(135deg, #f44336, #d32f2f);
                    color: white;
                    box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
                }}
                .btn-decline:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(244, 67, 54, 0.4);
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    padding: 20px;
                    background: #333;
                    color: white;
                    border-radius: 0 0 8px 8px;
                }}
                .warning {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    color: #856404;
                    padding: 15px;
                    border-radius: 8px;
                    margin: 20px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 MediChain Doctor Verification</h1>
                <p>New doctor registration requires your approval</p>
            </div>

            <div class="content">
                <h2>Doctor Registration Details</h2>

                <div class="doctor-info">
                    <h3>👨‍⚕️ {doctor_data['firstName']} {doctor_data['lastName']}</h3>
                    <p><strong>Email:</strong> {doctor_data['email']}</p>
                    <p><strong>Specialization:</strong> {doctor_data['specialization']}</p>
                    <p><strong>Registration Date:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Doctor ID:</strong> {doctor_id}</p>
                </div>

                <div class="warning">
                    <strong>⚠️ Important:</strong> Please review the attached verification document before making a decision.
                    This link will expire in 24 hours and can only be used once.
                </div>

                <div class="action-buttons">
                    <a href="{approve_url}" class="btn btn-approve">
                        ✅ APPROVE DOCTOR
                    </a>
                    <a href="{decline_url}" class="btn btn-decline">
                        ❌ DECLINE APPLICATION
                    </a>
                </div>

                <p><strong>Verification Document:</strong> See attached file</p>
            </div>

            <div class="footer">
                <p>© 2025 MediChain - AI-Driven Diagnosis & Blockchain Health Records</p>
                <p>Taguig City University | BSCS Thesis Project</p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, "html"))

        # Attach verification document
        if os.path.exists(file_path):
            with open(file_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            filename = os.path.basename(file_path)
            part.add_header("Content-Disposition", f"attachment; filename= {filename}")
            msg.attach(part)

        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, admin_email, text)
        server.quit()

        return True

    except Exception as e:
        print(f"Error sending admin notification email: {str(e)}")
        return False


def send_doctor_notification_email(doctor_email, doctor_name, status, message):
    """Send notification email to doctor about verification status"""
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("ADMIN_EMAIL", "medichain173@gmail.com")
        sender_password = os.getenv("ADMIN_EMAIL_PASSWORD")

        if not sender_password:
            return False

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = doctor_email
        msg["Subject"] = f"MediChain Account {status.title()} - Welcome to Our Platform!"

        if status == "approved":
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #4caf50, #45a049);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 8px 8px 0 0;
                    }}
                    .content {{
                        background: #f9f9f9;
                        padding: 30px;
                        border: 1px solid #ddd;
                    }}
                    .success-badge {{
                        background: #d4edda;
                        border: 1px solid #c3e6cb;
                        color: #155724;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 20px 0;
                        text-align: center;
                    }}
                    .login-btn {{
                        display: inline-block;
                        background: linear-gradient(135deg, #0288d1, #0277bd);
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 25px;
                        font-weight: bold;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🎉 Welcome to MediChain, Dr. {doctor_name}!</h1>
                    <p>Your account has been approved</p>
                </div>

                <div class="content">
                    <div class="success-badge">
                        <strong>✅ Account Approved Successfully!</strong>
                    </div>

                    <p>Congratulations! Your MediChain doctor account has been verified and approved.</p>

                    <p>You can now:</p>
                    <ul>
                        <li>Access your doctor dashboard</li>
                        <li>Manage patient appointments</li>
                        <li>Use AI-powered diagnostic tools</li>
                        <li>Access secure medical records</li>
                    </ul>

                    <div style="text-align: center;">
                        <a href="https://my-medichain.com/login" class="login-btn">
                            Login to Your Account
                        </a>
                    </div>

                    <p><strong>Note:</strong> {message}</p>
                </div>
            </body>
            </html>
            """
        else:
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #f44336, #d32f2f);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 8px 8px 0 0;
                    }}
                    .content {{
                        background: #f9f9f9;
                        padding: 30px;
                        border: 1px solid #ddd;
                    }}
                    .decline-badge {{
                        background: #f8d7da;
                        border: 1px solid #f5c6cb;
                        color: #721c24;
                        padding: 15px;
                        border-radius: 8px;
                        margin: 20px 0;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>MediChain Application Update</h1>
                    <p>Regarding your doctor registration</p>
                </div>

                <div class="content">
                    <div class="decline-badge">
                        <strong>Application Not Approved</strong>
                    </div>

                    <p>Dear Dr. {doctor_name},</p>

                    <p>Thank you for your interest in joining MediChain. After reviewing your application,
                    we were unable to approve your account at this time.</p>

                    <p><strong>Reason:</strong> {message}</p>

                    <p>You're welcome to reapply with updated documentation. If you have any questions,
                    please contact our support team.</p>
                </div>
            </body>
            </html>
            """

        msg.attach(MIMEText(html_body, "html"))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, doctor_email, text)
        server.quit()

        return True

    except Exception as e:
        print(f"Error sending doctor notification email: {str(e)}")
        return False


@doctor_verification_bp.route("/doctor-signup", methods=["POST", "OPTIONS"])
def doctor_signup():
    """Handle doctor signup with verification document upload"""
    
    # Handle OPTIONS request for CORS
    if request.method == "OPTIONS":
        return jsonify({"status": "OK"}), 200
    
    try:
        print(f"🩺 DOCTOR SIGNUP REQUEST - Method: {request.method}")
        print(f"📋 Form data keys: {list(request.form.keys())}")
        print(f"📎 Files: {list(request.files.keys())}")
        
        # Get form data
        email = request.form.get("email")
        password = request.form.get("password")
        first_name = request.form.get("firstName")
        last_name = request.form.get("lastName")
        specialization = request.form.get("specialization")

        print(f"👤 Doctor data: {email}, {first_name} {last_name}, {specialization}")

        # Validate required fields
        if not all([email, password, first_name, last_name, specialization]):
            missing_fields = [field for field, value in [
                ('email', email), ('password', password), ('firstName', first_name), 
                ('lastName', last_name), ('specialization', specialization)
            ] if not value]
            return jsonify({"success": False, "error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Check for verification file
        if "verificationFile" not in request.files:
            return (
                jsonify({"success": False, "error": "Verification document is required"}),
                400,
            )

        file = request.files["verificationFile"]
        if file.filename == "":
            return (
                jsonify({"success": False, "error": "No verification document selected"}),
                400,
            )

        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid file type. Please upload PDF, JPG, or PNG",
                    }
                ),
                400,
            )

        # Generate unique identifiers
        doctor_id = str(uuid.uuid4())
        verification_token = generate_verification_token()

        # Save verification file
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{doctor_id}_verification.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)

        # Create Firebase user (but with unverified status)
        firebase_result = firebase_auth_service.create_user_with_email_password(email, password)

        if not firebase_result["success"]:
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
            return (
                jsonify(
                    {
                        "success": False,
                        "error": firebase_result.get("error", "Failed to create Firebase account"),
                    }
                ),
                400,
            )

        firebase_uid = firebase_result["user"]["uid"]

        # Store doctor data in Supabase with pending status
        user_profile_data = {
            "firebase_uid": firebase_uid,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "role": "doctor",
            "verification_status": "pending",
            "created_at": datetime.utcnow().isoformat(),
        }

        doctor_profile_data = {
            "firebase_uid": firebase_uid,
            "doctor_id": doctor_id,
            "specialization": specialization,
            "verification_token": verification_token,
            "verification_file_path": file_path,
            "verification_status": "pending",
            "token_expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "created_at": datetime.utcnow().isoformat(),
        }

        # Insert into database
        user_response = supabase.service_client.table("user_profiles").insert(user_profile_data).execute()
        doctor_response = supabase.service_client.table("doctor_profiles").insert(doctor_profile_data).execute()

        if not user_response.data or not doctor_response.data:
            # Clean up Firebase user and file
            firebase_auth_service.delete_user(firebase_uid)
            if os.path.exists(file_path):
                os.remove(file_path)
            return (
                jsonify({"success": False, "error": "Failed to save doctor profile"}),
                500,
            )

        # Send notification email to admin
        doctor_data = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "specialization": specialization,
        }

        email_sent = send_admin_notification_email(doctor_data, file_path, doctor_id, verification_token)

        return (
            jsonify(
                {
                    "success": True,
                    "message": (
                        "Doctor registration submitted successfully! You will receive an "
                        "email notification once your account is reviewed."
                    ),
                    "doctor_id": doctor_id,
                    "email_sent": email_sent,
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Doctor signup error: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": "An unexpected error occurred during registration",
                }
            ),
            500,
        )


@doctor_verification_bp.route("/verify/approve", methods=["GET"])
def approve_doctor():
    """Approve doctor verification (admin link)"""
    try:
        doctor_id = request.args.get("doctorId")
        token = request.args.get("token")

        if not doctor_id or not token:
            return "Invalid verification link", 400

        # Get doctor profile
        response = supabase.service_client.table("doctor_profiles").select("*").eq("doctor_id", doctor_id).execute()

        if not response.data:
            return "Doctor not found", 404

        doctor_profile = response.data[0]

        # Validate token and expiration
        if doctor_profile["verification_token"] != token:
            return "Invalid verification token", 403

        if doctor_profile["verification_status"] != "pending":
            return "This verification link has already been used", 400

        token_expires = datetime.fromisoformat(doctor_profile["token_expires_at"].replace("Z", "+00:00"))
        if datetime.utcnow().replace(tzinfo=token_expires.tzinfo) > token_expires:
            return "Verification link has expired", 400

        # Update doctor status to approved
        supabase.service_client.table("doctor_profiles").update(
            {
                "verification_status": "approved",
                "verified_at": datetime.utcnow().isoformat(),
                "verification_token": None,  # Invalidate token
            }
        ).eq("doctor_id", doctor_id).execute()

        # Update user profile
        supabase.service_client.table("user_profiles").update({"verification_status": "approved"}).eq(
            "firebase_uid", doctor_profile["firebase_uid"]
        ).execute()

        # Get user email for notification
        user_response = (
            supabase.service_client.table("user_profiles")
            .select("email, first_name, last_name")
            .eq("firebase_uid", doctor_profile["firebase_uid"])
            .execute()
        )

        if user_response.data:
            user_data = user_response.data[0]
            doctor_name = f"{user_data['first_name']} {user_data['last_name']}"

            # Send approval email to doctor
            send_doctor_notification_email(
                user_data["email"],
                doctor_name,
                "approved",
                "Your medical credentials have been verified. Welcome to MediChain!",
            )

        return (
            """
        <html>
        <head>
            <title>Doctor Approved - MediChain</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f8ff; }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    max-width: 500px;
                    margin: 0 auto;
                }
                .success { color: #4caf50; font-size: 24px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">✅ Doctor Approved Successfully!</div>
                <h2>Dr. """
            + doctor_name
            + """ has been approved</h2>
                <p>The doctor will receive an email notification and can now access their MediChain account.</p>
            </div>
        </body>
        </html>
        """
        )

    except Exception as e:
        print(f"Approve doctor error: {str(e)}")
        return "Error processing approval", 500


@doctor_verification_bp.route("/verify/decline", methods=["GET"])
def decline_doctor():
    """Decline doctor verification (admin link)"""
    try:
        doctor_id = request.args.get("doctorId")
        token = request.args.get("token")

        if not doctor_id or not token:
            return "Invalid verification link", 400

        # Get doctor profile
        response = supabase.service_client.table("doctor_profiles").select("*").eq("doctor_id", doctor_id).execute()

        if not response.data:
            return "Doctor not found", 404

        doctor_profile = response.data[0]

        # Validate token and expiration
        if doctor_profile["verification_token"] != token:
            return "Invalid verification token", 403

        if doctor_profile["verification_status"] != "pending":
            return "This verification link has already been used", 400

        token_expires = datetime.fromisoformat(doctor_profile["token_expires_at"].replace("Z", "+00:00"))
        if datetime.utcnow().replace(tzinfo=token_expires.tzinfo) > token_expires:
            return "Verification link has expired", 400

        # Get user data before deletion
        user_response = (
            supabase.service_client.table("user_profiles")
            .select("email, first_name, last_name")
            .eq("firebase_uid", doctor_profile["firebase_uid"])
            .execute()
        )

        if user_response.data:
            user_data = user_response.data[0]
            doctor_name = f"{user_data['first_name']} {user_data['last_name']}"

            # Send decline email to doctor
            send_doctor_notification_email(
                user_data["email"],
                doctor_name,
                "declined",
                "Unable to verify medical credentials. Please contact support for more information.",
            )

        # Update status to declined (don't delete, for audit trail)
        update_doctor = (
            supabase.service_client.table("doctor_profiles")
            .update(
                {
                    "verification_status": "declined",
                    "declined_at": datetime.utcnow().isoformat(),
                    "verification_token": None,  # Invalidate token
                }
            )
            .eq("doctor_id", doctor_id)
            .execute()
        )

        update_user = (
            supabase.service_client.table("user_profiles")
            .update({"verification_status": "declined"})
            .eq("firebase_uid", doctor_profile["firebase_uid"])
            .execute()
        )

        # Clean up verification file
        if doctor_profile["verification_file_path"] and os.path.exists(doctor_profile["verification_file_path"]):
            os.remove(doctor_profile["verification_file_path"])

        return (
            """
        <html>
        <head>
            <title>Doctor Declined - MediChain</title>
            <style>
                body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #f0f8ff; }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                    max-width: 500px;
                    margin: 0 auto;
                }
                .decline { color: #f44336; font-size: 24px; margin-bottom: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="decline">❌ Doctor Application Declined</div>
                <h2>Dr. """
            + (doctor_name if "doctor_name" in locals() else "Unknown")
            + """ application has been declined</h2>
                <p>The doctor will receive an email notification with information about the decision.</p>
            </div>
        </body>
        </html>
        """
        )

    except Exception as e:
        print(f"Decline doctor error: {str(e)}")
        return "Error processing decline", 500


@doctor_verification_bp.route("/doctor-verification-submit", methods=["POST", "OPTIONS"])
def submit_doctor_verification():
    """Submit doctor verification for an existing user (after email verification)"""
    
    # Handle OPTIONS request for CORS
    if request.method == "OPTIONS":
        return jsonify({"status": "OK"}), 200
    
    try:
        print(f"Doctor verification submit - Method: {request.method}")
        print(f"Form data keys: {list(request.form.keys())}")
        print(f"Files: {list(request.files.keys())}")
        
        # Get form data
        email = request.form.get("email")
        firebase_uid = request.form.get("firebase_uid")
        specialization = request.form.get("specialization")

        print(f"Doctor verification data: {email}, firebase_uid={firebase_uid}, specialization={specialization}")

        # Validate required fields
        if not all([email, firebase_uid, specialization]):
            missing_fields = []
            if not email: missing_fields.append('email')
            if not firebase_uid: missing_fields.append('firebase_uid')
            if not specialization: missing_fields.append('specialization')
            return jsonify({"success": False, "error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Check for verification file
        if "verificationFile" not in request.files:
            return (
                jsonify({"success": False, "error": "Verification document is required"}),
                400,
            )

        file = request.files["verificationFile"]
        if file.filename == "":
            return (
                jsonify({"success": False, "error": "No verification document selected"}),
                400,
            )

        if not allowed_file(file.filename):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid file type. Please upload PDF, JPG, or PNG",
                    }
                ),
                400,
            )

        # Check if user exists
        user_check = supabase.service_client.table("user_profiles").select("*").eq("firebase_uid", firebase_uid).execute()
        if not user_check.data:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        user = user_check.data[0]
        first_name = user.get("first_name", "")
        last_name = user.get("last_name", "")

        # Generate unique identifiers
        doctor_id = str(uuid.uuid4())
        verification_token = generate_verification_token()

        # Save verification file
        filename = secure_filename(file.filename)
        file_extension = filename.rsplit(".", 1)[1].lower()
        unique_filename = f"{doctor_id}_verification.{file_extension}"
        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)

        # Update user_profile to set verification_status to pending
        supabase.service_client.table("user_profiles").update({
            "verification_status": "pending"
        }).eq("firebase_uid", firebase_uid).execute()

        # Create doctor_profile entry
        doctor_profile_data = {
            "firebase_uid": firebase_uid,
            "doctor_id": doctor_id,
            "specialization": specialization,
            "verification_token": verification_token,
            "verification_file_path": file_path,
            "verification_status": "pending",
            "token_expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat(),
            "created_at": datetime.utcnow().isoformat(),
        }

        doctor_response = supabase.service_client.table("doctor_profiles").insert(doctor_profile_data).execute()

        if not doctor_response.data:
            # Clean up file
            if os.path.exists(file_path):
                os.remove(file_path)
            return (
                jsonify({"success": False, "error": "Failed to save doctor profile"}),
                500,
            )

        # Send notification email to admin
        doctor_data = {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "specialization": specialization,
        }

        email_sent = send_admin_notification_email(doctor_data, file_path, doctor_id, verification_token)

        return (
            jsonify(
                {
                    "success": True,
                    "message": (
                        "Doctor verification request submitted successfully! You will receive an "
                        "email notification once your account is reviewed."
                    ),
                    "doctor_id": doctor_id,
                    "email_sent": email_sent,
                }
            ),
            201,
        )

    except Exception as e:
        print(f"Doctor verification submit error: {str(e)}")
        import traceback
        traceback.print_exc()
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Failed to submit verification: {str(e)}",
                }
            ),
            500,
        )
