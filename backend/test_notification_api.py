#!/usr/bin/env python3
"""
Test Notification API Endpoints
Direct API test using requests
"""

import requests
import json
from datetime import datetime

def test_api_endpoints():
    """Test all notification API endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("🔌 Testing MediChain Notification API")
    print("=" * 50)
    
    # Test 1: Health check (if available)
    try:
        print("1️⃣ Testing health endpoint...")
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        else:
            print("   ⚠️  Health endpoint not available (this is normal)")
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  Health endpoint not reachable: {e}")
    
    # Test 2: Get notifications
    try:
        print("\n2️⃣ Testing GET /api/notifications...")
        response = requests.get(
            f"{base_url}/api/notifications", 
            params={'user_id': 'default_user'},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            print(f"   ✅ Success! Found {len(notifications)} notifications")
            
            for i, notif in enumerate(notifications[:3], 1):  # Show first 3
                status = "✅ Read" if notif.get('is_read') else "🔔 Unread"
                print(f"   {i}. {notif.get('title')} - {notif.get('category')}/{notif.get('priority')} ({status})")
                
        else:
            print(f"   ❌ Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 3: Get notification stats
    try:
        print("\n3️⃣ Testing GET /api/notifications/stats...")
        response = requests.get(
            f"{base_url}/api/notifications/stats", 
            params={'user_id': 'default_user'},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            print(f"   ✅ Success! Stats retrieved:")
            print(f"      Total: {stats.get('total', 0)}")
            print(f"      Unread: {stats.get('unread', 0)}")
            print(f"      High Priority: {stats.get('by_priority', {}).get('high', 0)}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 4: Create new notification
    try:
        print("\n4️⃣ Testing POST /api/notifications...")
        
        new_notification = {
            'user_id': 'default_user',
            'title': 'API Test Notification',
            'message': f'This notification was created via API at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
            'type': 'success',
            'category': 'system',
            'priority': 'normal',
            'action_url': '/dashboard',
            'action_label': 'View Dashboard',
            'metadata': {
                'test': True,
                'source': 'api_test',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        response = requests.post(
            f"{base_url}/api/notifications",
            json=new_notification,
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"   ✅ Success! Created notification:")
            print(f"      ID: {data.get('notification', {}).get('id', 'N/A')}")
            print(f"      Title: {new_notification['title']}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 5: Check if new notification appears in list
    try:
        print("\n5️⃣ Verifying new notification appears in list...")
        response = requests.get(
            f"{base_url}/api/notifications", 
            params={'user_id': 'default_user'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            notifications = data.get('notifications', [])
            
            # Look for our test notification
            api_test_notifs = [n for n in notifications if 'API Test' in n.get('title', '')]
            
            if api_test_notifs:
                print(f"   ✅ Success! Found {len(api_test_notifs)} API test notification(s)")
                latest = api_test_notifs[0]
                print(f"      Latest: {latest.get('title')} (ID: {latest.get('id')})")
            else:
                print(f"   ⚠️  API test notification not found in list")
                
        else:
            print(f"   ❌ Error retrieving notifications: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 API test completed!")

if __name__ == "__main__":
    test_api_endpoints()