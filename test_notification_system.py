#!/usr/bin/env python3
"""
Comprehensive Unit Test Suite for MediChain Notification System
Tests all notification API endpoints, database operations, and edge cases
"""

import unittest
import json
import sqlite3
import tempfile
import os
import sys
from datetime import datetime, timedelta

# Add the backend directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import Flask app components
try:
    from app import app, init_notifications_db, NOTIFICATIONS_DB_PATH
except ImportError as e:
    print(f"❌ Failed to import app components: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class NotificationSystemTestCase(unittest.TestCase):
    """Test case for the notification system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Create a temporary database for testing
        self.test_db_fd, self.test_db_path = tempfile.mkstemp(suffix='.db')
        
        # Override the database path for testing
        global NOTIFICATIONS_DB_PATH
        self.original_db_path = NOTIFICATIONS_DB_PATH
        NOTIFICATIONS_DB_PATH = self.test_db_path
        
        # Initialize test database
        init_notifications_db()
        
    def tearDown(self):
        """Clean up after tests"""
        global NOTIFICATIONS_DB_PATH
        NOTIFICATIONS_DB_PATH = self.original_db_path
        
        # Close and remove test database
        os.close(self.test_db_fd)
        os.unlink(self.test_db_path)
    
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
    
    def test_create_notification_success(self):
        """Test successful notification creation"""
        notification_data = {
            "user_id": "test_user",
            "title": "Test Notification",
            "message": "This is a test notification",
            "type": "info",
            "category": "general",
            "priority": "normal"
        }
        
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
        # Missing user_id
        notification_data = {
            "title": "Test Notification",
            "message": "This is a test notification"
        }
        
        response = self.client.post('/api/notifications',
                                  data=json.dumps(notification_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('user_id', data['error'])
    
    def test_get_notifications_success(self):
        """Test successful retrieval of notifications"""
        # First create a notification
        notification_data = {
            "user_id": "test_user",
            "title": "Test Notification",
            "message": "This is a test notification"
        }
        
        self.client.post('/api/notifications',
                        data=json.dumps(notification_data),
                        content_type='application/json')
        
        # Now retrieve notifications
        response = self.client.get('/api/notifications?user_id=test_user')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('notifications', data)
        self.assertIn('pagination', data)
        self.assertGreater(len(data['notifications']), 0)
    
    def test_get_notifications_pagination(self):
        """Test notification pagination"""
        # Create multiple notifications
        for i in range(15):
            notification_data = {
                "user_id": "pagination_user",
                "title": f"Notification {i}",
                "message": f"Message {i}"
            }
            self.client.post('/api/notifications',
                           data=json.dumps(notification_data),
                           content_type='application/json')
        
        # Test first page
        response = self.client.get('/api/notifications?user_id=pagination_user&page=1&per_page=10')
        data = json.loads(response.data)
        
        self.assertEqual(len(data['notifications']), 10)
        self.assertEqual(data['pagination']['page'], 1)
        self.assertEqual(data['pagination']['total'], 15)
        
        # Test second page
        response = self.client.get('/api/notifications?user_id=pagination_user&page=2&per_page=10')
        data = json.loads(response.data)
        
        self.assertEqual(len(data['notifications']), 5)
        self.assertEqual(data['pagination']['page'], 2)
    
    def test_update_notification_mark_read(self):
        """Test marking notification as read"""
        # Create a notification
        notification_data = {
            "user_id": "test_user",
            "title": "Test Notification",
            "message": "This is a test notification"
        }
        
        response = self.client.post('/api/notifications',
                                  data=json.dumps(notification_data),
                                  content_type='application/json')
        
        notification_id = json.loads(response.data)['notification_id']
        
        # Mark as read
        update_data = {"is_read": True}
        response = self.client.put(f'/api/notifications/{notification_id}',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Notification updated successfully')
    
    def test_update_notification_not_found(self):
        """Test updating non-existent notification"""
        update_data = {"is_read": True}
        response = self.client.put('/api/notifications/99999',
                                 data=json.dumps(update_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_delete_notification_success(self):
        """Test successful notification deletion"""
        # Create a notification
        notification_data = {
            "user_id": "test_user",
            "title": "Test Notification",
            "message": "This is a test notification"
        }
        
        response = self.client.post('/api/notifications',
                                  data=json.dumps(notification_data),
                                  content_type='application/json')
        
        notification_id = json.loads(response.data)['notification_id']
        
        # Delete the notification
        response = self.client.delete(f'/api/notifications/{notification_id}')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Notification deleted successfully')
    
    def test_delete_notification_not_found(self):
        """Test deleting non-existent notification"""
        response = self.client.delete('/api/notifications/99999')
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_bulk_mark_as_read(self):
        """Test bulk marking notifications as read"""
        # Create multiple notifications
        notification_ids = []
        for i in range(3):
            notification_data = {
                "user_id": "bulk_user",
                "title": f"Bulk Notification {i}",
                "message": f"Message {i}"
            }
            response = self.client.post('/api/notifications',
                                      data=json.dumps(notification_data),
                                      content_type='application/json')
            notification_ids.append(json.loads(response.data)['notification_id'])
        
        # Mark specific notifications as read
        bulk_data = {
            "user_id": "bulk_user",
            "notification_ids": notification_ids[:2]  # Only first two
        }
        
        response = self.client.post('/api/notifications/bulk-read',
                                  data=json.dumps(bulk_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['updated_count'], 2)
    
    def test_notification_statistics(self):
        """Test notification statistics endpoint"""
        # Create notifications with different statuses
        notifications = [
            {"user_id": "stats_user", "title": "Unread 1", "message": "Message", "priority": "high"},
            {"user_id": "stats_user", "title": "Unread 2", "message": "Message", "priority": "urgent"},
            {"user_id": "stats_user", "title": "Read 1", "message": "Message", "category": "medical"}
        ]
        
        notification_ids = []
        for notif in notifications:
            response = self.client.post('/api/notifications',
                                      data=json.dumps(notif),
                                      content_type='application/json')
            notification_ids.append(json.loads(response.data)['notification_id'])
        
        # Mark one as read
        update_data = {"is_read": True}
        self.client.put(f'/api/notifications/{notification_ids[2]}',
                       data=json.dumps(update_data),
                       content_type='application/json')
        
        # Get statistics
        response = self.client.get('/api/notifications/stats?user_id=stats_user')
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['total'], 3)
        self.assertEqual(data['unread'], 2)
        self.assertEqual(data['urgent'], 1)
        self.assertEqual(data['high_priority'], 1)
    
    def test_notification_filtering(self):
        """Test notification filtering by category and priority"""
        # Create notifications with different categories and priorities
        notifications = [
            {"user_id": "filter_user", "title": "Medical High", "message": "Msg", 
             "category": "medical", "priority": "high"},
            {"user_id": "filter_user", "title": "System Low", "message": "Msg", 
             "category": "system", "priority": "low"},
            {"user_id": "filter_user", "title": "Medical Normal", "message": "Msg", 
             "category": "medical", "priority": "normal"}
        ]
        
        for notif in notifications:
            self.client.post('/api/notifications',
                           data=json.dumps(notif),
                           content_type='application/json')
        
        # Filter by category
        response = self.client.get('/api/notifications?user_id=filter_user&category=medical')
        data = json.loads(response.data)
        self.assertEqual(len(data['notifications']), 2)
        
        # Filter by priority
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
        
        notification_data = {
            "user_id": "metadata_user",
            "title": "Metadata Test",
            "message": "Testing metadata",
            "metadata": metadata
        }
        
        response = self.client.post('/api/notifications',
                                  data=json.dumps(notification_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 201)
        
        # Retrieve and verify metadata
        response = self.client.get('/api/notifications?user_id=metadata_user')
        data = json.loads(response.data)
        
        notification = data['notifications'][0]
        self.assertEqual(notification['metadata'], metadata)
    
    def test_notification_priority_ordering(self):
        """Test that notifications are ordered by priority correctly"""
        priorities = ['low', 'normal', 'high', 'urgent']
        
        # Create notifications in random order
        for priority in reversed(priorities):
            notification_data = {
                "user_id": "priority_user",
                "title": f"{priority.title()} Priority",
                "message": "Message",
                "priority": priority
            }
            self.client.post('/api/notifications',
                           data=json.dumps(notification_data),
                           content_type='application/json')
        
        # Retrieve notifications
        response = self.client.get('/api/notifications?user_id=priority_user')
        data = json.loads(response.data)
        
        # Verify ordering (urgent first, low last)
        notifications = data['notifications']
        self.assertEqual(notifications[0]['priority'], 'urgent')
        self.assertEqual(notifications[1]['priority'], 'high')
        self.assertEqual(notifications[2]['priority'], 'normal')
        self.assertEqual(notifications[3]['priority'], 'low')


class NotificationIntegrationTestCase(unittest.TestCase):
    """Integration tests for notification system with the full app"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_flask_app_health(self):
        """Test that the Flask app is running correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'MediChain Backend is running!')
    
    def test_notification_endpoints_available(self):
        """Test that all notification endpoints are available"""
        # Test GET endpoint
        response = self.client.get('/api/notifications?user_id=test')
        self.assertIn(response.status_code, [200, 400])  # Should not be 404
        
        # Test POST endpoint
        response = self.client.post('/api/notifications')
        self.assertIn(response.status_code, [400, 422])  # Should not be 404
        
        # Test stats endpoint
        response = self.client.get('/api/notifications/stats?user_id=test')
        self.assertEqual(response.status_code, 200)


def run_all_tests():
    """Run all notification system tests"""
    print("🧪 Running MediChain Notification System Test Suite")
    print("=" * 60)
    
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
    print("\n" + "=" * 60)
    print(f"🧪 Test Summary:")
    print(f"   ✅ Tests Run: {result.testsRun}")
    print(f"   ❌ Failures: {len(result.failures)}")
    print(f"   🚨 Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.splitlines()[-1]}")
    
    if result.errors:
        print(f"\n🚨 Errors:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.splitlines()[-1]}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n✅ ALL TESTS PASSED! Notification system is ready for production.")
    else:
        print(f"\n❌ Some tests failed. Please review and fix issues before deploying.")
    
    return success


if __name__ == '__main__':
    run_all_tests()