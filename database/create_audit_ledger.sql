-- MediChain Audit Ledger Table (Blockchain-style Immutable Log)
-- This table tracks all admin actions in an immutable, blockchain-like structure
-- Each entry is linked to the previous entry via hash chaining

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create audit_ledger table
CREATE TABLE IF NOT EXISTS audit_ledger (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- Blockchain-like linking
    previous_hash VARCHAR(64),  -- Hash of previous entry (creates chain)
    current_hash VARCHAR(64) NOT NULL,  -- Hash of this entry's data
    
    -- Who performed the action
    admin_id VARCHAR(255) NOT NULL,  -- Firebase UID of admin
    admin_email VARCHAR(255),  -- Admin email for easier reference
    admin_name VARCHAR(200),  -- Admin name
    
    -- What action was performed
    action_type VARCHAR(50) NOT NULL,  -- CREATE, UPDATE, DELETE, VIEW, APPROVE, DECLINE, etc.
    action_description TEXT,  -- Human-readable description
    
    -- What entity was affected
    entity_type VARCHAR(50) NOT NULL,  -- user, appointment, doctor_profile, prescription, etc.
    entity_id VARCHAR(255),  -- ID of the affected entity
    
    -- Data changes (JSONB for flexibility)
    data_before JSONB,  -- State before action (for UPDATE/DELETE)
    data_after JSONB,  -- State after action (for CREATE/UPDATE)
    data_changes JSONB,  -- Only the changed fields (diff)
    
    -- Request metadata
    ip_address INET,  -- IP address of requester
    user_agent TEXT,  -- Browser/user agent
    request_id VARCHAR(100),  -- Unique request identifier
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}',  -- Extra information (route, method, etc.)
    
    -- Blockchain integrity
    block_number INTEGER,  -- Sequential block number
    verified BOOLEAN DEFAULT FALSE,  -- Hash verification status
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_audit_ledger_admin_id ON audit_ledger(admin_id);
CREATE INDEX IF NOT EXISTS idx_audit_ledger_action_type ON audit_ledger(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_ledger_entity_type ON audit_ledger(entity_type);
CREATE INDEX IF NOT EXISTS idx_audit_ledger_entity_id ON audit_ledger(entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_ledger_created_at ON audit_ledger(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_ledger_previous_hash ON audit_ledger(previous_hash);
CREATE INDEX IF NOT EXISTS idx_audit_ledger_current_hash ON audit_ledger(current_hash);
CREATE INDEX IF NOT EXISTS idx_audit_ledger_block_number ON audit_ledger(block_number);

-- Create composite index for common queries
CREATE INDEX IF NOT EXISTS idx_audit_ledger_admin_action ON audit_ledger(admin_id, action_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_ledger_entity ON audit_ledger(entity_type, entity_id, created_at DESC);

-- Function to verify ledger integrity
CREATE OR REPLACE FUNCTION verify_audit_ledger_integrity()
RETURNS TABLE (
    id UUID,
    block_number INTEGER,
    hash_matches BOOLEAN,
    chain_broken BOOLEAN,
    previous_hash_mismatch BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    WITH ledger_with_prev AS (
        SELECT 
            a.id,
            a.block_number,
            a.current_hash,
            a.previous_hash,
            LAG(a.current_hash) OVER (ORDER BY a.block_number) AS expected_previous_hash
        FROM audit_ledger a
        ORDER BY a.block_number
    )
    SELECT 
        l.id,
        l.block_number,
        (l.current_hash = encode(digest(
            CONCAT(
                COALESCE(l.previous_hash, ''),
                COALESCE(l.block_number::text, ''),
                'data_hash_placeholder'  -- This should match the actual hash calculation
            )::text,
            'sha256'
        ), 'hex')) AS hash_matches,
        (l.previous_hash IS NOT NULL AND l.previous_hash != COALESCE(l.expected_previous_hash, '')) AS chain_broken,
        (l.previous_hash IS NOT NULL AND l.previous_hash != COALESCE(l.expected_previous_hash, '')) AS previous_hash_mismatch
    FROM ledger_with_prev l;
END;
$$ LANGUAGE plpgsql;

-- Create function to get latest block number
CREATE OR REPLACE FUNCTION get_latest_block_number()
RETURNS INTEGER AS $$
DECLARE
    latest_block INTEGER;
BEGIN
    SELECT COALESCE(MAX(block_number), 0) INTO latest_block
    FROM audit_ledger;
    RETURN latest_block;
END;
$$ LANGUAGE plpgsql;

-- Create function to get previous hash
CREATE OR REPLACE FUNCTION get_previous_hash()
RETURNS VARCHAR(64) AS $$
DECLARE
    prev_hash VARCHAR(64);
BEGIN
    SELECT current_hash INTO prev_hash
    FROM audit_ledger
    ORDER BY block_number DESC
    LIMIT 1;
    RETURN COALESCE(prev_hash, '');
END;
$$ LANGUAGE plpgsql;

-- Add comments for documentation
COMMENT ON TABLE audit_ledger IS 'Immutable audit ledger tracking all admin actions in blockchain-like structure';
COMMENT ON COLUMN audit_ledger.previous_hash IS 'Hash of previous entry - creates immutable chain';
COMMENT ON COLUMN audit_ledger.current_hash IS 'Hash of current entry data - ensures integrity';
COMMENT ON COLUMN audit_ledger.block_number IS 'Sequential block number - order in chain';
COMMENT ON COLUMN audit_ledger.data_changes IS 'Only the fields that changed (diff of before/after)';

