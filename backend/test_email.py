"""
Test email notification system
"""
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

def test_email():
    """Test if email configuration works"""
    print("🔍 Testing email configuration...")
    
    # Get email settings
    sender_email = os.getenv("ADMIN_EMAIL")
    sender_password = os.getenv("ADMIN_EMAIL_PASSWORD")
    admin_email = os.getenv("ADMIN_NOTIFICATION_EMAIL")
    
    print(f"Sender Email: {sender_email}")
    print(f"Password configured: {'Yes' if sender_password else 'No'}")
    print(f"Admin Email: {admin_email}")
    
    if not sender_password:
        print("❌ ADMIN_EMAIL_PASSWORD not set in .env")
        return False
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = admin_email
        msg["Subject"] = "MediChain Test - Email Configuration Check"
        
        html_body = """
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #4caf50;">✅ Email Configuration Test</h2>
            <p>This is a test email from your MediChain backend.</p>
            <p>If you received this, your email configuration is working correctly!</p>
            <hr>
            <p><small>MediChain - AI-Driven Diagnosis System</small></p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, "html"))
        
        print("\n📤 Connecting to Gmail SMTP server...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        
        print("🔐 Logging in...")
        server.login(sender_email, sender_password)
        
        print("📧 Sending test email...")
        server.sendmail(sender_email, admin_email, msg.as_string())
        server.quit()
        
        print(f"\n✅ SUCCESS! Test email sent to {admin_email}")
        print("Check your inbox!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPossible issues:")
        print("1. Gmail App Password might be incorrect")
        print("2. 2-Step Verification not enabled on Gmail account")
        print("3. Network/firewall blocking SMTP port 587")
        return False

if __name__ == "__main__":
    test_email()

