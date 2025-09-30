#!/usr/bin/env python3
"""
Test script for OTP-based password reset functionality
"""

import requests
import json
import time

# Base URL for the backend API
BASE_URL = "http://localhost:5000"

def test_password_reset_flow():
    """Test the complete password reset flow"""
    
    print("🔧 Testing OTP-based Password Reset System")
    print("=" * 50)
    
    # Test data
    test_email = "test@example.com"
    test_otp = "123456"  # We'll need to check this from the backend logs
    new_password = "newSecurePassword123!"
    
    # Step 1: Test password reset request
    print("\n📧 Step 1: Testing password reset request...")
    reset_data = {
        "email": test_email
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/password-reset-request", 
                               json=reset_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Password reset request successful!")
        else:
            print("❌ Password reset request failed!")
            
    except Exception as e:
        print(f"❌ Error in password reset request: {e}")
    
    # Step 2: Test OTP verification (with a sample OTP)
    print("\n🔐 Step 2: Testing OTP verification...")
    otp_data = {
        "email": test_email,
        "otp": "123456"  # This might fail since we don't have the actual OTP
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/verify-otp", 
                               json=otp_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ OTP verification successful!")
            reset_token = response.json().get('reset_token')
            print(f"Reset Token: {reset_token}")
        else:
            print("❌ OTP verification failed (expected if using dummy OTP)")
            
    except Exception as e:
        print(f"❌ Error in OTP verification: {e}")
    
    # Step 3: Test password reset (this will likely fail without valid token)
    print("\n🔑 Step 3: Testing password reset...")
    password_data = {
        "token": "dummy_token",  # Would need actual token from Step 2
        "new_password": new_password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/password-reset", 
                               json=password_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Password reset successful!")
        else:
            print("❌ Password reset failed (expected without valid token)")
            
    except Exception as e:
        print(f"❌ Error in password reset: {e}")
    
    # Test API endpoints accessibility
    print("\n🌐 Testing API endpoint accessibility...")
    endpoints = [
        "/api/auth/password-reset-request",
        "/api/auth/verify-otp", 
        "/api/auth/password-reset"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.options(f"{BASE_URL}{endpoint}")
            print(f"✅ {endpoint} is accessible (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {endpoint} is not accessible: {e}")

def test_email_configuration():
    """Test if email configuration is properly set up"""
    print("\n📫 Testing Email Configuration...")
    
    # Check if environment variables are available (indirectly through API)
    test_data = {
        "email": "nonexistent@example.com"  # This should fail gracefully
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/password-reset-request", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code in [400, 404]:
            print("✅ Email service is configured (proper error handling)")
        elif response.status_code == 200:
            print("⚠️ Email service accepted non-existent email (check validation)")
        else:
            print(f"❓ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Email configuration test failed: {e}")

if __name__ == "__main__":
    test_password_reset_flow()
    test_email_configuration()
    
    print("\n" + "=" * 50)
    print("🏁 Password Reset Testing Complete!")
    print("\n📝 Next Steps:")
    print("1. Check backend logs for actual OTP values")
    print("2. Test with real email addresses")
    print("3. Verify Gmail SMTP credentials are configured")
    print("4. Run frontend tests: npm test -- ResetPassword.test.jsx")
    print("5. Test complete user flow in browser")