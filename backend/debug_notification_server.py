#!/usr/bin/env python3
"""
Simple Debug Notification Server
Standalone Flask server with debug logging for troubleshooting
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os

app = Flask(__name__)

# Enable CORS for all domains and methods
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'notifications.db')

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    print("Health check requested")
    return jsonify({
        'status': 'healthy',
        'service': 'notification-debug-server',
        'database': 'connected' if os.path.exists(DB_PATH) else 'missing'
    })

@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    """Get notifications for a user"""
    user_id = request.args.get('user_id', 'default_user')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    print(f"Getting notifications for user: {user_id}, page: {page}, per_page: {per_page}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Count total notifications
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ?", (user_id,))
        total = cursor.fetchone()[0]
        
        # Get notifications with pagination
        offset = (page - 1) * per_page
        cursor.execute("""
            SELECT * FROM notifications 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (user_id, per_page, offset))
        
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
        
        conn.close()
        
        result = {
            'notifications': notifications,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }
        
        print(f"Returning {len(notifications)} notifications")
        return jsonify(result)
        
    except Exception as e:
        print(f"Error getting notifications: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/stats', methods=['GET'])
def get_notification_stats():
    """Get notification statistics"""
    user_id = request.args.get('user_id', 'default_user')
    
    print(f"Getting stats for user: {user_id}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ?", (user_id,))
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0", (user_id,))
        unread = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND priority = 'high'", (user_id,))
        high_priority = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM notifications WHERE user_id = ? AND priority = 'urgent'", (user_id,))
        urgent = cursor.fetchone()[0]
        
        conn.close()
        
        stats = {
            'stats': {
                'total': total,
                'unread': unread,
                'by_priority': {
                    'high': high_priority,
                    'urgent': urgent
                },
                'by_category': {},
                'recent': total  # Simplified for demo
            }
        }
        
        print(f"Returning stats: {stats}")
        return jsonify(stats)
        
    except Exception as e:
        print(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<int:notification_id>', methods=['PUT'])
def update_notification(notification_id):
    """Update a notification"""
    data = request.get_json()
    user_id = data.get('user_id', 'default_user')
    is_read = data.get('is_read')
    
    print(f"Updating notification {notification_id} for user {user_id}: is_read={is_read}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if is_read is not None:
            cursor.execute("""
                UPDATE notifications 
                SET is_read = ?, updated_at = datetime('now')
                WHERE id = ? AND user_id = ?
            """, (1 if is_read else 0, notification_id, user_id))
        
        conn.commit()
        conn.close()
        
        print(f"Updated notification {notification_id}")
        return jsonify({'success': True, 'message': 'Notification updated'})
        
    except Exception as e:
        print(f"Error updating notification: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Delete a notification"""
    user_id = request.args.get('user_id', 'default_user')
    
    print(f"Deleting notification {notification_id} for user {user_id}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM notifications WHERE id = ? AND user_id = ?", (notification_id, user_id))
        
        conn.commit()
        conn.close()
        
        print(f"Deleted notification {notification_id}")
        return jsonify({'success': True, 'message': 'Notification deleted'})
        
    except Exception as e:
        print(f"Error deleting notification: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/debug/db', methods=['GET'])
def debug_database():
    """Debug endpoint to check database contents"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all notifications
        cursor.execute("SELECT * FROM notifications")
        notifications = [dict(row) for row in cursor.fetchall()]
        
        # Get table info
        cursor.execute("PRAGMA table_info(notifications)")
        table_info = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'database_exists': os.path.exists(DB_PATH),
            'database_path': DB_PATH,
            'table_info': table_info,
            'notifications': notifications
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🔧 Starting Debug Notification Server...")
    print(f"📁 Database path: {DB_PATH}")
    print(f"📊 Database exists: {os.path.exists(DB_PATH)}")
    
    app.run(
        host='0.0.0.0',
        port=5002,  # Use different port
        debug=True,
        threaded=True
    )