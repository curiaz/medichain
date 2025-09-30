#!/usr/bin/env python3
"""
Network Connection Test for MediChain
Tests backend connectivity and login endpoints
"""
#comment

import requests
import sys
import os

def test_backend_health():
    """Test if backend server is accessible"""
    print("🔍 Testing Backend Health...")
    print("=" * 40)
    
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running")
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            return True
        else:
            print(f"❌ Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible on localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_auth_endpoints():
    """Test authentication endpoints"""
    print("\n🔍 Testing Auth Endpoints...")
    print("=" * 40)
    
    endpoints = [
        "/api/auth/login",
        "/api/auth/register",
        "/api/auth/verify"
    ]
    
    all_accessible = True
    
    for endpoint in endpoints:
        try:
            url = f"http://localhost:5000{endpoint}"
            response = requests.options(url, timeout=5)  # OPTIONS request to check if endpoint exists
            
            if response.status_code in [200, 405]:  # 405 is OK for OPTIONS, means endpoint exists
                print(f"✅ {endpoint}: Endpoint accessible")
            else:
                print(f"⚠️  {endpoint}: Returned {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ {endpoint}: Connection failed")
            all_accessible = False
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
            all_accessible = False
    
    return all_accessible

def test_cors():
    """Test CORS configuration"""
    print("\n🔍 Testing CORS Configuration...")
    print("=" * 40)
    
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options("http://localhost:5000/api/auth/login", 
                                  headers=headers, timeout=5)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
        }
        
        if any(cors_headers.values()):
            print("✅ CORS is configured")
            for header, value in cors_headers.items():
                if value:
                    print(f"   {header}: {value}")
            return True
        else:
            print("❌ CORS headers not found")
            return False
            
    except Exception as e:
        print(f"❌ CORS test failed: {e}")
        return False

def main():
    """Run all network tests"""
    print("🚀 MediChain Network Connection Tests")
    print("=" * 50)
    
    tests = [
        test_backend_health(),
        test_auth_endpoints(),
        test_cors()
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All network tests passed!")
        print("✅ Backend is ready for frontend connections")
        return True
    else:
        print(f"❌ {total - passed} test(s) failed")
        print("⚠️  Please check backend configuration")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)