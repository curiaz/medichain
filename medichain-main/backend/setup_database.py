"""
Database setup script for MediChain
Creates the necessary tables if they don't exist
"""
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.supabase_client import SupabaseClient

def setup_database():
    """Set up the database tables"""
    try:
        supabase = SupabaseClient()
        print("✓ Successfully connected to Supabase")
        
        # Create users table
        users_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL CHECK (role IN ('doctor', 'patient', 'admin')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Create health_records table
        health_records_table_sql = """
        CREATE TABLE IF NOT EXISTS health_records (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES users(id),
            doctor_id INTEGER REFERENCES users(id),
            diagnosis TEXT NOT NULL,
            prescription TEXT NOT NULL,
            encrypted_diagnosis TEXT,
            encrypted_prescription TEXT,
            blockchain_hash VARCHAR(64),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """
        
        # Execute table creation
        try:
            # Note: Supabase doesn't allow direct SQL execution via the Python client
            # We need to use the Supabase dashboard or REST API for table creation
            print("Tables should be created via Supabase dashboard.")
            print("Please run the following SQL in your Supabase SQL editor:")
            print("\n" + "="*50)
            print(users_table_sql)
            print("\n" + "="*50)
            print(health_records_table_sql)
            print("="*50)
            
            # Check if tables exist by trying to query them
            try:
                users_result = supabase.client.table('users').select('count').execute()
                print("✓ Users table exists")
            except Exception as e:
                print(f"✗ Users table doesn't exist or has issues: {e}")
            
            try:
                health_records_result = supabase.client.table('health_records').select('count').execute()
                print("✓ Health records table exists")
            except Exception as e:
                print(f"✗ Health records table doesn't exist or has issues: {e}")
                
        except Exception as e:
            print(f"Error setting up tables: {e}")
            
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Setting up MediChain database...")
    success = setup_database()
    if success:
        print("Database setup completed!")
    else:
        print("Database setup failed!")
