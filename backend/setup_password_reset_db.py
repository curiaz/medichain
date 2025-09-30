"""
Database schema setup for password reset functionality
Creates tables for OTP storage and reset token management
"""

from db.supabase_client import SupabaseClient

def create_password_reset_tables():
    """
    Create the necessary tables for password reset functionality.
    
    Note: Since Supabase doesn't allow direct SQL execution via Python client,
    run these SQL commands in your Supabase SQL editor:
    """
    
    # SQL for password reset OTPs table
    password_reset_otps_sql = """
    CREATE TABLE IF NOT EXISTS password_reset_otps (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        otp VARCHAR(6) NOT NULL,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create index for faster lookups
    CREATE INDEX IF NOT EXISTS idx_password_reset_otps_email_otp 
    ON password_reset_otps(email, otp);
    
    -- Create index for cleanup of expired OTPs
    CREATE INDEX IF NOT EXISTS idx_password_reset_otps_expires_at 
    ON password_reset_otps(expires_at);
    """
    
    # SQL for password reset tokens table
    password_reset_tokens_sql = """
    CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id SERIAL PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        reset_token VARCHAR(255) NOT NULL UNIQUE,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    
    -- Create index for faster token lookups
    CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_reset_token 
    ON password_reset_tokens(reset_token);
    
    -- Create index for cleanup of expired tokens
    CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at 
    ON password_reset_tokens(expires_at);
    
    -- Create index for email lookups
    CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_email 
    ON password_reset_tokens(email);
    """
    
    # Cleanup function for expired records
    cleanup_function_sql = """
    -- Function to clean up expired OTPs and tokens (optional)
    CREATE OR REPLACE FUNCTION cleanup_expired_password_resets()
    RETURNS void AS $$
    BEGIN
        -- Delete expired OTPs
        DELETE FROM password_reset_otps 
        WHERE expires_at < NOW();
        
        -- Delete expired tokens
        DELETE FROM password_reset_tokens 
        WHERE expires_at < NOW();
    END;
    $$ LANGUAGE plpgsql;
    
    -- Optional: Create a scheduled job to run cleanup (requires pg_cron extension)
    -- SELECT cron.schedule('cleanup-password-resets', '0 * * * *', 'SELECT cleanup_expired_password_resets();');
    """
    
    print("🔧 Password Reset Database Schema Setup")
    print("=" * 50)
    print("Run the following SQL commands in your Supabase SQL editor:")
    print()
    print("1. Password Reset OTPs Table:")
    print(password_reset_otps_sql)
    print()
    print("2. Password Reset Tokens Table:")
    print(password_reset_tokens_sql)
    print()
    print("3. Cleanup Function (Optional):")
    print(cleanup_function_sql)
    print("=" * 50)
    print()
    
    # Test connection
    try:
        supabase = SupabaseClient()
        # Try a simple query to test connection
        response = supabase.client.table("users").select("count").limit(1).execute()
        print("✅ Database connection successful")
        print("📋 Please run the SQL commands above in Supabase dashboard")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def verify_password_reset_tables():
    """
    Verify that the password reset tables exist and are accessible
    """
    try:
        supabase = SupabaseClient()
        
        # Test OTPs table
        try:
            supabase.client.table("password_reset_otps").select("count").limit(1).execute()
            print("✅ password_reset_otps table is accessible")
        except Exception as e:
            print(f"❌ password_reset_otps table error: {e}")
            
        # Test tokens table
        try:
            supabase.client.table("password_reset_tokens").select("count").limit(1).execute()
            print("✅ password_reset_tokens table is accessible")
        except Exception as e:
            print(f"❌ password_reset_tokens table error: {e}")
            
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def test_password_reset_flow():
    """
    Test the password reset database operations
    """
    try:
        supabase = SupabaseClient()
        test_email = "test@example.com"
        test_otp = "123456"
        
        print("\n🧪 Testing Password Reset Database Operations")
        print("-" * 40)
        
        # Test OTP storage
        from datetime import datetime, timedelta
        expiry_time = datetime.utcnow() + timedelta(minutes=15)
        
        otp_data = {
            "email": test_email,
            "otp": test_otp,
            "expires_at": expiry_time.isoformat(),
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Insert test OTP
        result = supabase.client.table("password_reset_otps").insert(otp_data).execute()
        if result.data:
            print("✅ OTP storage test successful")
            
            # Test OTP retrieval
            lookup_result = supabase.client.table("password_reset_otps").select("*").eq("email", test_email).eq("otp", test_otp).execute()
            if lookup_result.data:
                print("✅ OTP retrieval test successful")
            else:
                print("❌ OTP retrieval test failed")
                
            # Clean up test data
            supabase.client.table("password_reset_otps").delete().eq("email", test_email).execute()
            print("✅ Test data cleanup successful")
            
        else:
            print("❌ OTP storage test failed")
            
    except Exception as e:
        print(f"❌ Password reset test failed: {e}")

if __name__ == "__main__":
    print("🚀 MediChain Password Reset Database Setup")
    print("=" * 50)
    
    # Create tables
    create_password_reset_tables()
    
    # Verify tables (will fail until SQL is run in Supabase)
    print("\n📋 After running the SQL commands, test with:")
    print("python -c 'from setup_password_reset_db import verify_password_reset_tables, test_password_reset_flow; verify_password_reset_tables(); test_password_reset_flow()'")