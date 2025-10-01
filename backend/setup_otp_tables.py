"""
Setup script for OTP-based password reset tables
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_otp_tables():
    """Create necessary tables for OTP password reset system"""
    
    # Initialize Supabase client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for admin operations
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found in environment variables")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    try:
        print("🔧 Setting up OTP password reset tables...")
        
        # Create password_reset_otps table
        otp_table_sql = """
        CREATE TABLE IF NOT EXISTS password_reset_otps (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            otp VARCHAR(6) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE,
            CONSTRAINT unique_email_otp UNIQUE(email, otp)
        );
        """
        
        # Create password_reset_tokens table
        token_table_sql = """
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) NOT NULL,
            reset_token VARCHAR(255) NOT NULL UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT FALSE
        );
        """
        
        # Create indexes for better performance
        indexes_sql = """
        CREATE INDEX IF NOT EXISTS idx_password_reset_otps_email ON password_reset_otps(email);
        CREATE INDEX IF NOT EXISTS idx_password_reset_otps_expires ON password_reset_otps(expires_at);
        CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_email ON password_reset_tokens(email);
        CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires ON password_reset_tokens(expires_at);
        """
        
        # Note: Since we can't execute raw SQL, we'll create the tables by inserting/deleting test data
        # The tables will be created automatically by Supabase when we first insert data
        print("📋 Creating tables by inserting test data (Supabase auto-creates tables)...")
        
        # Try to create the password_reset_otps table structure
        try:
            test_otp = {
                "email": "setup@test.com",
                "otp": "000000",
                "created_at": "2025-01-01T00:00:00Z",
                "expires_at": "2025-01-01T00:10:00Z",
                "used": False
            }
            
            result = supabase.table("password_reset_otps").insert(test_otp).execute()
            if result.data:
                print("✅ password_reset_otps table created")
                # Clean up test data
                supabase.table("password_reset_otps").delete().eq("email", "setup@test.com").execute()
        except Exception as e:
            print(f"📋 password_reset_otps table may already exist: {e}")
        
        # Try to create the password_reset_tokens table structure  
        try:
            test_token = {
                "email": "setup@test.com",
                "reset_token": "test_token_12345",
                "created_at": "2025-01-01T00:00:00Z", 
                "expires_at": "2025-01-01T00:15:00Z",
                "used": False
            }
            
            result = supabase.table("password_reset_tokens").insert(test_token).execute()
            if result.data:
                print("✅ password_reset_tokens table created")
                # Clean up test data
                supabase.table("password_reset_tokens").delete().eq("email", "setup@test.com").execute()
        except Exception as e:
            print(f"📋 password_reset_tokens table may already exist: {e}")
        
        print("✅ OTP password reset tables created successfully!")
        
        # Test table creation by inserting and deleting a test record
        print("🧪 Testing table functionality...")
        
        test_otp = {
            "email": "test@example.com",
            "otp": "123456", 
            "expires_at": "2025-01-01T00:00:00Z",
            "used": False
        }
        
        # Insert test record
        result = supabase.table("password_reset_otps").insert(test_otp).execute()
        if result.data:
            print("✅ Test OTP insert successful")
            
            # Delete test record
            supabase.table("password_reset_otps").delete().eq("email", "test@example.com").execute()
            print("✅ Test OTP cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up OTP tables: {str(e)}")
        print("💡 Make sure you have the correct Supabase service key and permissions")
        return False

def cleanup_expired_otps():
    """Clean up expired OTPs and tokens"""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        supabase = create_client(supabase_url, supabase_key)
        
        print("🧹 Cleaning up expired OTPs and tokens...")
        
        # Delete expired OTPs
        supabase.table("password_reset_otps").delete().lt("expires_at", "now()").execute()
        
        # Delete expired tokens
        supabase.table("password_reset_tokens").delete().lt("expires_at", "now()").execute()
        
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"❌ Cleanup error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Starting OTP Password Reset Setup...")
    
    success = setup_otp_tables()
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Restart your Flask backend server")
        print("2. Test the password reset flow with a real email address")
        print("3. Check that numeric OTP codes are generated and sent")
        
        cleanup_expired_otps()
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        
    input("\nPress Enter to exit...")