#!/usr/bin/env python3
"""
Environment Setup Script for MediChain Patient Profile Management
This script helps you set up the necessary environment variables
"""

import os
import sys

def create_env_file():
    """Create .env file with template values"""
    env_content = """# MediChain Patient Profile Management - Environment Configuration

# Supabase Configuration
# Get these from your Supabase project settings
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# Firebase Configuration
# Get these from your Firebase project settings
FIREBASE_SERVICE_ACCOUNT_KEY=path/to/your/firebase-service-account.json
FIREBASE_PROJECT_ID=your-firebase-project-id

# Flask Configuration
SECRET_KEY=your_flask_secret_key_here
FLASK_DEBUG=True
FLASK_ENV=development

# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/medichain
"""
    
    env_path = os.path.join('backend', '.env')
    
    if os.path.exists(env_path):
        print(f"⚠️  .env file already exists at {env_path}")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("❌ Environment setup cancelled")
            return False
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"✅ .env file created at {env_path}")
        print("\n📝 Please update the following values in your .env file:")
        print("   1. SUPABASE_URL - Your Supabase project URL")
        print("   2. SUPABASE_KEY - Your Supabase anon key")
        print("   3. SUPABASE_SERVICE_KEY - Your Supabase service role key")
        print("   4. FIREBASE_SERVICE_ACCOUNT_KEY - Path to Firebase service account JSON")
        print("   5. SECRET_KEY - A random secret key for Flask")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def check_supabase_connection():
    """Check if Supabase credentials are working"""
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join('backend', '.env'))
        
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials not found in .env file")
            return False
        
        if 'your-project-id' in supabase_url or 'your_supabase' in supabase_key:
            print("⚠️  Supabase credentials appear to be template values")
            print("   Please update them with your actual Supabase credentials")
            return False
        
        print("✅ Supabase credentials found")
        return True
        
    except ImportError:
        print("❌ python-dotenv not installed. Run: pip install python-dotenv")
        return False
    except Exception as e:
        print(f"❌ Error checking Supabase connection: {e}")
        return False

def check_firebase_connection():
    """Check if Firebase credentials are working"""
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join('backend', '.env'))
        
        firebase_key_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY')
        
        if not firebase_key_path:
            print("❌ Firebase service account key path not found in .env file")
            return False
        
        if 'path/to/your' in firebase_key_path:
            print("⚠️  Firebase service account key path appears to be template value")
            print("   Please update it with your actual Firebase service account JSON path")
            return False
        
        if not os.path.exists(firebase_key_path):
            print(f"❌ Firebase service account key file not found: {firebase_key_path}")
            return False
        
        print("✅ Firebase service account key found")
        return True
        
    except Exception as e:
        print(f"❌ Error checking Firebase connection: {e}")
        return False

def main():
    """Main setup function"""
    print("🏥 MediChain Patient Profile - Environment Setup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('backend'):
        print("❌ Please run this script from the medichain root directory")
        return False
    
    print("\n1️⃣ Creating .env file...")
    if not create_env_file():
        return False
    
    print("\n2️⃣ Checking Supabase configuration...")
    supabase_ok = check_supabase_connection()
    
    print("\n3️⃣ Checking Firebase configuration...")
    firebase_ok = check_firebase_connection()
    
    print("\n📋 Setup Summary:")
    print(f"   Supabase: {'✅ Ready' if supabase_ok else '❌ Needs configuration'}")
    print(f"   Firebase: {'✅ Ready' if firebase_ok else '❌ Needs configuration'}")
    
    if supabase_ok and firebase_ok:
        print("\n🎉 Environment setup complete!")
        print("\n🚀 Next steps:")
        print("   1. Run the database schema in Supabase")
        print("   2. Start the backend server: cd backend && python app.py")
        print("   3. Test the patient profile endpoints")
    else:
        print("\n⚠️  Please complete the configuration and run this script again")
        print("\n📚 Help:")
        print("   - Supabase: https://supabase.com/docs/guides/getting-started")
        print("   - Firebase: https://firebase.google.com/docs/admin/setup")
    
    return supabase_ok and firebase_ok

if __name__ == "__main__":
    main()

