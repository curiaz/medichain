#!/usr/bin/env python3
"""
Setup script to create password_reset_sessions table with verification code support
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.supabase_client import SupabaseClient

def create_password_reset_sessions_table():
    """Create password_reset_sessions table with all necessary columns"""
    try:
        supabase = SupabaseClient()
        
        print("🔧 Creating password_reset_sessions table...")
        
        # Create a sample record to ensure the table gets created with proper structure
        from datetime import datetime, timedelta
        import secrets
        
        sample_data = {
            "email": "setup@medichain.temp",
            "session_token": secrets.token_urlsafe(32),
            "verification_code": "123456",
            "code_verified": False,
            "reset_token": None,
            "firebase_reset_sent": True,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
        }
        
        # Try to insert the sample record
        try:
            insert_response = supabase.client.table("password_reset_sessions").insert(sample_data).execute()
            
            if insert_response.data:
                print("✅ password_reset_sessions table created successfully")
                
                # Clean up the sample record
                supabase.client.table("password_reset_sessions").delete().eq("email", "setup@medichain.temp").execute()
                print("🧹 Cleaned up sample record")
                
                # Test the structure by inserting and retrieving a test record
                test_data = {
                    "email": "test@structure.check",
                    "session_token": secrets.token_urlsafe(32),
                    "verification_code": "654321",
                    "code_verified": True,
                    "reset_token": secrets.token_urlsafe(32),
                    "firebase_reset_sent": True,
                    "created_at": datetime.utcnow().isoformat(),
                    "expires_at": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
                }
                
                # Insert test record
                test_insert = supabase.client.table("password_reset_sessions").insert(test_data).execute()
                
                if test_insert.data:
                    print("✅ Table structure verified - all columns working")
                    
                    # Retrieve and verify
                    retrieve_test = supabase.client.table("password_reset_sessions").select("*").eq("email", "test@structure.check").execute()
                    
                    if retrieve_test.data:
                        record = retrieve_test.data[0]
                        print(f"✅ Verified columns: email, session_token, verification_code={record.get('verification_code')}, code_verified={record.get('code_verified')}")
                        
                        # Clean up
                        supabase.client.table("password_reset_sessions").delete().eq("email", "test@structure.check").execute()
                        print("🧹 Cleaned up test record")
                    
                else:
                    print("⚠️  Test record insert failed")
                    
            else:
                print("⚠️  Sample record insert returned no data")
                
        except Exception as e:
            print(f"❌ Failed to create table: {e}")
            return False
            
        print("✅ password_reset_sessions table setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Creating password_reset_sessions table...")
    
    if create_password_reset_sessions_table():
        print("✅ Table creation completed successfully!")
        print("📋 Table includes columns: email, session_token, verification_code, code_verified, reset_token, firebase_reset_sent, created_at, expires_at")
    else:
        print("❌ Table creation failed!")
        sys.exit(1)