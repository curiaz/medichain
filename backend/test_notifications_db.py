#!/usr/bin/env python3
"""
Test Notification Database
Quick test to verify the notification database is working correctly
"""

import sqlite3
import os
import json

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'notifications.db')

def test_database():
    """Test the notification database"""
    print(f"Testing database at: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print("❌ Database file not found!")
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Test 1: Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ Notifications table exists")
        else:
            print("❌ Notifications table not found!")
            return
        
        # Test 2: Check table structure
        cursor.execute("PRAGMA table_info(notifications)")
        columns = cursor.fetchall()
        print(f"✅ Table has {len(columns)} columns")
        
        # Test 3: Count notifications
        cursor.execute("SELECT COUNT(*) FROM notifications")
        count = cursor.fetchone()[0]
        print(f"✅ Found {count} notifications in database")
        
        # Test 4: Show sample notifications
        cursor.execute("""
            SELECT id, user_id, title, type, category, priority, is_read, created_at 
            FROM notifications 
            ORDER BY created_at DESC 
            LIMIT 3
        """)
        notifications = cursor.fetchall()
        
        print("\n📋 Sample notifications:")
        for notif in notifications:
            status = "📖 Read" if notif[6] else "📩 Unread"
            print(f"  {status} | {notif[3].upper()} | {notif[4]} | {notif[2]}")
        
        # Test 5: Check notification stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread,
                COUNT(DISTINCT user_id) as users
            FROM notifications
        """)
        stats = cursor.fetchone()
        print(f"\n📊 Statistics:")
        print(f"  Total: {stats[0]} | Unread: {stats[1]} | Users: {stats[2]}")
        
        # Test 6: Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='notifications'")
        indexes = cursor.fetchall()
        print(f"\n🔍 Found {len(indexes)} indexes for performance")
        
        conn.close()
        print("\n✅ Database test completed successfully!")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🧪 MediChain Notification Database Test")
    print("=" * 50)
    test_database()