"""
Test if backend auth routes are actually working
"""
import requests
import json

API_URL = "https://medichain.clinic"

print("\n" + "="*60)
print("🔍 Testing Backend Auth Routes")
print("="*60)

# Test 1: Check if /api/auth is accessible
print("\n1️⃣  Testing /api/auth endpoint...")
try:
    response = requests.get(f"{API_URL}/api/auth")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Check /api/auth/register route
print("\n2️⃣  Testing /api/auth/register endpoint...")
try:
    response = requests.post(
        f"{API_URL}/api/auth/register",
        json={"test": "data"},
        headers={"Content-Type": "application/json"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: List all available routes
print("\n3️⃣  Testing route availability...")
test_routes = [
    "/api/auth/signup",
    "/api/auth/register",
    "/api/auth/login",
    "/api/health"
]

for route in test_routes:
    try:
        response = requests.get(f"{API_URL}{route}")
        print(f"   {route}: {response.status_code}")
    except Exception as e:
        print(f"   {route}: ❌ Error - {e}")

print("\n" + "="*60 + "\n")
