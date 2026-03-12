#!/usr/bin/env python3
"""
Notification System Backend Routes
Handles notification CRUD operations and real-time notifications
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import sqlite3
import json
import uuid
import os

# Create notifications blueprint
notifications_bp = Blueprint('notifications', __name__)

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'notifications.db')

def init_notifications_db():
    """Initialize the notifications database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the basic table structure directly (more reliable than reading external file)
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
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_category ON notifications(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, is_read)')
    
    # Create trigger to update read_at timestamp when is_read is changed to 1
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_notification_read_at
            AFTER UPDATE OF is_read ON notifications
            FOR EACH ROW
            WHEN NEW.is_read = 1 AND OLD.is_read = 0
            BEGIN
                UPDATE notifications 
                SET read_at = datetime('now'),
                    updated_at = datetime('now')
                WHERE id = NEW.id;
            END
    ''')
    
    # Create trigger to update updated_at timestamp
    cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_notification_timestamp
            AFTER UPDATE ON notifications
            FOR EACH ROW
            BEGIN
                UPDATE notifications 
                SET updated_at = datetime('now')
                WHERE id = NEW.id;
            END
    ''')
    
    # Insert sample notifications if table is empty
    cursor.execute('SELECT COUNT(*) FROM notifications')
    count = cursor.fetchone()[0]
    
    if count == 0:
        sample_notifications = [
            ('default_user', 'Welcome to MediChain', 'Welcome to our healthcare platform! Your account has been successfully created.', 'success', 'system', 'normal', '/profile', 'Complete Profile', '{"source": "registration"}'),
            ('default_user', 'AI Diagnosis Complete', 'Your symptom analysis is ready for review. Please check your results.', 'info', 'medical', 'high', '/ai-health', 'View Results', '{"diagnosis_id": "123", "condition": "Common Cold"}'),
            ('default_user', 'Medication Reminder', 'Time to take your prescribed medication: Acetaminophen 500mg', 'warning', 'medication', 'high', '/medications', 'Mark as Taken', '{"medication": "Acetaminophen", "dosage": "500mg", "time": "08:00"}'),
            ('default_user', 'Appointment Scheduled', 'Your appointment with Dr. Smith is confirmed for tomorrow at 2:00 PM', 'info', 'appointment', 'normal', '/appointments', 'View Details', '{"appointment_id": "456", "doctor": "Dr. Smith", "date": "2025-10-08"}'),
            ('default_user', 'System Maintenance', 'Scheduled maintenance will occur tonight from 2:00 AM to 4:00 AM EST', 'warning', 'system', 'low', None, None, '{"maintenance_window": "2025-10-08 02:00 - 04:00"}'),
            ('test_user', 'Test Notification', 'This is a test notification for development purposes.', 'info', 'system', 'normal', None, None, '{"test": true}')
        ]
        
        cursor.executemany('''
            INSERT INTO notifications (user_id, title, message, type, category, priority, action_url, action_label, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_notifications)
    
    # Create notification preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_preferences (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL UNIQUE,
            email_enabled BOOLEAN DEFAULT TRUE,
            push_enabled BOOLEAN DEFAULT TRUE,
            sms_enabled BOOLEAN DEFAULT FALSE,
            categories TEXT DEFAULT '[]',
            quiet_hours_start TEXT DEFAULT '22:00',
            quiet_hours_end TEXT DEFAULT '08:00',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create notification logs table for tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notification_logs (
            id TEXT PRIMARY KEY,
            notification_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            FOREIGN KEY (notification_id) REFERENCES notifications (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@notifications_bp.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get notifications for a user with filtering and pagination"""
    try:
        # Get query parameters
        user_id = request.args.get('user_id', 'default_user')
        category = request.args.get('category', '')
        is_read = request.args.get('is_read', '')
        priority = request.args.get('priority', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        conn = get_db_connection()
        
        # Build query with filters
        query = '''
            SELECT * FROM notifications 
            WHERE user_id = ? AND is_archived = FALSE
        '''
        params = [user_id]
        
        if category:
            query += ' AND category = ?'
            params.append(category)
        
        if is_read:
            query += ' AND is_read = ?'
            params.append(is_read.lower() == 'true')
        
        if priority:
            query += ' AND priority = ?'
            params.append(priority)
        
        # Add ordering and pagination
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])
        
        notifications = conn.execute(query, params).fetchall()
        
        # Get total count for pagination
        count_query = '''
            SELECT COUNT(*) as total FROM notifications 
            WHERE user_id = ? AND is_archived = FALSE
        '''
        count_params = [user_id]
        
        if category:
            count_query += ' AND category = ?'
            count_params.append(category)
        
        if is_read:
            count_query += ' AND is_read = ?'
            count_params.append(is_read.lower() == 'true')
        
        if priority:
            count_query += ' AND priority = ?'
            count_params.append(priority)
        
        total = conn.execute(count_query, count_params).fetchone()['total']
        
        conn.close()
        
        # Convert to list of dictionaries
        notifications_list = []
        for notification in notifications:
            notification_dict = dict(notification)
            # Parse metadata JSON if present
            if notification_dict.get('metadata'):
                try:
                    notification_dict['metadata'] = json.loads(notification_dict['metadata'])
                except:
                    notification_dict['metadata'] = {}
            
            notifications_list.append(notification_dict)
        
        return jsonify({
            'success': True,
            'notifications': notifications_list,
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get notifications: {str(e)}'
        }), 500

@notifications_bp.route('/api/notifications', methods=['POST'])
def create_notification():
    """Create a new notification"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user_id', 'title', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Generate notification ID
        notification_id = str(uuid.uuid4())
        
        # Prepare notification data
        notification_data = {
            'id': notification_id,
            'user_id': data['user_id'],
            'title': data['title'],
            'message': data['message'],
            'type': data.get('type', 'info'),
            'priority': data.get('priority', 'normal'),
            'category': data.get('category', 'general'),
            'action_url': data.get('action_url'),
            'action_label': data.get('action_label'),
            'metadata': json.dumps(data.get('metadata', {})),
            'expires_at': data.get('expires_at'),
            'source_system': data.get('source_system', 'medichain')
        }
        
        conn = get_db_connection()
        
        # Insert notification
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO notifications (
                id, user_id, title, message, type, priority, category,
                action_url, action_label, metadata, expires_at, source_system
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            notification_data['id'], notification_data['user_id'],
            notification_data['title'], notification_data['message'],
            notification_data['type'], notification_data['priority'],
            notification_data['category'], notification_data['action_url'],
            notification_data['action_label'], notification_data['metadata'],
            notification_data['expires_at'], notification_data['source_system']
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'notification_id': notification_id,
            'message': 'Notification created successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to create notification: {str(e)}'
        }), 500

@notifications_bp.route('/api/notifications/<notification_id>', methods=['PUT'])
def update_notification(notification_id):
    """Update a notification (mark as read, archive, etc.)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User ID is required'
            }), 400
        
        conn = get_db_connection()
        
        # Check if notification exists and belongs to user
        notification = conn.execute(
            'SELECT * FROM notifications WHERE id = ? AND user_id = ?',
            (notification_id, user_id)
        ).fetchone()
        
        if not notification:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        # Update fields
        update_fields = []
        params = []
        
        if 'is_read' in data:
            update_fields.append('is_read = ?')
            params.append(data['is_read'])
        
        if 'is_archived' in data:
            update_fields.append('is_archived = ?')
            params.append(data['is_archived'])
        
        if update_fields:
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            query = f'UPDATE notifications SET {", ".join(update_fields)} WHERE id = ? AND user_id = ?'
            params.extend([notification_id, user_id])
            
            conn.execute(query, params)
            
            # Log the action
            log_id = str(uuid.uuid4())
            action = 'read' if data.get('is_read') else 'archive' if data.get('is_archived') else 'update'
            conn.execute('''
                INSERT INTO notification_logs (id, notification_id, user_id, action, ip_address)
                VALUES (?, ?, ?, ?, ?)
            ''', (log_id, notification_id, user_id, action, request.remote_addr))
            
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Notification updated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to update notification: {str(e)}'
        }), 500

@notifications_bp.route('/api/notifications/<notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Delete a notification"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User ID is required'
            }), 400
        
        conn = get_db_connection()
        
        # Check if notification exists and belongs to user
        notification = conn.execute(
            'SELECT * FROM notifications WHERE id = ? AND user_id = ?',
            (notification_id, user_id)
        ).fetchone()
        
        if not notification:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        # Delete notification and its logs
        conn.execute('DELETE FROM notification_logs WHERE notification_id = ?', (notification_id,))
        conn.execute('DELETE FROM notifications WHERE id = ? AND user_id = ?', (notification_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Notification deleted successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to delete notification: {str(e)}'
        }), 500

@notifications_bp.route('/api/notifications/bulk', methods=['POST'])
def bulk_update_notifications():
    """Bulk update notifications (mark all as read, archive multiple, etc.)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        action = data.get('action')  # 'mark_all_read', 'archive_all', 'delete_read'
        notification_ids = data.get('notification_ids', [])
        
        if not user_id or not action:
            return jsonify({
                'success': False,
                'error': 'User ID and action are required'
            }), 400
        
        conn = get_db_connection()
        
        if action == 'mark_all_read':
            if notification_ids:
                # Mark specific notifications as read
                placeholders = ','.join(['?' for _ in notification_ids])
                query = f'UPDATE notifications SET is_read = TRUE, updated_at = CURRENT_TIMESTAMP WHERE id IN ({placeholders}) AND user_id = ?'
                params = notification_ids + [user_id]
            else:
                # Mark all unread notifications as read
                query = 'UPDATE notifications SET is_read = TRUE, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND is_read = FALSE'
                params = [user_id]
            
            result = conn.execute(query, params)
            affected_rows = result.rowcount
            
        elif action == 'archive_all':
            if notification_ids:
                placeholders = ','.join(['?' for _ in notification_ids])
                query = f'UPDATE notifications SET is_archived = TRUE, updated_at = CURRENT_TIMESTAMP WHERE id IN ({placeholders}) AND user_id = ?'
                params = notification_ids + [user_id]
            else:
                query = 'UPDATE notifications SET is_archived = TRUE, updated_at = CURRENT_TIMESTAMP WHERE user_id = ? AND is_archived = FALSE'
                params = [user_id]
            
            result = conn.execute(query, params)
            affected_rows = result.rowcount
            
        elif action == 'delete_read':
            query = 'DELETE FROM notifications WHERE user_id = ? AND is_read = TRUE'
            params = [user_id]
            result = conn.execute(query, params)
            affected_rows = result.rowcount
            
        else:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Invalid action'
            }), 400
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'Bulk action completed successfully',
            'affected_rows': affected_rows
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to perform bulk action: {str(e)}'
        }), 500

@notifications_bp.route('/api/notifications/stats', methods=['GET'])
def get_notification_stats():
    """Get notification statistics for a user"""
    try:
        user_id = request.args.get('user_id', 'default_user')
        
        conn = get_db_connection()
        
        # Get various counts
        stats = {}
        
        # Total notifications
        stats['total'] = conn.execute(
            'SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_archived = FALSE',
            (user_id,)
        ).fetchone()['count']
        
        # Unread notifications
        stats['unread'] = conn.execute(
            'SELECT COUNT(*) as count FROM notifications WHERE user_id = ? AND is_read = FALSE AND is_archived = FALSE',
            (user_id,)
        ).fetchone()['count']
        
        # By priority
        priority_stats = conn.execute('''
            SELECT priority, COUNT(*) as count 
            FROM notifications 
            WHERE user_id = ? AND is_archived = FALSE 
            GROUP BY priority
        ''', (user_id,)).fetchall()
        
        stats['by_priority'] = {row['priority']: row['count'] for row in priority_stats}
        
        # By category
        category_stats = conn.execute('''
            SELECT category, COUNT(*) as count 
            FROM notifications 
            WHERE user_id = ? AND is_archived = FALSE 
            GROUP BY category
        ''', (user_id,)).fetchall()
        
        stats['by_category'] = {row['category']: row['count'] for row in category_stats}
        
        # Recent activity (last 7 days)
        stats['recent'] = conn.execute('''
            SELECT COUNT(*) as count 
            FROM notifications 
            WHERE user_id = ? AND created_at >= datetime('now', '-7 days')
        ''', (user_id,)).fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get stats: {str(e)}'
        }), 500

# Initialize database when module is imported
init_notifications_db()