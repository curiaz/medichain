#!/usr/bin/env python3
"""
Test Notification Database - Insert Sample Notification
Test script to verify notification database is working
"""

import sqlite3
import json
import os
from datetime import datetime

def test_notification_database():
    """Test inserting and retrieving notifications"""
    
    # Database path (same as used by the app)
    db_path = os.path.join(os.path.dirname(__file__), 'notifications.db')
    
    print(f"🔍 Testing notification database at: {db_path}")
    print(f"📁 Database exists: {os.path.exists(db_path)}")
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        print("\n📊 Current database contents:")
        
        # Show current notifications
        cursor.execute("SELECT COUNT(*) as count FROM notifications")
        count = cursor.fetchone()['count']
        print(f"   Current notification count: {count}")
        
        # Show existing notifications
        cursor.execute("SELECT id, title, user_id, category, priority, is_read, created_at FROM notifications ORDER BY created_at DESC LIMIT 5")
        existing = cursor.fetchall()
        
        print("\n   📋 Recent notifications:")
        for notif in existing:
            status = "✅ Read" if notif['is_read'] else "🔔 Unread"
            print(f"   - ID {notif['id']}: {notif['title']} ({status}) - {notif['category']}/{notif['priority']}")
        
        # Insert new test notification
        test_notification = {
            'user_id': 'test_user_' + datetime.now().strftime('%H%M%S'),
            'title': 'Test Notification from Script',
            'message': f'This is a test notification created at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} to verify the database is working properly.',
            'type': 'info',
            'category': 'system',
            'priority': 'normal',
            'is_read': 0,
            'is_archived': 0,
            'action_url': '/notifications',
            'action_label': 'View All',
            'metadata': json.dumps({
                'test': True,
                'source': 'test_script',
                'timestamp': datetime.now().isoformat()
            })
        }
        
        print(f"\n➕ Inserting new test notification for user: {test_notification['user_id']}")
        
        cursor.execute("""
            INSERT INTO notifications (
                user_id, title, message, type, category, priority, 
                is_read, is_archived, action_url, action_label, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_notification['user_id'],
            test_notification['title'],
            test_notification['message'],
            test_notification['type'],
            test_notification['category'],
            test_notification['priority'],
            test_notification['is_read'],
            test_notification['is_archived'],
            test_notification['action_url'],
            test_notification['action_label'],
            test_notification['metadata']
        ))
        
        # Get the inserted notification ID
        new_id = cursor.lastrowid
        print(f"✅ Successfully inserted notification with ID: {new_id}")
        
        # Commit the changes
        conn.commit()
        
        # Verify the insertion
        cursor.execute("SELECT * FROM notifications WHERE id = ?", (new_id,))
        inserted = cursor.fetchone()
        
        if inserted:
            print(f"✅ Verification successful! Notification details:")
            print(f"   ID: {inserted['id']}")
            print(f"   Title: {inserted['title']}")
            print(f"   User: {inserted['user_id']}")
            print(f"   Category: {inserted['category']}")
            print(f"   Priority: {inserted['priority']}")
            print(f"   Created: {inserted['created_at']}")
            print(f"   Metadata: {inserted['metadata']}")
        
        # Show updated count
        cursor.execute("SELECT COUNT(*) as count FROM notifications")
        new_count = cursor.fetchone()['count']
        print(f"\n📊 Updated notification count: {new_count} (increased by {new_count - count})")
        
        # Test retrieval for default_user
        print(f"\n🔍 Testing retrieval for 'default_user':")
        cursor.execute("SELECT COUNT(*) as count FROM notifications WHERE user_id = 'default_user'")
        default_count = cursor.fetchone()['count']
        print(f"   Notifications for default_user: {default_count}")
        
        if default_count > 0:
            cursor.execute("""
                SELECT id, title, category, priority, is_read, created_at 
                FROM notifications 
                WHERE user_id = 'default_user' 
                ORDER BY created_at DESC LIMIT 3
            """)
            default_notifs = cursor.fetchall()
            
            print("   📋 Recent default_user notifications:")
            for notif in default_notifs:
                status = "✅ Read" if notif['is_read'] else "🔔 Unread"
                print(f"   - ID {notif['id']}: {notif['title']} ({status})")
        
        conn.close()
        
        print(f"\n🎉 Database test completed successfully!")
        print(f"💡 You can now test the API endpoints with the notification data")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_api_simulation():
    """Simulate what the API would return"""
    db_path = os.path.join(os.path.dirname(__file__), 'notifications.db')
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print(f"\n🔌 Simulating API response for GET /api/notifications?user_id=default_user")
        
        # Simulate the API query
        cursor.execute("""
            SELECT * FROM notifications 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        """, ('default_user', 10))
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'id': row['id'],
                'title': row['title'],
                'message': row['message'],
                'type': row['type'],
                'category': row['category'],
                'priority': row['priority'],
                'is_read': bool(row['is_read']),
                'action_url': row['action_url'],
                'action_label': row['action_label'],
                'created_at': row['created_at'],
                'metadata': json.loads(row['metadata'] or '{}')
            })
        
        print(f"📊 API would return {len(notifications)} notifications:")
        for i, notif in enumerate(notifications, 1):
            print(f"   {i}. {notif['title']} - {notif['category']}/{notif['priority']} ({'read' if notif['is_read'] else 'unread'})")
        
        conn.close()
        
        return notifications
        
    except Exception as e:
        print(f"❌ API simulation error: {e}")
        return []

if __name__ == "__main__":
    print("🧪 Testing MediChain Notification Database")
    print("=" * 50)
    
    success = test_notification_database()
    
    if success:
        test_api_simulation()
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")