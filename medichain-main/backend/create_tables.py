"""
Create database tables using Supabase REST API
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

def create_tables():
    """Create tables using Supabase REST API"""
    
    # Headers for Supabase REST API
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }
    
    # SQL commands to create tables
    sql_commands = [
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL CHECK (role IN ('doctor', 'patient', 'admin')),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        """,
        """
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
    ]
    
    # Execute SQL commands
    for sql in sql_commands:
        try:
            # Use Supabase Edge Functions or direct SQL endpoint
            # Note: This approach may not work with the standard Supabase setup
            # You typically need to use the Supabase dashboard SQL editor
            print(f"Attempting to execute SQL...")
            print("Note: You may need to run this SQL manually in Supabase dashboard:")
            print(sql)
            print("-" * 50)
            
        except Exception as e:
            print(f"Error executing SQL: {e}")

if __name__ == "__main__":
    create_tables()
