#!/usr/bin/env python3
"""
Simplified Unit Test Suite for MediChain Notification System
Tests the embedded notification API functionality
"""

import unittest
import json
import requests
import time
import threading
import subprocess
import sys
import os
from datetime import datetime


class NotificationAPITestCase(unittest.TestCase):
    """Test case for the notification API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Start the Flask server for testing"""
        cls.base_url = "http://localhost:5000"
        cls.api_url = f"{cls.base_url}/api/notifications"
        
        # Check if server is already running
        try:
            response = requests.get(cls.base_url, timeout=5)
            if response.status_code == 200:
                print("✅ Flask server is already running")
                cls.server_started = True
            else:
                cls.server_started = False
        except requests.exceptions.RequestException:
            cls.server_started = False
        
        if not cls.server_started:
            print("❌ Flask server is not running. Please start it manually: python backend/app.py")
            raise unittest.SkipTest("Flask server not available")
    
    def test_01_server_health(self):
        """Test that the Flask server is running and healthy"""
        response = requests.get(self.base_url, timeout=10)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'MediChain Backend is running!')
    
    def test_02_create_notification(self):
        """Test creating a new notification"""
        notification_data = {
            "user_id": "unittest_user",
            "title": "Unit Test Notification",
            "message": "This notification was created during unit testing",
            "type": "info",
            "category": "system",
            "priority": "normal",
            "metadata": {
                "test": True,
                "test_id": "unit_test_01"
            }
        }
        
        response = requests.post(self.api_url, json=notification_data, timeout=10)
        
        self.assertEqual(response.status_code, 201, f"Expected 201, got {response.status_code}: {response.text}")
        
        data = response.json()
        self.assertIn('notification_id', data)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Notification created successfully')
        
        # Store notification ID for later tests
        self.__class__.test_notification_id = data['notification_id']
    
    def test_03_get_notifications(self):
        """Test retrieving notifications for a user"""
        params = {"user_id": "unittest_user"}
        response = requests.get(self.api_url, params=params, timeout=10)
        
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}: {response.text}")
        
        data = response.json()
        self.assertIn('notifications', data)
        self.assertIn('pagination', data)
        
        notifications = data['notifications']
        self.assertGreater(len(notifications), 0, "Should have at least one notification")
        
        # Verify our test notification exists
        test_notification = next((n for n in notifications if n['title'] == 'Unit Test Notification'), None)
        self.assertIsNotNone(test_notification, "Test notification should exist")
        self.assertEqual(test_notification['user_id'], 'unittest_user')
        self.assertEqual(test_notification['type'], 'info')
        self.assertEqual(test_notification['category'], 'system')
    
    def test_04_get_notification_stats(self):
        """Test getting notification statistics"""
        params = {"user_id": "unittest_user"}
        response = requests.get(f"{self.api_url}/stats", params=params, timeout=10)
        
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}: {response.text}")
        
        data = response.json()
        self.assertIn('total', data)
        self.assertIn('unread', data)
        self.assertIn('categories', data)
        
        self.assertGreater(data['total'], 0, "Should have at least one notification")
        self.assertIn('system', data['categories'], "Should have system category")
    
    def test_05_update_notification(self):
        """Test updating a notification (marking as read)"""
        if not hasattr(self.__class__, 'test_notification_id'):
            self.skipTest("No test notification ID available")
        
        notification_id = self.__class__.test_notification_id
        update_data = {"is_read": True}
        
        response = requests.put(f"{self.api_url}/{notification_id}", json=update_data, timeout=10)
        
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}: {response.text}")
        
        data = response.json()
        self.assertEqual(data['message'], 'Notification updated successfully')
        
        # Verify the notification was marked as read
        params = {"user_id": "unittest_user"}
        response = requests.get(self.api_url, params=params, timeout=10)
        data = response.json()
        
        test_notification = next((n for n in data['notifications'] if n['id'] == notification_id), None)
        self.assertIsNotNone(test_notification)
        self.assertTrue(test_notification['is_read'], "Notification should be marked as read")
    
    def test_06_bulk_mark_as_read(self):
        """Test bulk marking notifications as read"""
        # Create multiple notifications for testing
        notification_ids = []
        
        for i in range(3):
            notification_data = {
                "user_id": "bulk_test_user",
                "title": f"Bulk Test Notification {i}",
                "message": f"Bulk test message {i}",
                "type": "info",
                "category": "general"
            }
            
            response = requests.post(self.api_url, json=notification_data, timeout=10)
            self.assertEqual(response.status_code, 201)
            
            data = response.json()
            notification_ids.append(data['notification_id'])
        
        # Mark first two as read
        bulk_data = {
            "user_id": "bulk_test_user",
            "notification_ids": notification_ids[:2]
        }
        
        response = requests.post(f"{self.api_url}/bulk-read", json=bulk_data, timeout=10)
        
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}: {response.text}")
        
        data = response.json()
        self.assertEqual(data['updated_count'], 2, "Should have updated 2 notifications")
    
    def test_07_notification_filtering(self):
        """Test notification filtering by category and priority"""
        # Create notifications with different categories
        test_notifications = [
            {"user_id": "filter_test_user", "title": "Medical Notification", "message": "Medical msg", 
             "category": "medical", "priority": "high"},
            {"user_id": "filter_test_user", "title": "System Notification", "message": "System msg", 
             "category": "system", "priority": "low"}
        ]
        
        for notif in test_notifications:
            response = requests.post(self.api_url, json=notif, timeout=10)
            self.assertEqual(response.status_code, 201)
        
        # Test category filtering
        params = {"user_id": "filter_test_user", "category": "medical"}
        response = requests.get(self.api_url, params=params, timeout=10)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        medical_notifications = [n for n in data['notifications'] if n['category'] == 'medical']
        self.assertGreater(len(medical_notifications), 0, "Should find medical notifications")
        
        # Test priority filtering
        params = {"user_id": "filter_test_user", "priority": "high"}
        response = requests.get(self.api_url, params=params, timeout=10)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        high_priority_notifications = [n for n in data['notifications'] if n['priority'] == 'high']
        self.assertGreater(len(high_priority_notifications), 0, "Should find high priority notifications")
    
    def test_08_delete_notification(self):
        """Test deleting a notification"""
        if not hasattr(self.__class__, 'test_notification_id'):
            self.skipTest("No test notification ID available")
        
        notification_id = self.__class__.test_notification_id
        
        response = requests.delete(f"{self.api_url}/{notification_id}", timeout=10)
        
        self.assertEqual(response.status_code, 200, f"Expected 200, got {response.status_code}: {response.text}")
        
        data = response.json()
        self.assertEqual(data['message'], 'Notification deleted successfully')
        
        # Verify the notification was deleted
        params = {"user_id": "unittest_user"}
        response = requests.get(self.api_url, params=params, timeout=10)
        data = response.json()
        
        test_notification = next((n for n in data['notifications'] if n['id'] == notification_id), None)
        self.assertIsNone(test_notification, "Deleted notification should not exist")
    
    def test_09_error_handling(self):
        """Test API error handling"""
        # Test missing required fields
        invalid_data = {
            "title": "Missing user_id",
            "message": "This should fail"
        }
        
        response = requests.post(self.api_url, json=invalid_data, timeout=10)
        self.assertEqual(response.status_code, 400)
        
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('user_id', data['error'])
        
        # Test updating non-existent notification
        update_data = {"is_read": True}
        response = requests.put(f"{self.api_url}/99999", json=update_data, timeout=10)
        self.assertEqual(response.status_code, 404)
        
        # Test deleting non-existent notification
        response = requests.delete(f"{self.api_url}/99999", timeout=10)
        self.assertEqual(response.status_code, 404)
    
    def test_10_notification_metadata(self):
        """Test notification metadata handling"""
        metadata = {
            "diagnosis_id": "test_12345",
            "severity": "medium",
            "follow_up": True,
            "nested_data": {
                "key": "value",
                "number": 42
            }
        }
        
        notification_data = {
            "user_id": "metadata_test_user",
            "title": "Metadata Test",
            "message": "Testing metadata handling",
            "type": "info",
            "category": "medical",
            "metadata": metadata
        }
        
        response = requests.post(self.api_url, json=notification_data, timeout=10)
        self.assertEqual(response.status_code, 201)
        
        # Retrieve and verify metadata
        params = {"user_id": "metadata_test_user"}
        response = requests.get(self.api_url, params=params, timeout=10)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        notification = next((n for n in data['notifications'] if n['title'] == 'Metadata Test'), None)
        self.assertIsNotNone(notification)
        self.assertEqual(notification['metadata'], metadata, "Metadata should be preserved exactly")


def run_notification_tests():
    """Run the notification system tests"""
    print("🧪 Running MediChain Notification API Test Suite")
    print("=" * 60)
    print("📝 Note: This requires the Flask server to be running on localhost:5000")
    print("   Start it with: python backend/app.py")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(NotificationAPITestCase)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=False)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"🧪 Test Results Summary:")
    print(f"   ✅ Tests Run: {result.testsRun}")
    print(f"   ✅ Successful: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ Failures: {len(result.failures)}")
    print(f"   🚨 Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ Test Failures:")
        for test, traceback in result.failures:
            test_name = str(test).split('.')[-1].replace(')', '')
            print(f"   - {test_name}")
            # Print last line of traceback for quick debugging
            lines = traceback.strip().split('\n')
            if lines:
                print(f"     {lines[-1]}")
    
    if result.errors:
        print(f"\n🚨 Test Errors:")
        for test, traceback in result.errors:
            test_name = str(test).split('.')[-1].replace(')', '')
            print(f"   - {test_name}")
            # Print last line of traceback for quick debugging
            lines = traceback.strip().split('\n')
            if lines:
                print(f"     {lines[-1]}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    print("\n" + "=" * 60)
    if success:
        print("✅ ALL NOTIFICATION TESTS PASSED!")
        print("🚀 Notification system is ready for production deployment")
    else:
        print("❌ Some tests failed. Review the output above.")
        print("🔧 Fix issues before proceeding with deployment")
    
    print("=" * 60)
    return success


if __name__ == '__main__':
    success = run_notification_tests()
    sys.exit(0 if success else 1)