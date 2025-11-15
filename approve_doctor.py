"""
Approve doctor verification status
"""
from backend.db.supabase_client import SupabaseClient

supabase = SupabaseClient()

doctor_email = "abayonkenneth372@gmail.com"

print(f"✅ Approving verification for: {doctor_email}")
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
    firebase_uid = user['firebase_uid']
    
    # Update to approved
    update_response = (
        supabase.service_client.table("user_profiles")
        .update({"verification_status": "approved"})
        .eq("firebase_uid", firebase_uid)
        .execute()
    )
    
    print(f"✅ Status changed to: approved")
    print(f"\n🎉 Dr. {doctor_email} is now verified!")
    print(f"\n📝 Refresh your dashboard to see the 'Verified Doctor' status")
else:
    print("❌ User not found!")
