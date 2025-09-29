import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Blueprint, jsonify, request

contact_bp = Blueprint("contact", __name__)


@contact_bp.route("/contact", methods=["POST"])
def send_contact_email():
    """
    Handle contact form submissions and send emails to medichain173@gmail.com

    Expected JSON payload:
    {
        "name": "User's full name",
        "email": "user@example.com",
        "phone": "Optional phone number",
        "subject": "Message subject",
        "message": "Message content"
    }

    Returns:
    - 200: Success with confirmation message
    - 400: Validation error (missing fields, invalid email)
    - 500: Server error (email service issues)
    """
    try:
        # Get form data
        data = request.get_json()

        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        phone = data.get("phone", "").strip()
        subject = data.get("subject", "").strip()
        message = data.get("message", "").strip()

        # Validate required fields
        if not all([name, email, subject, message]):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Please fill in all required fields (name, email, subject, message)",
                    }
                ),
                400,
            )

        # Basic email validation
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            return (
                jsonify(
                    {"success": False, "error": "Please enter a valid email address"}
                ),
                400,
            )

        # Length validation for security
        if (
            len(name) > 100
            or len(email) > 100
            or len(subject) > 200
            or len(message) > 2000
        ):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "One or more fields exceed maximum length limits",
                    }
                ),
                400,
            )

        # Basic spam protection - check for suspicious content
        spam_keywords = [
            "spam",
            "viagra",
            "casino",
            "lottery",
            "winner",
            "click here",
            "buy now",
        ]
        content_to_check = f"{subject} {message}".lower()
        if any(keyword in content_to_check for keyword in spam_keywords):
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Message content flagged by spam filter",
                    }
                ),
                400,
            )

        # Email configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = os.getenv("GMAIL_USER")  # Your Gmail address
        sender_password = os.getenv("GMAIL_APP_PASSWORD")  # Gmail App Password
        recipient_email = "medichain173@gmail.com"

        if not sender_email or not sender_password:
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Email service is temporarily unavailable. Please try again later or contact support.",
                    }
                ),
                500,
            )

        # Create email message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = f"New Contact Form Submission – {subject}"

        # Email body
        email_body = f"""
📧 NEW CONTACT FORM SUBMISSION - MEDICHAIN

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 Date & Time: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
👤 Contact Name: {name}
📧 Email Address: {email}
📱 Phone Number: {phone if phone else 'Not provided'}
📋 Subject: {subject}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💬 MESSAGE:

{message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏥 This message was sent from the MediChain contact form.
✅ Reply directly to this email to respond to {name} at {email}.
🌐 Visit: localhost:3001

Best regards,
MediChain Contact System
        """

        msg.attach(MIMEText(email_body, "plain"))

        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return (
            jsonify(
                {
                    "success": True,
                    "message": "Your message has been sent successfully! We will get back to you soon.",
                }
            ),
            200,
        )

    except smtplib.SMTPAuthenticationError:
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Email authentication failed. Please contact support.",
                }
            ),
            500,
        )
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Failed to send email. Please try again later.",
                }
            ),
            500,
        )
    except Exception as e:
        print(f"Contact form error: {str(e)}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": "An unexpected error occurred. Please try again later.",
                }
            ),
            500,
        )
