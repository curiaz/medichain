-- MediChain Settings Page Database Schema
-- Complete schema for notification preferences, password history, and account management

-- ============================================================================
-- NOTIFICATION PREFERENCES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_firebase_uid TEXT NOT NULL UNIQUE REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    email_notifications BOOLEAN DEFAULT true,
    sms_notifications BOOLEAN DEFAULT false,
    appointment_reminders BOOLEAN DEFAULT true,
    diagnosis_alerts BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_notification_prefs_user_id ON notification_preferences(user_firebase_uid);

-- ============================================================================
-- PASSWORD HISTORY TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS password_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_firebase_uid TEXT NOT NULL REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    password_hash TEXT NOT NULL,
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address TEXT,
    user_agent TEXT
);

-- Index for password history lookups
CREATE INDEX IF NOT EXISTS idx_password_history_user_id ON password_history(user_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_password_history_changed_at ON password_history(changed_at DESC);

-- ============================================================================
-- ACCOUNT DELETION REQUESTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS account_deletion_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_firebase_uid TEXT NOT NULL REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    requested_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scheduled_deletion_at TIMESTAMP WITH TIME ZONE NOT NULL,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    reason TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'cancelled', 'completed')),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for deletion requests
CREATE INDEX IF NOT EXISTS idx_deletion_requests_user_id ON account_deletion_requests(user_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_deletion_requests_status ON account_deletion_requests(status);
CREATE INDEX IF NOT EXISTS idx_deletion_requests_scheduled ON account_deletion_requests(scheduled_deletion_at);

-- ============================================================================
-- SECURITY AUDIT LOG TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS security_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_firebase_uid TEXT NOT NULL REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    action TEXT NOT NULL,
    action_type TEXT DEFAULT 'security',
    description TEXT,
    ip_address TEXT,
    user_agent TEXT,
    status TEXT DEFAULT 'success' CHECK (status IN ('success', 'failed', 'blocked')),
    error_message TEXT,
    metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for audit log
CREATE INDEX IF NOT EXISTS idx_security_audit_user_id ON security_audit_log(user_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_security_audit_timestamp ON security_audit_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_security_audit_action ON security_audit_log(action);
CREATE INDEX IF NOT EXISTS idx_security_audit_status ON security_audit_log(status);

-- ============================================================================
-- USER SESSIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_firebase_uid TEXT NOT NULL REFERENCES user_profiles(firebase_uid) ON DELETE CASCADE,
    session_token TEXT NOT NULL UNIQUE,
    device_info TEXT,
    browser_info TEXT,
    ip_address TEXT,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for sessions
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_firebase_uid);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_active ON user_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_user_sessions_last_activity ON user_sessions(last_activity_at DESC);

-- ============================================================================
-- UPDATE user_profiles TABLE TO ADD ACCOUNT STATUS FIELDS
-- ============================================================================
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS account_status TEXT DEFAULT 'active' CHECK (account_status IN ('active', 'deactivated', 'pending_deletion', 'deleted')),
ADD COLUMN IF NOT EXISTS deactivated_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS deactivation_reason TEXT,
ADD COLUMN IF NOT EXISTS deletion_requested_at TIMESTAMP WITH TIME ZONE;

-- Index for account status
CREATE INDEX IF NOT EXISTS idx_user_profiles_account_status ON user_profiles(account_status);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE account_deletion_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE security_audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- Notification Preferences Policies
CREATE POLICY "Users can view their own notification preferences"
    ON notification_preferences FOR SELECT
    USING (auth.uid()::text = user_firebase_uid);

CREATE POLICY "Users can update their own notification preferences"
    ON notification_preferences FOR UPDATE
    USING (auth.uid()::text = user_firebase_uid);

CREATE POLICY "Users can insert their own notification preferences"
    ON notification_preferences FOR INSERT
    WITH CHECK (auth.uid()::text = user_firebase_uid);

-- Password History Policies (read-only for users, write for system)
CREATE POLICY "Users can view their own password history"
    ON password_history FOR SELECT
    USING (auth.uid()::text = user_firebase_uid);

-- Account Deletion Requests Policies
CREATE POLICY "Users can view their own deletion requests"
    ON account_deletion_requests FOR SELECT
    USING (auth.uid()::text = user_firebase_uid);

CREATE POLICY "Users can create their own deletion requests"
    ON account_deletion_requests FOR INSERT
    WITH CHECK (auth.uid()::text = user_firebase_uid);

CREATE POLICY "Users can update their own deletion requests"
    ON account_deletion_requests FOR UPDATE
    USING (auth.uid()::text = user_firebase_uid);

-- Security Audit Log Policies (read-only for users)
CREATE POLICY "Users can view their own security audit log"
    ON security_audit_log FOR SELECT
    USING (auth.uid()::text = user_firebase_uid);

-- User Sessions Policies
CREATE POLICY "Users can view their own sessions"
    ON user_sessions FOR SELECT
    USING (auth.uid()::text = user_firebase_uid);

CREATE POLICY "Users can update their own sessions"
    ON user_sessions FOR UPDATE
    USING (auth.uid()::text = user_firebase_uid);

-- ============================================================================
-- FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_notification_preferences_updated_at
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_account_deletion_requests_updated_at
    BEFORE UPDATE ON account_deletion_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to clean old password history (keep only last 5)
CREATE OR REPLACE FUNCTION cleanup_old_password_history()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM password_history
    WHERE user_firebase_uid = NEW.user_firebase_uid
    AND id NOT IN (
        SELECT id FROM password_history
        WHERE user_firebase_uid = NEW.user_firebase_uid
        ORDER BY changed_at DESC
        LIMIT 5
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to cleanup old password history
CREATE TRIGGER cleanup_password_history_trigger
    AFTER INSERT ON password_history
    FOR EACH ROW
    EXECUTE FUNCTION cleanup_old_password_history();

-- Function to clean old audit logs (keep only last 90 days)
CREATE OR REPLACE FUNCTION cleanup_old_audit_logs()
RETURNS void AS $$
BEGIN
    DELETE FROM security_audit_log
    WHERE timestamp < NOW() - INTERVAL '90 days';
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DEFAULT DATA
-- ============================================================================

-- Insert default notification preferences for existing users without preferences
INSERT INTO notification_preferences (user_firebase_uid, email_notifications, sms_notifications, appointment_reminders, diagnosis_alerts)
SELECT 
    firebase_uid,
    true,
    false,
    true,
    true
FROM user_profiles
WHERE firebase_uid NOT IN (SELECT user_firebase_uid FROM notification_preferences)
ON CONFLICT (user_firebase_uid) DO NOTHING;

-- ============================================================================
-- COMMENTS
-- ============================================================================

COMMENT ON TABLE notification_preferences IS 'Stores user notification preferences for email, SMS, and app notifications';
COMMENT ON TABLE password_history IS 'Tracks password change history to prevent password reuse';
COMMENT ON TABLE account_deletion_requests IS 'Manages account deletion requests with grace period';
COMMENT ON TABLE security_audit_log IS 'Comprehensive security event logging for compliance and auditing';
COMMENT ON TABLE user_sessions IS 'Tracks active user sessions for security monitoring';

-- ============================================================================
-- GRANTS
-- ============================================================================

-- Grant appropriate permissions to authenticated users
GRANT SELECT, INSERT, UPDATE ON notification_preferences TO authenticated;
GRANT SELECT ON password_history TO authenticated;
GRANT SELECT, INSERT, UPDATE ON account_deletion_requests TO authenticated;
GRANT SELECT ON security_audit_log TO authenticated;
GRANT SELECT, UPDATE ON user_sessions TO authenticated;

-- Service role has full access
GRANT ALL ON notification_preferences TO service_role;
GRANT ALL ON password_history TO service_role;
GRANT ALL ON account_deletion_requests TO service_role;
GRANT ALL ON security_audit_log TO service_role;
GRANT ALL ON user_sessions TO service_role;
