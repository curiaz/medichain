#!/usr/bin/env python3
"""
Test the embedded notification API by creating and retrieving notifications
"""

import requests
import json

# Test the notification API endpoints
BASE_URL = "http://localhost:5000/api/notifications"

def test_create_notification():
    """Test creating a new notification"""
    print("🔔 Testing notification creation...")
    
    notification_data = {
        "user_id": "test_user",
        "title": "API Test Notification",
        "message": "This notification was created via the embedded API in app.py!",
        "type": "success",
        "category": "system",
        "priority": "high",
        "action_url": "/test",
        "action_label": "View Test",
        "metadata": {
            "test": True,
            "created_by": "embedded_api_test",
            "timestamp": "2025-10-07"
        }
    }
    
    try:
        response = requests.post(BASE_URL, json=notification_data, timeout=10)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Notification created successfully!")
            print(f"   📝 ID: {result.get('notification_id')}")
            print(f"   💬 Message: {notification_data['message']}")
            return result.get('notification_id')
        else:
            print(f"❌ Failed to create notification: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating notification: {e}")
        return None

def test_get_notifications():
    """Test retrieving notifications"""
    print("\n📋 Testing notification retrieval...")
    
    try:
        # Get notifications for test_user
        response = requests.get(f"{BASE_URL}?user_id=test_user", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            notifications = result.get('notifications', [])
            pagination = result.get('pagination', {})
            
            print(f"✅ Retrieved {len(notifications)} notifications")
            print(f"   📊 Total: {pagination.get('total', 0)}")
            
            for i, notif in enumerate(notifications, 1):
                print(f"   {i}. {notif['title']} - {notif['type']} ({notif['category']})")
                print(f"      📅 {notif['created_at']}")
            
            return notifications
        else:
            print(f"❌ Failed to get notifications: {response.status_code}")
            print(f"   Error: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting notifications: {e}")
        return []

def test_notification_stats():
    """Test getting notification statistics"""
    print("\n📊 Testing notification statistics...")
    
    try:
        response = requests.get(f"{BASE_URL}/stats?user_id=test_user", timeout=10)
        
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Statistics retrieved:")
            print(f"   📈 Total: {stats.get('total', 0)}")
            print(f"   📬 Unread: {stats.get('unread', 0)}")
            print(f"   🗂️ Categories: {stats.get('categories', {})}")
            return stats
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
        return None

def main():
    """Run all notification tests"""
    print("🚀 Testing Embedded Notification API")
    print("=" * 50)
    
    # Test creating notification
    notification_id = test_create_notification()
    
    # Test getting notifications
    notifications = test_get_notifications()
    
    # Test statistics
    stats = test_notification_stats()
    
    print("\n" + "=" * 50)
    
    if notification_id and notifications and stats:
        print("✅ ALL TESTS PASSED! Embedded notification API is working!")
        print(f"   📝 Created notification ID: {notification_id}")
        print(f"   📋 Found {len(notifications)} notifications")
        print(f"   📊 Stats show {stats.get('total', 0)} total notifications")
    else:
        print("❌ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()