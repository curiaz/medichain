"""
Reset doctor verification status to 'pending' for testing
"""
from backend.db.supabase_client import SupabaseClient

supabase = SupabaseClient()

doctor_email = "abayonkenneth372@gmail.com"

print(f"🔄 Resetting verification status for: {doctor_email}")
print("=" * 60)

# Get user
user_response = (
    supabase.service_client.table("user_profiles")
    .select("firebase_uid, email, verification_status")
    .eq("email", doctor_email)
    .execute()
)

if user_response.data:
    user = user_response.data[0]
    current_status = user['verification_status']
    firebase_uid = user['firebase_uid']
    
    print(f"\n📋 Current Status: {current_status}")
    
    if current_status == 'approved':
        print(f"\n⚠️  Changing status from 'approved' to 'pending' for testing...")
        
        # Update user_profiles
        update_response = (
            supabase.service_client.table("user_profiles")
            .update({"verification_status": "pending"})
            .eq("firebase_uid", firebase_uid)
            .execute()
        )
        
        print(f"✅ Status changed to: pending")
        print(f"\n💡 Now you can test the 'Request Verification Review' feature!")
        print(f"\n📝 To revert back to approved later, you can:")
        print(f"   1. Click the verification link in email")
        print(f"   2. Or manually update in Supabase")
    else:
        print(f"✅ Status is already: {current_status}")
        print(f"   You can test the resend feature now!")
else:
    print("❌ User not found!")
