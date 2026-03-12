-- =====================================================
-- NOTIFICATIONS TABLE SCHEMA FOR MEDICHAIN (SQLite)
-- Local development database schema
-- =====================================================

-- Create notifications table (SQLite version)
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- User identification
    user_id TEXT NOT NULL,
    
    -- Notification content
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'error', 'alert')),
    category TEXT DEFAULT 'general' CHECK (category IN ('general', 'medical', 'appointment', 'system', 'medication', 'diagnosis', 'profile', 'security')),
    
    -- Priority and status
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    is_read INTEGER DEFAULT 0, -- SQLite uses INTEGER for boolean
    is_archived INTEGER DEFAULT 0,
    
    -- Action information
    action_url TEXT,
    action_label TEXT,
    
    -- Metadata and context
    metadata TEXT DEFAULT '{}', -- JSON as TEXT in SQLite
    
    -- Expiration
    expires_at TEXT, -- ISO datetime string
    
    -- Timestamps
    created_at TEXT DEFAULT (datetime('now')),
    read_at TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read ON notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_category ON notifications(category);
CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_user_unread ON notifications(user_id, is_read);

-- Create trigger to update read_at timestamp when is_read is changed to 1
CREATE TRIGGER IF NOT EXISTS update_notification_read_at
    AFTER UPDATE OF is_read ON notifications
    FOR EACH ROW
    WHEN NEW.is_read = 1 AND OLD.is_read = 0
    BEGIN
        UPDATE notifications 
        SET read_at = datetime('now'),
            updated_at = datetime('now')
        WHERE id = NEW.id;
    END;

-- Create trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_notification_timestamp
    AFTER UPDATE ON notifications
    FOR EACH ROW
    BEGIN
        UPDATE notifications 
        SET updated_at = datetime('now')
        WHERE id = NEW.id;
    END;

-- Insert sample notifications for testing
INSERT OR REPLACE INTO notifications (id, user_id, title, message, type, category, priority, action_url, action_label, metadata) VALUES
(1, 'default_user', 'Welcome to MediChain', 'Welcome to our healthcare platform! Your account has been successfully created.', 'success', 'system', 'normal', '/profile', 'Complete Profile', '{"source": "registration"}'),
(2, 'default_user', 'AI Diagnosis Complete', 'Your symptom analysis is ready for review. Please check your results.', 'info', 'medical', 'high', '/ai-health', 'View Results', '{"diagnosis_id": "123", "condition": "Common Cold"}'),
(3, 'default_user', 'Medication Reminder', 'Time to take your prescribed medication: Acetaminophen 500mg', 'warning', 'medication', 'high', '/medications', 'Mark as Taken', '{"medication": "Acetaminophen", "dosage": "500mg", "time": "08:00"}'),
(4, 'default_user', 'Appointment Scheduled', 'Your appointment with Dr. Smith is confirmed for tomorrow at 2:00 PM', 'info', 'appointment', 'normal', '/appointments', 'View Details', '{"appointment_id": "456", "doctor": "Dr. Smith", "date": "2025-10-08"}'),
(5, 'default_user', 'System Maintenance', 'Scheduled maintenance will occur tonight from 2:00 AM to 4:00 AM EST', 'warning', 'system', 'low', NULL, NULL, '{"maintenance_window": "2025-10-08 02:00 - 04:00"}'),
(6, 'test_user', 'Test Notification', 'This is a test notification for development purposes.', 'info', 'system', 'normal', NULL, NULL, '{"test": true}');

-- Create view for unread notifications
CREATE VIEW IF NOT EXISTS unread_notifications AS
SELECT 
    n.*,
    CASE 
        WHEN n.expires_at IS NOT NULL AND datetime(n.expires_at) < datetime('now') THEN 1
        ELSE 0
    END AS is_expired
FROM notifications n
WHERE n.is_read = 0 
AND n.is_archived = 0
AND (n.expires_at IS NULL OR datetime(n.expires_at) > datetime('now'))
ORDER BY 
    CASE n.priority 
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'normal' THEN 3
        WHEN 'low' THEN 4
    END,
    n.created_at DESC;

-- Create view for notification statistics
CREATE VIEW IF NOT EXISTS notification_stats AS
SELECT 
    user_id,
    COUNT(*) as total_notifications,
    SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread_count,
    SUM(CASE WHEN priority = 'urgent' THEN 1 ELSE 0 END) as urgent_count,
    SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) as high_priority_count,
    SUM(CASE WHEN datetime(created_at) >= datetime('now', '-7 days') THEN 1 ELSE 0 END) as recent_count,
    SUM(CASE WHEN category = 'medical' THEN 1 ELSE 0 END) as medical_count,
    SUM(CASE WHEN category = 'appointment' THEN 1 ELSE 0 END) as appointment_count,
    SUM(CASE WHEN category = 'medication' THEN 1 ELSE 0 END) as medication_count,
    SUM(CASE WHEN category = 'system' THEN 1 ELSE 0 END) as system_count
FROM notifications
GROUP BY user_id;