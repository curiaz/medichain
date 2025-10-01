"""
Simplified OTP Manager - In-memory storage with database fallback
Works without requiring manual table creation
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import random
import time

class SimpleOTPManager:
    """Simple OTP manager with in-memory storage and 5-minute expiration"""
    
    def __init__(self):
        self.otp_storage = {}  # In-memory storage for development
        self.cleanup_interval = 60  # Clean up every 60 seconds
        self.last_cleanup = time.time()
    
    def _cleanup_expired(self):
        """Clean up expired OTPs"""
        current_time = time.time()
        
        # Only cleanup if enough time has passed
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
            
        expired_emails = []
        for email, data in self.otp_storage.items():
            if current_time > data['expires_timestamp']:
                expired_emails.append(email)
        
        for email in expired_emails:
            del self.otp_storage[email]
            print(f"🧹 Cleaned up expired OTP for {email}")
        
        self.last_cleanup = current_time
    
    def generate_otp(self) -> str:
        """Generate a 6-digit OTP code"""
        return str(random.randint(100000, 999999))
    
    def generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def store_otp(self, email: str, firebase_reset_link: str) -> Dict[str, Any]:
        """
        Store OTP with 5-minute expiration
        
        Args:
            email: User's email address
            firebase_reset_link: Firebase password reset URL
            
        Returns:
            Dict containing success status, otp_code, and session_token
        """
        try:
            self._cleanup_expired()
            
            # Generate new OTP and session token
            otp_code = self.generate_otp()
            session_token = self.generate_session_token()
            
            # Calculate expiration time (5 minutes from now)
            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(minutes=5)
            expires_timestamp = time.time() + (5 * 60)  # 5 minutes in seconds
            
            # Store in memory
            self.otp_storage[email] = {
                "otp_code": otp_code,
                "session_token": session_token,
                "firebase_reset_link": firebase_reset_link,
                "created_at": created_at.isoformat(),
                "expires_at": expires_at.isoformat(),
                "expires_timestamp": expires_timestamp,
                "is_used": False
            }
            
            print(f"✅ OTP stored for {email}: {otp_code} (expires in 5 minutes)")
            return {
                "success": True,
                "otp_code": otp_code,
                "session_token": session_token,
                "expires_at": expires_at.isoformat()
            }
                
        except Exception as e:
            print(f"❌ OTP storage error: {str(e)}")
            return {"success": False, "error": f"Storage error: {str(e)}"}
    
    def verify_otp(self, email: str, otp_code: str) -> Dict[str, Any]:
        """
        Verify OTP code for given email
        
        Args:
            email: User's email address
            otp_code: 6-digit OTP code to verify
            
        Returns:
            Dict containing success status and session info
        """
        try:
            self._cleanup_expired()
            
            # Check if OTP exists for this email
            if email not in self.otp_storage:
                return {"success": False, "error": "No valid OTP found. Please request a new password reset."}
            
            otp_data = self.otp_storage[email]
            
            # Check if OTP has been used
            if otp_data.get("is_used", False):
                return {"success": False, "error": "OTP has already been used. Please request a new password reset."}
            
            # Check if OTP has expired
            if time.time() > otp_data["expires_timestamp"]:
                del self.otp_storage[email]
                return {"success": False, "error": "OTP has expired. Please request a new password reset."}
            
            # Verify OTP code
            if otp_data["otp_code"] != otp_code:
                return {"success": False, "error": "Invalid OTP code. Please check your email and try again."}
            
            # Mark OTP as used
            self.otp_storage[email]["is_used"] = True
            
            print(f"✅ OTP verified successfully for {email}")
            return {
                "success": True,
                "session_token": otp_data["session_token"],
                "firebase_reset_link": otp_data["firebase_reset_link"],
                "message": "OTP verified successfully"
            }
            
        except Exception as e:
            print(f"❌ OTP verification error: {str(e)}")
            return {"success": False, "error": f"Verification error: {str(e)}"}
    
    def get_otp_info(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get OTP information for given email (for development/debugging)
        
        Args:
            email: User's email address
            
        Returns:
            Dict containing OTP info or None if not found
        """
        try:
            self._cleanup_expired()
            
            if email in self.otp_storage and not self.otp_storage[email].get("is_used", False):
                return self.otp_storage[email]
            return None
            
        except Exception as e:
            print(f"❌ Error getting OTP info: {str(e)}")
            return None
    
    def cleanup_all_otps(self) -> int:
        """
        Remove all OTPs from storage (for development/testing)
        
        Returns:
            Number of OTPs removed
        """
        count = len(self.otp_storage)
        self.otp_storage.clear()
        print(f"🧹 Removed all {count} OTPs from storage")
        return count

# Global instance
simple_otp_manager = SimpleOTPManager()