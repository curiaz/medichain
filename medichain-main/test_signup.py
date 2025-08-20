import requests
import json

# Test the signup endpoint directly
url = "http://localhost:5000/api/auth/signup"

test_data = {
    "email": "test@example.com",
    "password": "TestPass123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "patient"
}

print("Testing signup with data:", json.dumps(test_data, indent=2))

try:
    response = requests.post(url, json=test_data, headers={'Content-Type': 'application/json'})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
