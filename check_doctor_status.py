"""
Quick diagnostic script to check doctor verification status
"""
from backend.db.supabase_client import SupabaseClient

supabase = SupabaseClient()

# Check Dr. Kenneth Abayon's status
doctor_email = "abayonkenneth372@gmail.com"

print(f"🔍 Checking verification status for: {doctor_email}")
print("=" * 60)

# Check user_profiles
user_response = (
    supabase.service_client.table("user_profiles")
    .select("firebase_uid, email, role, verification_status")
    .eq("email", doctor_email)
    .execute()
)

if user_response.data:
    user = user_response.data[0]
    print(f"\n📋 User Profile:")
    print(f"   Email: {user['email']}")
    print(f"   Role: {user['role']}")
    print(f"   Firebase UID: {user['firebase_uid']}")
    print(f"   Verification Status: {user['verification_status']}")
    
    # Check doctor_profiles
    firebase_uid = user['firebase_uid']
    doctor_response = (
        supabase.service_client.table("doctor_profiles")
        .select("*")
        .eq("firebase_uid", firebase_uid)
        .execute()
    )
    
    if doctor_response.data:
        doctor = doctor_response.data[0]
        print(f"\n👨‍⚕️ Doctor Profile:")
        print(f"   Specialization: {doctor.get('specialization')}")
        print(f"   Verification Token: {doctor.get('verification_token', 'None')[:20]}..." if doctor.get('verification_token') else "   Verification Token: None")
        print(f"   Last Request Sent: {doctor.get('last_verification_request_sent', 'Never')}")
        
        print(f"\n✅ DIAGNOSIS:")
        if user['verification_status'] == 'approved':
            print("   Your account IS APPROVED! ✓")
            print("   The UI might be caching old data or there's a data fetch issue.")
            print("\n💡 SOLUTION:")
            print("   1. Refresh your dashboard page")
            print("   2. Clear browser cache")
            print("   3. Log out and log back in")
        elif user['verification_status'] == 'pending':
            print("   Your account is PENDING verification")
            print("   You can use the 'Request Verification Review' button")
        else:
            print(f"   Status: {user['verification_status']}")
    else:
        print("\n❌ No doctor profile found!")
else:
    print("\n❌ User not found!")
