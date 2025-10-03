-- =============================================================================
-- SETTINGS PAGE DATABASE SCHEMA
-- Complete database setup for notification preferences and security features
-- =============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- TABLE: notification_preferences
-- Stores user notification preferences for various alert types
-- =============================================================================

CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_firebase_uid TEXT NOT NULL,
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE,
    appointment_reminders BOOLEAN DEFAULT TRUE,
    diagnosis_alerts BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT notification_preferences_user_unique UNIQUE(user_firebase_uid)
);

-- Add foreign key constraint if user_profiles table exists
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'user_profiles') THEN
        ALTER TABLE notification_preferences 
        ADD CONSTRAINT fk_notification_preferences_user 
        FOREIGN KEY (user_firebase_uid) 
        REFERENCES user_profiles(firebase_uid) 
        ON DELETE CASCADE;
    END IF;
END $$;

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_notification_preferences_user 
    ON notification_preferences(user_firebase_uid);

CREATE INDEX IF NOT EXISTS idx_notification_preferences_updated 
    ON notification_preferences(updated_at DESC);

-- =============================================================================
-- TABLE: security_audit_log
-- Comprehensive audit trail for all security-related actions
-- =============================================================================

CREATE TABLE IF NOT EXISTS security_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_firebase_uid TEXT NOT NULL,
    action TEXT NOT NULL,
    action_type TEXT DEFAULT 'security',
    description TEXT,
    ip_address TEXT,
    user_agent TEXT,
    status TEXT DEFAULT 'success',
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_security_audit_user 
    ON security_audit_log(user_firebase_uid);

CREATE INDEX IF NOT EXISTS idx_security_audit_timestamp 
    ON security_audit_log(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_security_audit_action 
    ON security_audit_log(action);

CREATE INDEX IF NOT EXISTS idx_security_audit_status 
    ON security_audit_log(status);

CREATE INDEX IF NOT EXISTS idx_security_audit_metadata 
    ON security_audit_log USING gin(metadata);

-- =============================================================================
-- TABLE: password_history
-- Track password changes to prevent reuse of recent passwords
-- =============================================================================

CREATE TABLE IF NOT EXISTS password_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_firebase_uid TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_password_history_user 
    ON password_history(user_firebase_uid);

CREATE INDEX IF NOT EXISTS idx_password_history_changed 
    ON password_history(changed_at DESC);

-- =============================================================================
-- TABLE: account_deletion_requests
-- Track account deletion requests with grace period
-- =============================================================================

CREATE TABLE IF NOT EXISTS account_deletion_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_firebase_uid TEXT NOT NULL,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scheduled_deletion_at TIMESTAMP WITH TIME ZONE,
    reason TEXT,
    status TEXT DEFAULT 'pending',
    cancelled_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT account_deletion_user_unique UNIQUE(user_firebase_uid)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_deletion_requests_user 
    ON account_deletion_requests(user_firebase_uid);

CREATE INDEX IF NOT EXISTS idx_deletion_requests_status 
    ON account_deletion_requests(status);

CREATE INDEX IF NOT EXISTS idx_deletion_requests_scheduled 
    ON account_deletion_requests(scheduled_deletion_at);

-- =============================================================================
-- TABLE: user_sessions
-- Track active user sessions for security monitoring
-- =============================================================================

CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_firebase_uid TEXT NOT NULL,
    session_token TEXT NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    device_info JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT TRUE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT user_sessions_token_unique UNIQUE(session_token)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_user_sessions_user 
    ON user_sessions(user_firebase_uid);

CREATE INDEX IF NOT EXISTS idx_user_sessions_token 
    ON user_sessions(session_token);

CREATE INDEX IF NOT EXISTS idx_user_sessions_active 
    ON user_sessions(is_active, last_activity_at DESC);

-- =============================================================================
-- FUNCTIONS AND TRIGGERS
-- =============================================================================

-- Function to update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for notification_preferences
DROP TRIGGER IF EXISTS update_notification_preferences_updated_at ON notification_preferences;
CREATE TRIGGER update_notification_preferences_updated_at
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for account_deletion_requests
DROP TRIGGER IF EXISTS update_deletion_requests_updated_at ON account_deletion_requests;
CREATE TRIGGER update_deletion_requests_updated_at
    BEFORE UPDATE ON account_deletion_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically set deletion schedule (30 days from request)
CREATE OR REPLACE FUNCTION set_deletion_schedule()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.scheduled_deletion_at IS NULL THEN
        NEW.scheduled_deletion_at = NEW.requested_at + INTERVAL '30 days';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to set deletion schedule
DROP TRIGGER IF EXISTS set_deletion_schedule_trigger ON account_deletion_requests;
CREATE TRIGGER set_deletion_schedule_trigger
    BEFORE INSERT ON account_deletion_requests
    FOR EACH ROW
    EXECUTE FUNCTION set_deletion_schedule();

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================================================

-- Enable RLS on notification_preferences
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;

-- Users can view their own preferences
DROP POLICY IF EXISTS "Users can view own notification preferences" ON notification_preferences;
CREATE POLICY "Users can view own notification preferences"
    ON notification_preferences
    FOR SELECT
    USING (user_firebase_uid = current_setting('app.current_user_id', true));

-- Users can insert their own preferences
DROP POLICY IF EXISTS "Users can insert own notification preferences" ON notification_preferences;
CREATE POLICY "Users can insert own notification preferences"
    ON notification_preferences
    FOR INSERT
    WITH CHECK (user_firebase_uid = current_setting('app.current_user_id', true));

-- Users can update their own preferences
DROP POLICY IF EXISTS "Users can update own notification preferences" ON notification_preferences;
CREATE POLICY "Users can update own notification preferences"
    ON notification_preferences
    FOR UPDATE
    USING (user_firebase_uid = current_setting('app.current_user_id', true));

-- Enable RLS on security_audit_log
ALTER TABLE security_audit_log ENABLE ROW LEVEL SECURITY;

-- Users can view their own audit logs
DROP POLICY IF EXISTS "Users can view own security audit log" ON security_audit_log;
CREATE POLICY "Users can view own security audit log"
    ON security_audit_log
    FOR SELECT
    USING (user_firebase_uid = current_setting('app.current_user_id', true));

-- Service role can insert any audit logs
DROP POLICY IF EXISTS "Service role can insert security audit logs" ON security_audit_log;
CREATE POLICY "Service role can insert security audit logs"
    ON security_audit_log
    FOR INSERT
    WITH CHECK (true);

-- Enable RLS on account_deletion_requests
ALTER TABLE account_deletion_requests ENABLE ROW LEVEL SECURITY;

-- Users can view their own deletion requests
DROP POLICY IF EXISTS "Users can view own deletion requests" ON account_deletion_requests;
CREATE POLICY "Users can view own deletion requests"
    ON account_deletion_requests
    FOR SELECT
    USING (user_firebase_uid = current_setting('app.current_user_id', true));

-- Users can insert their own deletion requests
DROP POLICY IF EXISTS "Users can insert own deletion requests" ON account_deletion_requests;
CREATE POLICY "Users can insert own deletion requests"
    ON account_deletion_requests
    FOR INSERT
    WITH CHECK (user_firebase_uid = current_setting('app.current_user_id', true));

-- Users can update their own deletion requests
DROP POLICY IF EXISTS "Users can update own deletion requests" ON account_deletion_requests;
CREATE POLICY "Users can update own deletion requests"
    ON account_deletion_requests
    FOR UPDATE
    USING (user_firebase_uid = current_setting('app.current_user_id', true));

-- =============================================================================
-- UTILITY FUNCTIONS
-- =============================================================================

-- Function to get notification preferences with defaults
CREATE OR REPLACE FUNCTION get_notification_preferences(p_user_id TEXT)
RETURNS TABLE (
    email_notifications BOOLEAN,
    sms_notifications BOOLEAN,
    appointment_reminders BOOLEAN,
    diagnosis_alerts BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COALESCE(np.email_notifications, TRUE),
        COALESCE(np.sms_notifications, FALSE),
        COALESCE(np.appointment_reminders, TRUE),
        COALESCE(np.diagnosis_alerts, TRUE)
    FROM (SELECT 1) AS dummy
    LEFT JOIN notification_preferences np ON np.user_firebase_uid = p_user_id;
END;
$$ LANGUAGE plpgsql;

-- Function to log security events
CREATE OR REPLACE FUNCTION log_security_event(
    p_user_id TEXT,
    p_action TEXT,
    p_ip_address TEXT DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_status TEXT DEFAULT 'success',
    p_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS UUID AS $$
DECLARE
    v_log_id UUID;
BEGIN
    INSERT INTO security_audit_log (
        user_firebase_uid,
        action,
        ip_address,
        user_agent,
        status,
        metadata
    ) VALUES (
        p_user_id,
        p_action,
        p_ip_address,
        p_user_agent,
        p_status,
        p_metadata
    ) RETURNING id INTO v_log_id;
    
    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql;

-- Function to clean old audit logs (keep last 90 days)
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS INTEGER AS $$
DECLARE
    v_deleted_count INTEGER;
BEGIN
    DELETE FROM security_audit_log
    WHERE timestamp < NOW() - INTERVAL '90 days';
    
    GET DIAGNOSTICS v_deleted_count = ROW_COUNT;
    RETURN v_deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to process pending account deletions
CREATE OR REPLACE FUNCTION process_pending_deletions()
RETURNS TABLE (
    user_id TEXT,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    UPDATE account_deletion_requests
    SET 
        status = 'completed',
        deleted_at = NOW()
    WHERE 
        status = 'pending'
        AND scheduled_deletion_at <= NOW()
    RETURNING user_firebase_uid, status;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- COMMENTS FOR DOCUMENTATION
-- =============================================================================

COMMENT ON TABLE notification_preferences IS 'User notification preferences for email, SMS, appointments, and diagnosis alerts';
COMMENT ON TABLE security_audit_log IS 'Complete audit trail of all security-related actions and events';
COMMENT ON TABLE password_history IS 'Historical record of password changes to prevent password reuse';
COMMENT ON TABLE account_deletion_requests IS 'Tracks account deletion requests with 30-day grace period';
COMMENT ON TABLE user_sessions IS 'Active user sessions for security monitoring and management';

COMMENT ON COLUMN notification_preferences.email_notifications IS 'Enable/disable email notifications';
COMMENT ON COLUMN notification_preferences.sms_notifications IS 'Enable/disable SMS text message notifications';
COMMENT ON COLUMN notification_preferences.appointment_reminders IS 'Enable/disable appointment reminder notifications';
COMMENT ON COLUMN notification_preferences.diagnosis_alerts IS 'Enable/disable AI diagnosis alert notifications';

COMMENT ON COLUMN security_audit_log.action IS 'Type of security action (password_change, login, logout, etc.)';
COMMENT ON COLUMN security_audit_log.action_type IS 'Category of action (security, access, modification, etc.)';
COMMENT ON COLUMN security_audit_log.status IS 'Status of the action (success, failed, blocked, etc.)';
COMMENT ON COLUMN security_audit_log.metadata IS 'Additional JSON metadata about the security event';

COMMENT ON COLUMN account_deletion_requests.status IS 'Status: pending, cancelled, completed';
COMMENT ON COLUMN account_deletion_requests.scheduled_deletion_at IS 'Scheduled date for account deletion (30 days after request)';

-- =============================================================================
-- GRANT PERMISSIONS
-- =============================================================================

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, UPDATE ON notification_preferences TO authenticated;
GRANT SELECT ON security_audit_log TO authenticated;
GRANT INSERT ON security_audit_log TO service_role;
GRANT SELECT, INSERT, UPDATE ON account_deletion_requests TO authenticated;
GRANT SELECT ON user_sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON password_history TO service_role;

-- Grant execute permissions on functions
GRANT EXECUTE ON FUNCTION get_notification_preferences(TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION log_security_event(TEXT, TEXT, TEXT, TEXT, TEXT, JSONB) TO service_role;
GRANT EXECUTE ON FUNCTION cleanup_old_audit_logs() TO service_role;
GRANT EXECUTE ON FUNCTION process_pending_deletions() TO service_role;

-- =============================================================================
-- INITIAL DATA / SEED DATA (Optional)
-- =============================================================================

-- You can add default notification preferences for existing users here if needed

-- =============================================================================
-- VERIFICATION QUERIES
-- =============================================================================

-- Verify tables were created
SELECT 
    tablename,
    schemaname
FROM pg_tables 
WHERE tablename IN (
    'notification_preferences',
    'security_audit_log',
    'password_history',
    'account_deletion_requests',
    'user_sessions'
)
ORDER BY tablename;

-- Verify indexes
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes 
WHERE tablename IN (
    'notification_preferences',
    'security_audit_log',
    'password_history',
    'account_deletion_requests',
    'user_sessions'
)
ORDER BY tablename, indexname;

-- =============================================================================
-- MAINTENANCE TASKS (Run periodically via cron or scheduled jobs)
-- =============================================================================

-- Clean old audit logs (keep last 90 days)
-- SELECT cleanup_old_audit_logs();

-- Process pending account deletions
-- SELECT * FROM process_pending_deletions();

-- =============================================================================
-- ROLLBACK SCRIPT (Use with caution!)
-- =============================================================================

/*
-- Uncomment to drop all settings-related tables

DROP TABLE IF EXISTS user_sessions CASCADE;
DROP TABLE IF EXISTS account_deletion_requests CASCADE;
DROP TABLE IF EXISTS password_history CASCADE;
DROP TABLE IF EXISTS security_audit_log CASCADE;
DROP TABLE IF EXISTS notification_preferences CASCADE;

DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS set_deletion_schedule() CASCADE;
DROP FUNCTION IF EXISTS get_notification_preferences(TEXT) CASCADE;
DROP FUNCTION IF EXISTS log_security_event(TEXT, TEXT, TEXT, TEXT, TEXT, JSONB) CASCADE;
DROP FUNCTION IF EXISTS cleanup_old_audit_logs() CASCADE;
DROP FUNCTION IF EXISTS process_pending_deletions() CASCADE;
*/
