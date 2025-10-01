"""
Temporary OTP Storage Service
Handles database operations for 5-minute expiring OTPs
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import random
import os
import sys

# Add the parent directory to path to import db module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db.supabase_client import SupabaseClient

class TemporaryOTPService:
    """Service for managing temporary OTP storage with 5-minute expiration"""
    
    def __init__(self):
        self.supabase = SupabaseClient()
        self.table_name = "temporary_otp_storage"
    
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
            # Clean up any existing OTPs for this email
            self.cleanup_expired_otps()
            self.supabase.client.table(self.table_name).delete().eq("email", email).execute()
            
            # Generate new OTP and session token
            otp_code = self.generate_otp()
            session_token = self.generate_session_token()
            
            # Calculate expiration time (5 minutes from now)
            created_at = datetime.utcnow()
            expires_at = created_at + timedelta(minutes=5)
            
            otp_data = {
                "email": email,
                "otp_code": otp_code,
                "session_token": session_token,
                "firebase_reset_link": firebase_reset_link,
                "created_at": created_at.isoformat(),
                "expires_at": expires_at.isoformat(),
                "is_used": False
            }
            
            # Insert into database
            response = self.supabase.client.table(self.table_name).insert(otp_data).execute()
            
            if response.data:
                print(f"✅ OTP stored for {email}: {otp_code} (expires in 5 minutes)")
                return {
                    "success": True,
                    "otp_code": otp_code,
                    "session_token": session_token,
                    "expires_at": expires_at.isoformat()
                }
            else:
                print(f"❌ Failed to store OTP for {email}")
                return {"success": False, "error": "Failed to store OTP"}
                
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
            # Clean up expired OTPs first
            self.cleanup_expired_otps()
            
            # Find valid OTP for this email
            response = self.supabase.client.table(self.table_name).select("*").eq("email", email).eq("is_used", False).execute()
            
            if not response.data:
                return {"success": False, "error": "No valid OTP found. Please request a new password reset."}
            
            otp_record = response.data[0]
            
            # Check if OTP has expired
            expires_at = datetime.fromisoformat(otp_record["expires_at"])
            if datetime.utcnow() > expires_at:
                # Remove expired OTP
                self.supabase.client.table(self.table_name).delete().eq("id", otp_record["id"]).execute()
                return {"success": False, "error": "OTP has expired. Please request a new password reset."}
            
            # Verify OTP code
            if otp_record["otp_code"] != otp_code:
                return {"success": False, "error": "Invalid OTP code. Please check your email and try again."}
            
            # Mark OTP as used
            self.supabase.client.table(self.table_name).update({"is_used": True}).eq("id", otp_record["id"]).execute()
            
            print(f"✅ OTP verified successfully for {email}")
            return {
                "success": True,
                "session_token": otp_record["session_token"],
                "firebase_reset_link": otp_record["firebase_reset_link"],
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
            self.cleanup_expired_otps()
            
            response = self.supabase.client.table(self.table_name).select("*").eq("email", email).eq("is_used", False).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            print(f"❌ Error getting OTP info: {str(e)}")
            return None
    
    def cleanup_expired_otps(self) -> int:
        """
        Clean up expired OTPs from the database
        
        Returns:
            Number of expired OTPs removed
        """
        try:
            current_time = datetime.utcnow().isoformat()
            
            # Get expired OTPs
            expired_response = self.supabase.client.table(self.table_name).select("id").lt("expires_at", current_time).execute()
            
            expired_count = len(expired_response.data) if expired_response.data else 0
            
            if expired_count > 0:
                # Delete expired OTPs
                self.supabase.client.table(self.table_name).delete().lt("expires_at", current_time).execute()
                print(f"🧹 Cleaned up {expired_count} expired OTPs")
            
            return expired_count
            
        except Exception as e:
            print(f"⚠️  Cleanup error: {str(e)}")
            return 0
    
    def cleanup_all_otps(self) -> int:
        """
        Remove all OTPs from storage (for development/testing)
        
        Returns:
            Number of OTPs removed
        """
        try:
            # Get all OTPs
            all_response = self.supabase.client.table(self.table_name).select("id").execute()
            
            total_count = len(all_response.data) if all_response.data else 0
            
            if total_count > 0:
                # Delete all OTPs
                self.supabase.client.table(self.table_name).delete().neq("id", 0).execute()
                print(f"🧹 Removed all {total_count} OTPs from storage")
            
            return total_count
            
        except Exception as e:
            print(f"⚠️  Full cleanup error: {str(e)}")
            return 0

# Global instance
otp_service = TemporaryOTPService()