"""
Simple notification server for testing - without Supabase dependencies
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import uuid
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Database setup
DB_FILE = os.path.join(os.path.dirname(__file__), 'notifications.db')

def init_notification_db():
    """Initialize the notification database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            action_url TEXT,
            action_label TEXT,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON notifications(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON notifications(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_priority ON notifications(priority)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_is_read ON notifications(is_read)')
    
    conn.commit()
    conn.close()

# Notification API Routes
@app.route('/api/notifications', methods=['GET'])
def get_notifications():
    try:
        user_id = request.args.get('user_id', 'default_user')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        category = request.args.get('category')
        priority = request.args.get('priority')
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Build query
        query = "SELECT * FROM notifications WHERE user_id = ?"
        params = [user_id]
        
        if category:
            query += " AND category = ?"
            params.append(category)
            
        if priority:
            query += " AND priority = ?"
            params.append(priority)
            
        if unread_only:
            query += " AND is_read = 0"
        
        # Order by priority and creation time
        priority_order = "CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END"
        query += f" ORDER BY {priority_order}, created_at DESC"
        
        # Add pagination
        offset = (page - 1) * limit
        query += f" LIMIT {limit} OFFSET {offset}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Convert to dictionaries
        notifications = []
        for row in rows:
            notification = {
                'id': row[0],
                'user_id': row[1],
                'title': row[2],
                'message': row[3],
                'type': row[4],
                'category': row[5],
                'priority': row[6],
                'is_read': bool(row[7]),
                'action_url': row[8],
                'action_label': row[9],
                'metadata': json.loads(row[10]) if row[10] else {},
                'created_at': row[11],
                'updated_at': row[12]
            }
            notifications.append(notification)
        
        conn.close()
        
        return jsonify({
            'notifications': notifications,
            'page': page,
            'limit': limit,
            'total': len(notifications)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications', methods=['POST'])
def create_notification():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['user_id', 'title', 'message', 'type', 'category', 'priority']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create notification
        notification_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications (
                id, user_id, title, message, type, category, priority,
                is_read, action_url, action_label, metadata, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            notification_id,
            data['user_id'],
            data['title'],
            data['message'],
            data['type'],
            data['category'],
            data['priority'],
            False,
            data.get('action_url'),
            data.get('action_label'),
            json.dumps(data.get('metadata', {})),
            current_time,
            current_time
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Notification created successfully',
            'id': notification_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<notification_id>', methods=['PUT'])
def update_notification(notification_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check if notification exists
        cursor.execute('SELECT id FROM notifications WHERE id = ?', (notification_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Notification not found'}), 404
        
        # Update notification
        update_fields = []
        params = []
        
        for field in ['title', 'message', 'type', 'category', 'priority', 'is_read', 'action_url', 'action_label']:
            if field in data:
                update_fields.append(f'{field} = ?')
                params.append(data[field])
        
        if 'metadata' in data:
            update_fields.append('metadata = ?')
            params.append(json.dumps(data['metadata']))
        
        update_fields.append('updated_at = ?')
        params.append(datetime.now().isoformat())
        params.append(notification_id)
        
        query = f"UPDATE notifications SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Notification updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM notifications WHERE id = ?', (notification_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'error': 'Notification not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Notification deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/bulk-read', methods=['POST'])
def bulk_mark_as_read():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        notification_ids = data.get('notification_ids', [])
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        if notification_ids:
            # Mark specific notifications as read
            placeholders = ','.join(['?' for _ in notification_ids])
            query = f"UPDATE notifications SET is_read = 1, updated_at = ? WHERE user_id = ? AND id IN ({placeholders})"
            params = [datetime.now().isoformat(), user_id] + notification_ids
        else:
            # Mark all notifications as read for user
            query = "UPDATE notifications SET is_read = 1, updated_at = ? WHERE user_id = ?"
            params = [datetime.now().isoformat(), user_id]
        
        cursor.execute(query, params)
        updated_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': f'{updated_count} notifications marked as read',
            'updated_count': updated_count
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/stats', methods=['GET'])
def get_notification_stats():
    try:
        user_id = request.args.get('user_id', 'default_user')
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute('SELECT COUNT(*) FROM notifications WHERE user_id = ?', (user_id,))
        total = cursor.fetchone()[0]
        
        # Get unread count
        cursor.execute('SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0', (user_id,))
        unread = cursor.fetchone()[0]
        
        # Get counts by priority
        cursor.execute('''
            SELECT priority, COUNT(*) 
            FROM notifications 
            WHERE user_id = ? 
            GROUP BY priority
        ''', (user_id,))
        
        priority_counts = dict(cursor.fetchall())
        
        conn.close()
        
        return jsonify({
            'total': total,
            'unread': unread,
            'by_priority': {
                'high': priority_counts.get('high', 0),
                'medium': priority_counts.get('medium', 0),
                'low': priority_counts.get('low', 0)
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'MediChain Notification Service'}), 200

if __name__ == '__main__':
    print("🔧 Initializing notification database...")
    init_notification_db()
    print("✅ Notification database initialized")
    print("🚀 Starting MediChain Simple Notification Server...")
    app.run(debug=True, host='0.0.0.0', port=5000)