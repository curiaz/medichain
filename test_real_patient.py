#!/usr/bin/env python3
"""
Quick Test: Patient Profile with Real Data
"""

import os
import sys

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_real_patient_profile():
    """Test getting real patient profile"""
    print("Testing Real Patient Profile...")
    
    try:
        from db.supabase_client import SupabaseClient
        
        supabase = SupabaseClient()
        
        # Test with real patient UID
        real_patient_uid = 'xeA5Dv1708a2YVyxO4I1HBpHnBv2'  # medichain173@gmail.com
        
        print(f"Getting profile for real patient: {real_patient_uid}")
        profile = supabase.get_patient_profile(real_patient_uid)
        
        if profile:
            print("SUCCESS: Real patient profile retrieved!")
            user_profile = profile['user_profile']
            print(f"  Name: {user_profile['first_name']} {user_profile['last_name']}")
            print(f"  Email: {user_profile['email']}")
            print(f"  Role: {user_profile['role']}")
            print(f"  Phone: {user_profile.get('phone', 'N/A')}")
            print(f"  Firebase UID: {user_profile['firebase_uid']}")
            return True
        else:
            print("ERROR: Could not retrieve real patient profile")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Main function"""
    print("Testing Real Patient Profile Data")
    print("=" * 35)
    
    test_real_patient_profile()
    print("\nDone!")

if __name__ == "__main__":
    main()

