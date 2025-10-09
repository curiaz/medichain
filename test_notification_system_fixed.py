#!/usr/bin/env python3
"""
Fixed Comprehensive Unit Test Suite for MediChain Notification System
Tests all notification API endpoints, database operations, and edge cases
"""

import unittest
import json
import sqlite3
import tempfile
import os
import sys
import shutil
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import Flask app components
try:
    from app import app
    import app as app_module  # Import as module for patching
except ImportError as e:
    print(f"❌ Failed to import app components: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class NotificationSystemTestCase(unittest.TestCase):
    """Test case for the notification system with proper mocking"""
    
    def setUp(self):
        """Set up test fixtures with temporary database"""
        # Create Flask test client
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.client = self.app.test_client()
        
        # Create temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, 'test_notifications.db')
        
        # Patch the database path in the app module
        self.db_patcher = patch.object(app_module, 'NOTIFICATIONS_DB_PATH', self.test_db_path)
        self.db_patcher.start()
        
        # Initialize test database
        self._init_test_db()
        
    def tearDown(self):
        """Clean up after tests"""
        # Stop the patcher
        self.db_patcher.stop()
        
        # Clean up temporary directory
        try:
            shutil.rmtree(self.test_dir)
        except (PermissionError, OSError):
            # On Windows, files might be locked, try again
            import time
            time.sleep(0.1)
            try:
                shutil.rmtree(self.test_dir)
            except (PermissionError, OSError):
                pass  # Skip cleanup if still locked
    
    def _init_test_db(self):
        """Initialize test database with schema"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Create notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'error', 'alert')),
                category TEXT DEFAULT 'general' CHECK (category IN ('general', 'medical', 'appointment', 'system', 'medication', 'diagnosis', 'profile', 'security')),
                priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
                is_read INTEGER DEFAULT 0,
                is_archived INTEGER DEFAULT 0,
                action_url TEXT,
                action_label TEXT,
                metadata TEXT DEFAULT '{}',
                expires_at TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                read_at TEXT,
                updated_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_category ON notifications(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority)')
        
        conn.commit()
        conn.close()
    
    def test_database_initialization(self):
        """Test that the database is properly initialized"""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        # Check if notifications table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notifications'")
        result = cursor.fetchone()
        self.assertIsNotNone(result, "Notifications table should exist")
        
        # Check table schema
        cursor.execute("PRAGMA table_info(notifications)")
        columns = [row[1] for row in cursor.fetchall()]
        expected_columns = ['id', 'user_id', 'title', 'message', 'type', 'category', 
                          'priority', 'is_read', 'is_archived', 'action_url', 'action_label', 
                          'metadata', 'expires_at', 'created_at', 'read_at', 'updated_at']
        
        for col in expected_columns:
            self.assertIn(col, columns, f"Column '{col}' should exist in notifications table")
        
        conn.close()
    
    @patch.object(app_module, 'NOTIFICATIONS_DB_PATH')
    def test_create_notification_success(self, mock_db_path):
        """Test successful notification creation"""
        mock_db_path.return_value = self.test_db_path
        
        notification_data = {
            "user_id": "test_user",
            "title": "Test Notification",
            "message": "This is a test notification",
            "type": "info",
            "category": "general",
            "priority": "normal"
        }
        
        with self.app.app_context():
            response = self.client.post('/api/notifications', 
                                      data=json.dumps(notification_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        data = json.loads(response.data)
        self.assertIn('notification_id', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Notification created successfully')
    
    def test_create_notification_missing_fields(self):
        """Test notification creation with missing required fields"""
        notification_data = {
            "title": "Test Notification",
            "message": "This is a test notification"
            # Missing user_id
        }
        
        with self.app.app_context():
            response = self.client.post('/api/notifications',
                                      data=json.dumps(notification_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('user_id', data['error'])
    
    def test_get_notifications_success(self):
        """Test successful retrieval of notifications"""
        # First create a notification directly in database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, type, category)
            VALUES (?, ?, ?, ?, ?)
        ''', ('test_user', 'Test Notification', 'Test message', 'info', 'general'))
        conn.commit()
        conn.close()
        
        # Now retrieve notifications
        with self.app.app_context():
            response = self.client.get('/api/notifications?user_id=test_user')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('notifications', data)
        self.assertIn('pagination', data)
        self.assertGreater(len(data['notifications']), 0)
    
    def test_get_notifications_pagination(self):
        """Test notification pagination"""
        # Create multiple notifications directly in database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        for i in range(15):
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message)
                VALUES (?, ?, ?)
            ''', ('pagination_user', f'Notification {i}', f'Message {i}'))
        
        conn.commit()
        conn.close()
        
        # Test first page
        with self.app.app_context():
            response = self.client.get('/api/notifications?user_id=pagination_user&page=1&per_page=10')
        
        data = json.loads(response.data)
        
        self.assertEqual(len(data['notifications']), 10)
        self.assertEqual(data['pagination']['page'], 1)
        self.assertEqual(data['pagination']['total'], 15)
        
        # Test second page
        with self.app.app_context():
            response = self.client.get('/api/notifications?user_id=pagination_user&page=2&per_page=10')
        
        data = json.loads(response.data)
        
        self.assertEqual(len(data['notifications']), 5)
        self.assertEqual(data['pagination']['page'], 2)
    
    def test_update_notification_mark_read(self):
        """Test marking notification as read"""
        # Create a notification directly in database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message)
            VALUES (?, ?, ?)
        ''', ('test_user', 'Test Notification', 'Test message'))
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Mark as read
        update_data = {"is_read": True}
        with self.app.app_context():
            response = self.client.put(f'/api/notifications/{notification_id}',
                                     data=json.dumps(update_data),
                                     content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Notification updated successfully')
        
        # Verify update in database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT is_read FROM notifications WHERE id = ?', (notification_id,))
        is_read = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(is_read, 1)
    
    def test_update_notification_not_found(self):
        """Test updating non-existent notification"""
        update_data = {"is_read": True}
        with self.app.app_context():
            response = self.client.put('/api/notifications/99999',
                                     data=json.dumps(update_data),
                                     content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_delete_notification_success(self):
        """Test successful notification deletion"""
        # Create a notification directly in database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message)
            VALUES (?, ?, ?)
        ''', ('test_user', 'Test Notification', 'Test message'))
        notification_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Delete the notification
        with self.app.app_context():
            response = self.client.delete(f'/api/notifications/{notification_id}')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Notification deleted successfully')
        
        # Verify deletion in database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM notifications WHERE id = ?', (notification_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 0)
    
    def test_delete_notification_not_found(self):
        """Test deleting non-existent notification"""
        with self.app.app_context():
            response = self.client.delete('/api/notifications/99999')
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_bulk_mark_as_read(self):
        """Test bulk marking notifications as read"""
        # Create multiple notifications directly in database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        notification_ids = []
        
        for i in range(3):
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message)
                VALUES (?, ?, ?)
            ''', ('bulk_user', f'Bulk Notification {i}', f'Message {i}'))
            notification_ids.append(cursor.lastrowid)
        
        conn.commit()
        conn.close()
        
        # Mark specific notifications as read
        bulk_data = {
            "user_id": "bulk_user",
            "notification_ids": notification_ids[:2]  # Only first two
        }
        
        with self.app.app_context():
            response = self.client.post('/api/notifications/bulk-read',
                                      data=json.dumps(bulk_data),
                                      content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['updated_count'], 2)
    
    def test_notification_statistics(self):
        """Test notification statistics endpoint"""
        # Create notifications with different statuses directly in database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        notifications = [
            ('stats_user', 'Unread 1', 'Message', 'info', 'general', 'high', 0),
            ('stats_user', 'Unread 2', 'Message', 'info', 'general', 'urgent', 0),
            ('stats_user', 'Read 1', 'Message', 'info', 'medical', 'normal', 1)
        ]
        
        for notif in notifications:
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, type, category, priority, is_read)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', notif)
        
        conn.commit()
        conn.close()
        
        # Get statistics
        with self.app.app_context():
            response = self.client.get('/api/notifications/stats?user_id=stats_user')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['total'], 3)
        self.assertEqual(data['unread'], 2)
        self.assertEqual(data['urgent'], 1)
        self.assertEqual(data['high_priority'], 1)
    
    def test_notification_filtering(self):
        """Test notification filtering by category and priority"""
        # Create notifications with different categories directly in database
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        notifications = [
            ('filter_user', 'Medical High', 'Msg', 'info', 'medical', 'high'),
            ('filter_user', 'System Low', 'Msg', 'info', 'system', 'low'),
            ('filter_user', 'Medical Normal', 'Msg', 'info', 'medical', 'normal')
        ]
        
        for notif in notifications:
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, type, category, priority)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', notif)
        
        conn.commit()
        conn.close()
        
        # Filter by category
        with self.app.app_context():
            response = self.client.get('/api/notifications?user_id=filter_user&category=medical')
        
        data = json.loads(response.data)
        self.assertEqual(len(data['notifications']), 2)
        
        # Filter by priority
        with self.app.app_context():
            response = self.client.get('/api/notifications?user_id=filter_user&priority=high')
        
        data = json.loads(response.data)
        self.assertEqual(len(data['notifications']), 1)
        self.assertEqual(data['notifications'][0]['title'], 'Medical High')
    
    def test_notification_metadata_handling(self):
        """Test proper handling of notification metadata"""
        metadata = {
            "diagnosis_id": "12345",
            "severity": "medium",
            "follow_up_required": True,
            "nested": {"key": "value"}
        }
        
        # Insert directly into database to test retrieval
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (user_id, title, message, metadata)
            VALUES (?, ?, ?, ?)
        ''', ('metadata_user', 'Metadata Test', 'Testing metadata', json.dumps(metadata)))
        conn.commit()
        conn.close()
        
        # Retrieve and verify metadata
        with self.app.app_context():
            response = self.client.get('/api/notifications?user_id=metadata_user')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        notification = data['notifications'][0]
        self.assertEqual(notification['metadata'], metadata)
    
    def test_notification_priority_ordering(self):
        """Test that notifications are ordered by priority correctly"""
        priorities = ['low', 'normal', 'high', 'urgent']
        
        # Create notifications directly in database in random order
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        
        for priority in reversed(priorities):
            cursor.execute('''
                INSERT INTO notifications (user_id, title, message, priority)
                VALUES (?, ?, ?, ?)
            ''', ('priority_user', f'{priority.title()} Priority', 'Message', priority))
        
        conn.commit()
        conn.close()
        
        # Retrieve notifications
        with self.app.app_context():
            response = self.client.get('/api/notifications?user_id=priority_user')
        
        data = json.loads(response.data)
        
        # Verify ordering (urgent first, low last)
        notifications = data['notifications']
        self.assertGreaterEqual(len(notifications), 4)
        
        # Find our test notifications and verify order
        test_notifications = [n for n in notifications if n['user_id'] == 'priority_user']
        priorities_found = [n['priority'] for n in test_notifications]
        
        # Check that urgent comes before high, high before normal, normal before low
        urgent_idx = priorities_found.index('urgent') if 'urgent' in priorities_found else -1
        high_idx = priorities_found.index('high') if 'high' in priorities_found else -1
        normal_idx = priorities_found.index('normal') if 'normal' in priorities_found else -1
        low_idx = priorities_found.index('low') if 'low' in priorities_found else -1
        
        if urgent_idx >= 0 and high_idx >= 0:
            self.assertLess(urgent_idx, high_idx)
        if high_idx >= 0 and normal_idx >= 0:
            self.assertLess(high_idx, normal_idx)
        if normal_idx >= 0 and low_idx >= 0:
            self.assertLess(normal_idx, low_idx)


class NotificationIntegrationTestCase(unittest.TestCase):
    """Integration tests for notification system with the full app"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_flask_app_health(self):
        """Test that the Flask app is running correctly"""
        with self.app.app_context():
            response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'MediChain Backend is running!')
    
    def test_notification_endpoints_available(self):
        """Test that all notification endpoints are available"""
        with self.app.app_context():
            # Test GET endpoint
            response = self.client.get('/api/notifications?user_id=test')
            self.assertIn(response.status_code, [200, 400])  # Should not be 404
            
            # Test POST endpoint (will fail validation but route should exist)
            response = self.client.post('/api/notifications')
            self.assertIn(response.status_code, [400, 422])  # Should not be 404
            
            # Test stats endpoint
            response = self.client.get('/api/notifications/stats?user_id=test')
            self.assertEqual(response.status_code, 200)


def run_all_tests():
    """Run all notification system tests"""
    print("🧪 Running Fixed MediChain Notification System Test Suite")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(NotificationSystemTestCase))
    suite.addTests(loader.loadTestsFromTestCase(NotificationIntegrationTestCase))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"🧪 Test Summary:")
    print(f"   ✅ Tests Run: {result.testsRun}")
    print(f"   ❌ Failures: {len(result.failures)}")
    print(f"   🚨 Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            test_name = str(test).split('.')[-1].replace(')', '')
            print(f"   - {test_name}")
    
    if result.errors:
        print(f"\n🚨 Errors:")
        for test, traceback in result.errors:
            test_name = str(test).split('.')[-1].replace(')', '')
            print(f"   - {test_name}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n✅ ALL TESTS PASSED! Notification system is ready for production.")
    else:
        print(f"\n❌ Some tests failed. Please review and fix issues before deploying.")
    
    return success


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)