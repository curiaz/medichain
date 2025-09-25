#!/usr/bin/env python3
"""
Test script to check if all imports work correctly
"""

print("Testing imports...")

try:
    from flask import Flask
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask import failed: {e}")

try:
    from flask_cors import CORS
    print("✅ Flask-CORS imported successfully")
except ImportError as e:
    print(f"❌ Flask-CORS import failed: {e}")

try:
    from dotenv import load_dotenv
    print("✅ dotenv imported successfully")
except ImportError as e:
    print(f"❌ dotenv import failed: {e}")

try:
    from auth.firebase_auth_routes import auth_firebase_bp
    print("✅ firebase_auth_routes imported successfully")
except ImportError as e:
    print(f"❌ firebase_auth_routes import failed: {e}")

try:
    from medical_routes import medical_bp
    print("✅ medical_routes imported successfully")
except ImportError as e:
    print(f"❌ medical_routes import failed: {e}")

try:
    from appointment_routes import appointments_bp
    print("✅ appointment_routes imported successfully")
except ImportError as e:
    print(f"❌ appointment_routes import failed: {e}")

try:
    from db.supabase_client import SupabaseClient
    print("✅ SupabaseClient imported successfully")
except ImportError as e:
    print(f"❌ SupabaseClient import failed: {e}")

print("Import test completed!")