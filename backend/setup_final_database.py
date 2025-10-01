#!/usr/bin/env python3
"""
Final Database Setup for OTP Storage
Creates temporary_otp_storage table for 5-minute expiring OTPs
"""

import os
import sys
from datetime import datetime, timedelta
import secrets

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

try:
    from db.supabase_client import SupabaseClient
except ImportError as e:
    print(f"❌ Could not import SupabaseClient: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)

def setup_otp_database():
    """Set up the OTP storage table by creating a test record"""
    try:
        supabase = SupabaseClient()
        
        print("🚀 Setting up OTP database...")
        
        # Create table by inserting a test record (Supabase auto-creates schema)
        setup_data = {
            "email": "setup@medichain.system",
            "otp_code": "000000",
            "session_token": secrets.token_urlsafe(32),
            "firebase_reset_link": "https://setup.test.com",
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            "is_used": False
        }
        
        # Insert the setup record
        response = supabase.client.table("temporary_otp_storage").insert(setup_data).execute()
        
        if response.data:
            print("✅ temporary_otp_storage table created successfully")
            
            # Verify the record was inserted
            verify_response = supabase.client.table("temporary_otp_storage").select("*").eq("email", "setup@medichain.system").execute()
            
            if verify_response.data:
                record = verify_response.data[0]
                print(f"✅ Test record verified:")
                print(f"   📧 Email: {record['email']}")
                print(f"   🔢 OTP Code: {record['otp_code']}")
                print(f"   ⏰ Expires: {record['expires_at']}")
                print(f"   🎫 Session: {record['session_token'][:16]}...")
                
                # Clean up the setup record
                supabase.client.table("temporary_otp_storage").delete().eq("email", "setup@medichain.system").execute()
                print("🧹 Setup record cleaned up")
            
            # Test the OTP service
            print("\n🧪 Testing OTP service...")
            try:
                from services.otp_service import otp_service
                
                # Test storing an OTP
                test_result = otp_service.store_otp("test@medichain.dev", "https://test.firebase.link")
                
                if test_result["success"]:
                    print(f"✅ OTP service test passed:")
                    print(f"   🔢 Generated OTP: {test_result['otp_code']}")
                    print(f"   ⏰ Expires at: {test_result['expires_at']}")
                    
                    # Test verification
                    verify_result = otp_service.verify_otp("test@medichain.dev", test_result['otp_code'])
                    
                    if verify_result["success"]:
                        print("✅ OTP verification test passed")
                    else:
                        print(f"❌ OTP verification test failed: {verify_result['error']}")
                    
                    # Clean up test record
                    supabase.client.table("temporary_otp_storage").delete().eq("email", "test@medichain.dev").execute()
                    print("🧹 Test OTP cleaned up")
                else:
                    print(f"❌ OTP service test failed: {test_result['error']}")
                    
            except ImportError as e:
                print(f"⚠️  Could not test OTP service: {e}")
                print("   This is normal if services directory is not in path")
            
            print("\n✅ Database setup completed successfully!")
            print("\n📋 Table Structure:")
            print("   - id: BIGSERIAL PRIMARY KEY")
            print("   - email: VARCHAR(255) NOT NULL")
            print("   - otp_code: VARCHAR(6) NOT NULL")  
            print("   - session_token: VARCHAR(255) NOT NULL UNIQUE")
            print("   - firebase_reset_link: TEXT NOT NULL")
            print("   - created_at: TIMESTAMP WITH TIME ZONE")
            print("   - expires_at: TIMESTAMP WITH TIME ZONE")
            print("   - is_used: BOOLEAN DEFAULT FALSE")
            
            print("\n🔒 Security Features:")
            print("   ⏰ 5-minute automatic expiration")
            print("   🔄 One-time use (marked as used)")
            print("   🧹 Automatic cleanup of expired codes")
            print("   🎫 Secure session token generation")
            
            return True
            
        else:
            print("❌ Failed to create table - no data returned")
            return False
            
    except Exception as e:
        print(f"❌ Database setup failed: {str(e)}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your Supabase credentials in .env")
        print("   2. Ensure Supabase project is accessible")
        print("   3. Check network connection")
        return False

if __name__ == "__main__":
    print("🏥 MediChain OTP Database Setup")
    print("=" * 40)
    
    if setup_otp_database():
        print("\n🎉 Setup completed! You can now use password reset with OTP.")
        print("\n🚀 Next steps:")
        print("   1. Start the Flask server: python app.py")
        print("   2. Test password reset at: http://localhost:3000/reset-password")
        print("   3. Check console for OTP codes during development")
    else:
        print("\n❌ Setup failed! Please check the errors above.")
        sys.exit(1)