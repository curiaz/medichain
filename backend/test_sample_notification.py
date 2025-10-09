#!/usr/bin/env python3
"""
Insert a sample notification for default_user to test the complete system
"""

import requests
import json

def insert_sample_notification():
    """Insert a sample notification for default_user"""
    print("🔔 Inserting sample notification for default_user...")
    
    notification_data = {
        "user_id": "default_user", 
        "title": "Diagnosis Complete",
        "message": "Your AI health analysis has been completed. The system identified potential symptoms and provided recommendations.",
        "type": "success",
        "category": "medical",
        "priority": "high",
        "action_url": "/ai-health",
        "action_label": "View Results",
        "metadata": {
            "diagnosis": "Common Cold",
            "symptoms": ["fever", "cough", "fatigue"],
            "confidence": "high",
            "timestamp": "2025-10-07T15:30:00Z"
        }
    }
    
    try:
        response = requests.post("http://localhost:5000/api/notifications", json=notification_data, timeout=10)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Sample notification created successfully!")
            print(f"   📝 Notification ID: {result.get('notification_id')}")
            print(f"   👤 User: {notification_data['user_id']}")
            print(f"   💬 Title: {notification_data['title']}")
            print(f"   📋 Category: {notification_data['category']}")
            return True
        else:
            print(f"❌ Failed to create notification: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating notification: {e}")
        return False

def check_default_user_notifications():
    """Check all notifications for default_user"""
    print("\n📋 Checking all notifications for default_user...")
    
    try:
        response = requests.get("http://localhost:5000/api/notifications?user_id=default_user", timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            notifications = result.get('notifications', [])
            
            print(f"✅ Found {len(notifications)} notifications for default_user:")
            
            for i, notif in enumerate(notifications, 1):
                print(f"   {i}. [{notif['type'].upper()}] {notif['title']}")
                print(f"      📝 {notif['message'][:80]}{'...' if len(notif['message']) > 80 else ''}")
                print(f"      🏷️ {notif['category']} | 🔔 {notif['priority']} | 📅 {notif['created_at']}")
                print()
            
            return len(notifications)
        else:
            print(f"❌ Failed to get notifications: {response.status_code}")
            return 0
            
    except Exception as e:
        print(f"❌ Error getting notifications: {e}")
        return 0

if __name__ == "__main__":
    print("🚀 Testing notification system for default_user")
    print("=" * 60)
    
    # Insert sample notification
    success = insert_sample_notification()
    
    # Check all notifications
    count = check_default_user_notifications()
    
    print("=" * 60)
    
    if success and count > 0:
        print(f"✅ SUCCESS! Notification system is fully functional!")
        print(f"   📝 Sample notification inserted successfully")
        print(f"   📋 Total notifications for default_user: {count}")
        print(f"   🔗 Frontend can now call: http://localhost:5000/api/notifications?user_id=default_user")
    else:
        print("❌ There might be an issue. Check the Flask server logs.")