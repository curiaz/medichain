-- =====================================================
-- NOTIFICATIONS TABLE SCHEMA FOR MEDICHAIN (SERIAL VERSION)
-- Complete notification system with auto-incrementing IDs
-- =====================================================

-- Create notifications table with SERIAL ID
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    
    -- User identification
    user_id VARCHAR(255) NOT NULL, -- Firebase UID or user identifier
    
    -- Notification content
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info' CHECK (type IN ('info', 'success', 'warning', 'error', 'alert')),
    category VARCHAR(50) DEFAULT 'general' CHECK (category IN ('general', 'medical', 'appointment', 'system', 'medication', 'diagnosis', 'profile', 'security')),
    
    -- Priority and status
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    is_read BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    
    -- Action information
    action_url TEXT, -- URL to navigate to when notification is clicked
    action_label VARCHAR(100), -- Text for action button (e.g., "View Appointment", "Review Diagnosis")
    
    -- Metadata and context
    metadata JSONB DEFAULT '{}', -- Additional data like appointment_id, diagnosis_id, etc.
    
    -- Expiration
    expires_at TIMESTAMP WITH TIME ZONE, -- When notification should no longer be shown
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_category ON notifications(category);
CREATE INDEX idx_notifications_priority ON notifications(priority);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
CREATE INDEX idx_notifications_expires_at ON notifications(expires_at);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;

-- Create a function to automatically update read_at timestamp when is_read is set to true
CREATE OR REPLACE FUNCTION update_notification_read_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.is_read = TRUE AND OLD.is_read = FALSE THEN
        NEW.read_at = NOW();
    END IF;
    
    NEW.updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatically updating read_at and updated_at
CREATE TRIGGER trigger_update_notification_read_at
    BEFORE UPDATE ON notifications
    FOR EACH ROW
    EXECUTE FUNCTION update_notification_read_at();

-- Create a function to clean up expired notifications
CREATE OR REPLACE FUNCTION cleanup_expired_notifications()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM notifications 
    WHERE expires_at IS NOT NULL 
    AND expires_at < NOW() 
    AND is_read = TRUE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Optional: Create a view for unread notifications
CREATE VIEW unread_notifications AS
SELECT 
    n.*,
    CASE 
        WHEN n.expires_at IS NOT NULL AND n.expires_at < NOW() THEN TRUE
        ELSE FALSE
    END AS is_expired
FROM notifications n
WHERE n.is_read = FALSE 
AND n.is_archived = FALSE
AND (n.expires_at IS NULL OR n.expires_at > NOW())
ORDER BY 
    CASE n.priority 
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'normal' THEN 3
        WHEN 'low' THEN 4
    END,
    n.created_at DESC;

-- Insert sample notifications for testing
INSERT INTO notifications (user_id, title, message, type, category, priority, action_url, action_label, metadata) VALUES
('default_user', 'Welcome to MediChain', 'Welcome to our healthcare platform! Your account has been successfully created.', 'success', 'system', 'normal', '/profile', 'Complete Profile', '{"source": "registration"}'),
('default_user', 'AI Diagnosis Complete', 'Your symptom analysis is ready for review. Please check your results.', 'info', 'medical', 'high', '/ai-health', 'View Results', '{"diagnosis_id": "123", "condition": "Common Cold"}'),
('default_user', 'Medication Reminder', 'Time to take your prescribed medication: Acetaminophen 500mg', 'warning', 'medication', 'high', '/medications', 'Mark as Taken', '{"medication": "Acetaminophen", "dosage": "500mg", "time": "08:00"}'),
('default_user', 'Appointment Scheduled', 'Your appointment with Dr. Smith is confirmed for tomorrow at 2:00 PM', 'info', 'appointment', 'normal', '/appointments', 'View Details', '{"appointment_id": "456", "doctor": "Dr. Smith", "date": "2025-10-08"}'),
('default_user', 'System Maintenance', 'Scheduled maintenance will occur tonight from 2:00 AM to 4:00 AM EST', 'warning', 'system', 'low', null, null, '{"maintenance_window": "2025-10-08 02:00 - 04:00"}');

-- Create notification statistics view
CREATE VIEW notification_stats AS
SELECT 
    user_id,
    COUNT(*) as total_notifications,
    COUNT(*) FILTER (WHERE is_read = FALSE) as unread_count,
    COUNT(*) FILTER (WHERE priority = 'urgent') as urgent_count,
    COUNT(*) FILTER (WHERE priority = 'high') as high_priority_count,
    COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '7 days') as recent_count,
    COUNT(*) FILTER (WHERE category = 'medical') as medical_count,
    COUNT(*) FILTER (WHERE category = 'appointment') as appointment_count,
    COUNT(*) FILTER (WHERE category = 'medication') as medication_count,
    COUNT(*) FILTER (WHERE category = 'system') as system_count
FROM notifications
GROUP BY user_id;

-- Row Level Security (RLS) policies
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own notifications
CREATE POLICY "Users can view own notifications" ON notifications
    FOR SELECT USING (auth.uid()::text = user_id);

-- Policy: Users can update their own notifications (mark as read, archive, etc.)
CREATE POLICY "Users can update own notifications" ON notifications
    FOR UPDATE USING (auth.uid()::text = user_id);

-- Policy: System can insert notifications for any user
CREATE POLICY "System can insert notifications" ON notifications
    FOR INSERT WITH CHECK (true);

-- Policy: Users can delete their own notifications
CREATE POLICY "Users can delete own notifications" ON notifications
    FOR DELETE USING (auth.uid()::text = user_id);

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON notifications TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE notifications_id_seq TO authenticated;
GRANT SELECT ON unread_notifications TO authenticated;
GRANT SELECT ON notification_stats TO authenticated;

-- Comments for documentation
COMMENT ON TABLE notifications IS 'Stores all user notifications including medical alerts, appointment reminders, and system messages';
COMMENT ON COLUMN notifications.user_id IS 'Firebase UID of the user who should receive this notification';
COMMENT ON COLUMN notifications.type IS 'Visual type of notification (info, success, warning, error, alert)';
COMMENT ON COLUMN notifications.category IS 'Functional category for grouping and filtering notifications';
COMMENT ON COLUMN notifications.priority IS 'Priority level affecting display order and urgency';
COMMENT ON COLUMN notifications.action_url IS 'Optional URL to navigate to when notification is clicked';
COMMENT ON COLUMN notifications.metadata IS 'JSON field for storing additional context data';
COMMENT ON COLUMN notifications.expires_at IS 'Optional expiration date after which notification should not be shown';