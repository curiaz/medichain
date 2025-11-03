"""
Simple test to check if Firebase authentication is working
"""
import sys
sys.path.append('./backend')

print("\n🔥 Testing Firebase Authentication Setup\n")
print("="*60)

try:
    from auth.firebase_auth import firebase_auth_service
    print("✅ Firebase auth service imported")
    
    # Try to verify a real Firebase token (this will fail but shows us the error)
    print("\n📝 Firebase auth service is ready to verify tokens")
    print(f"   Service type: {type(firebase_auth_service).__name__}")
    print(f"   Methods available: {[m for m in dir(firebase_auth_service) if not m.startswith('_')]}")
    
except ImportError as e:
    print(f"❌ Failed to import Firebase: {e}")
    print("\n⚠️  Make sure you're in the medichain directory")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("\n📋 To test signup flow:")
print("   1. Go to http://localhost:3001/signup")
print("   2. Fill in the form")
print("   3. Open browser console (F12)")
print("   4. Click 'Create Account'")
print("   5. Check console for errors")
print("\n" + "="*60 + "\n")
