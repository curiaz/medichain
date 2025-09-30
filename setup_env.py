#!/usr/bin/env python3
"""
Quick Environment Setup for MediChain
"""

import os
import shutil

def create_env_file():
    """Create .env file from template"""
    print("Setting up environment configuration...")
    
    template_path = os.path.join('backend', 'env_template.txt')
    env_path = os.path.join('backend', '.env')
    
    if os.path.exists(env_path):
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/n): ").lower().strip()
        if overwrite != 'y':
            print("❌ Setup cancelled")
            return False
    
    try:
        shutil.copy(template_path, env_path)
        print("✅ .env file created!")
        print(f"📝 Please edit {env_path} with your actual credentials")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def show_instructions():
    """Show setup instructions"""
    print("\n📋 Setup Instructions:")
    print("=" * 50)
    print("\n1️⃣ SUPABASE SETUP:")
    print("   - Go to your Supabase project dashboard")
    print("   - Navigate to Settings > API")
    print("   - Copy the Project URL and API keys")
    print("   - Update SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY in .env")
    
    print("\n2️⃣ FIREBASE SETUP:")
    print("   - Go to your Firebase project console")
    print("   - Navigate to Project Settings > Service Accounts")
    print("   - Generate new private key (downloads JSON file)")
    print("   - Update FIREBASE_SERVICE_ACCOUNT_KEY with path to JSON file")
    
    print("\n3️⃣ FLASK SETUP:")
    print("   - Generate a random SECRET_KEY (32+ characters)")
    print("   - Update SECRET_KEY in .env")
    
    print("\n4️⃣ TEST CONNECTION:")
    print("   - Run: python test_real_database.py")
    print("   - Start backend: cd backend && python app.py")
    print("   - Test frontend: npm start")

def main():
    """Main setup function"""
    print("🏥 MediChain Environment Setup")
    print("=" * 35)
    
    # Create .env file
    if create_env_file():
        show_instructions()
        print("\n🎉 Setup complete! Update your .env file and test the connection.")
    else:
        print("\n❌ Setup failed. Please create .env file manually.")

if __name__ == "__main__":
    main()

