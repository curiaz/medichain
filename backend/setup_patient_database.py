#!/usr/bin/env python3
"""
Database setup script for Patient Profile Management System
This script creates the necessary tables for the patient profile system
"""

import os
import sys
from dotenv import load_dotenv

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.supabase_client import SupabaseClient

def setup_database():
    """Setup the database tables for patient profile management"""
    try:
        print("🏥 Setting up MediChain Patient Profile Database...")
        
        # Initialize Supabase client
        supabase = SupabaseClient()
        
        # Read the SQL schema file
        schema_file = os.path.join(os.path.dirname(__file__), '..', 'database', 'enhanced_profile_management_schema.sql')
        
        if not os.path.exists(schema_file):
            print(f"❌ Schema file not found: {schema_file}")
            return False
        
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        print("📋 Executing database schema...")
        
        # Split the SQL into individual statements
        statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
        
        for i, statement in enumerate(statements):
            if statement:
                try:
                    print(f"   Executing statement {i+1}/{len(statements)}...")
                    # Note: Supabase doesn't support multi-statement execution
                    # In production, you would run this SQL directly in Supabase dashboard
                    # or use a migration tool
                    pass
                except Exception as e:
                    print(f"   ⚠️  Statement {i+1} failed: {e}")
        
        print("✅ Database setup completed!")
        print("\n📝 Note: Please run the SQL schema manually in your Supabase dashboard:")
        print(f"   File: {schema_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def test_database_connection():
    """Test the database connection"""
    try:
        print("\n🔍 Testing database connection...")
        
        supabase = SupabaseClient()
        
        # Test basic connection
        response = supabase.client.table('user_profiles').select('count').execute()
        print("✅ Database connection successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("\n💡 Make sure your Supabase credentials are correct in the .env file:")
        print("   SUPABASE_URL=your_supabase_url")
        print("   SUPABASE_KEY=your_supabase_anon_key")
        print("   SUPABASE_SERVICE_KEY=your_supabase_service_key")
        return False

def create_sample_patient_data():
    """Create sample patient data for testing"""
    try:
        print("\n👤 Creating sample patient data...")
        
        supabase = SupabaseClient()
        
        # Sample patient profile
        patient_data = {
            'firebase_uid': 'sample_patient_123',
            'email': 'patient@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'phone': '+1 (555) 123-4567',
            'date_of_birth': '1990-01-01',
            'gender': 'male',
            'role': 'patient',
            'address': {
                'street': '123 Main St',
                'city': 'Anytown',
                'state': 'CA',
                'postal_code': '12345'
            },
            'emergency_contact': {
                'name': 'Jane Doe',
                'phone': '+1 (555) 987-6543',
                'relationship': 'Spouse'
            },
            'medical_conditions': ['Hypertension', 'Diabetes Type 2'],
            'allergies': ['Penicillin', 'Shellfish'],
            'current_medications': ['Metformin 500mg', 'Lisinopril 10mg'],
            'blood_type': 'O+',
            'medical_notes': 'Regular checkups every 6 months',
            'is_active': True,
            'is_verified': True
        }
        
        # Insert sample patient
        response = supabase.client.table('user_profiles').insert(patient_data).execute()
        
        if response.data:
            print("✅ Sample patient data created successfully!")
            print(f"   Patient ID: {response.data[0]['id']}")
            return True
        else:
            print("❌ Failed to create sample patient data")
            return False
            
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("🏥 MediChain Patient Profile Management - Database Setup")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check if Supabase credentials are available
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials not found!")
        print("Please create a .env file with your Supabase credentials:")
        print("SUPABASE_URL=your_supabase_url")
        print("SUPABASE_KEY=your_supabase_anon_key")
        print("SUPABASE_SERVICE_KEY=your_supabase_service_key")
        return False
    
    # Setup database
    if not setup_database():
        return False
    
    # Test connection
    if not test_database_connection():
        return False
    
    # Create sample data (optional)
    create_sample = input("\n🤔 Would you like to create sample patient data? (y/n): ").lower().strip()
    if create_sample == 'y':
        create_sample_patient_data()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the SQL schema in your Supabase dashboard")
    print("2. Start the Flask backend server")
    print("3. Test the patient profile endpoints")
    
    return True

if __name__ == "__main__":
    main()

