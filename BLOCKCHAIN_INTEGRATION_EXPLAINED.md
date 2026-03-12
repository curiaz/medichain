# Blockchain Integration in MediChain System

## Overview

MediChain uses blockchain technology in **two complementary ways** to ensure data integrity, immutability, and auditability of medical records and administrative actions:

1. **In-Memory Blockchain** (`backend/blockchain.py`) - For medical record hash verification
2. **Database-Based Audit Ledger** (`database/create_audit_ledger.sql` + `backend/services/audit_service.py`) - For immutable admin action logging

---

## 1. In-Memory Blockchain for Medical Records

### Location
- **File**: `backend/blockchain.py`
- **Purpose**: Store cryptographic hashes of medical records to verify integrity

### Architecture

#### Core Components

**Block Class** (`Block`)
- Represents a single block in the chain
- Contains:
  - `index`: Sequential position in chain
  - `timestamp`: When block was created
  - `data`: Medical record information (record_id, encrypted_hash)
  - `previous_hash`: Hash of previous block (creates chain)
  - `nonce`: Used for proof-of-work mining
  - `hash`: SHA-256 hash of block contents

**Blockchain Class** (`Blockchain`)
- Manages the entire chain
- Features:
  - Genesis block (first block)
  - Proof-of-work mining (difficulty = 4 leading zeros)
  - Chain verification
  - Medical record hash storage

### How It Works

```python
# 1. Medical record is created/updated
record_id = "medical_record_123"
encrypted_hash = "abc123def456..."  # Hash of encrypted record

# 2. Hash is added to blockchain
block = medical_blockchain.add_medical_record_hash(record_id, encrypted_hash)

# 3. Block is mined (proof-of-work)
# - Nonce is incremented until hash starts with "0000"
# - Creates computational cost to prevent tampering

# 4. Block is added to chain
# - Links to previous block via previous_hash
# - Creates immutable chain
```

### Key Functions

**`add_medical_record_to_blockchain(record_id, encrypted_hash)`**
- Adds a medical record hash to the blockchain
- Returns: `{block_index, hash, timestamp}`

**`verify_medical_record_integrity(record_id, expected_hash)`**
- Verifies if a record's hash matches what's stored in blockchain
- Returns: `True` if hash matches, `False` otherwise

**`verify_chain()`**
- Validates entire blockchain integrity
- Checks:
  - Each block's hash is correct
  - Each block links correctly to previous block
- Returns: `True` if chain is valid

**`get_blockchain_status()`**
- Returns current blockchain state:
  - Chain length
  - Validity status
  - Latest block info

### Current Status
- **Storage**: In-memory (Python list)
- **Persistence**: Not persisted to database (resets on server restart)
- **Use Case**: Real-time integrity verification during runtime

---

## 2. Database-Based Audit Ledger (Blockchain-Style)

### Location
- **Database Table**: `audit_ledger` (PostgreSQL/Supabase)
- **Service**: `backend/services/audit_service.py`
- **Schema**: `database/create_audit_ledger.sql`

### Purpose
Tracks **all admin actions** in an immutable, blockchain-like structure stored in the database.

### Architecture

#### Database Schema

```sql
CREATE TABLE audit_ledger (
    id UUID PRIMARY KEY,
    
    -- Blockchain-like linking
    previous_hash VARCHAR(64),      -- Hash of previous entry
    current_hash VARCHAR(64),       -- Hash of this entry
    block_number INTEGER,           -- Sequential block number
    
    -- Who performed action
    admin_id VARCHAR(255),          -- Firebase UID
    admin_email VARCHAR(255),
    admin_name VARCHAR(200),
    
    -- What action
    action_type VARCHAR(50),       -- CREATE, UPDATE, DELETE, etc.
    action_description TEXT,
    
    -- What entity affected
    entity_type VARCHAR(50),        -- user, appointment, etc.
    entity_id VARCHAR(255),
    
    -- Data changes
    data_before JSONB,             -- State before action
    data_after JSONB,              -- State after action
    data_changes JSONB,            -- Only changed fields
    
    -- Metadata
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(100),
    metadata JSONB,
    
    -- Integrity
    verified BOOLEAN,
    created_at TIMESTAMP
);
```

### How It Works

#### 1. Hash Chaining
Each entry links to the previous entry via `previous_hash`:

```
Entry 1: previous_hash = "" (first entry)
         current_hash = hash(entry1_data)
         
Entry 2: previous_hash = entry1.current_hash
         current_hash = hash(entry2_data + previous_hash)
         
Entry 3: previous_hash = entry2.current_hash
         current_hash = hash(entry3_data + previous_hash)
```

#### 2. Hash Calculation
The `current_hash` includes ALL entry data:
- Previous hash
- Block number
- Admin info
- Action details
- Entity info
- Data before/after
- Timestamp
- IP address
- User agent

This ensures **any tampering is detectable**.

#### 3. Integrity Verification
The `verify_chain_integrity()` function:
- Checks each entry's hash matches recalculated hash
- Verifies `previous_hash` links are correct
- Detects broken chain links
- Identifies tampered entries

### Integration Points

#### Where Audit Ledger is Used

1. **Profile Management** (`backend/profile_routes.py`)
   - Line 307-334: Logs profile updates
   - Line 757-758: Logs deletions

2. **Appointment Routes** (`backend/appointment_routes.py`)
   - Line 1355: Logs appointment creation
   - Line 2104: Logs appointment updates
   - Line 2432: Logs appointment deletions

3. **Admin Routes** (`backend/admin_audit_routes.py`)
   - Provides API endpoints to view audit ledger
   - Allows querying by admin, action type, entity, date range

### Key Functions

**`AuditService.log_action()`**
- Creates new audit ledger entry
- Calculates hash including all data
- Links to previous entry
- Stores in database

**`AuditService.get_ledger_entries()`**
- Queries audit ledger with filters:
  - Admin ID
  - Action type
  - Entity type/ID
  - Date range
  - Pagination

**`AuditService.verify_chain_integrity()`**
- Verifies entire audit ledger chain
- Detects tampering
- Returns broken links and tampered entries

---

## 3. Frontend Integration

### Audit Ledger Viewer
- **Component**: `src/components/AuditLedger.jsx`
- **Styling**: `src/assets/styles/AuditLedger.css`
- **Features**:
  - Visual blockchain chain representation
  - Expandable blocks showing full details
  - Hash display (click to copy)
  - Filtering by admin, action type, entity
  - Chain integrity verification

### Patient Records Display
- **Page**: `src/pages/Patients.jsx`
- Shows `blockchain_hash` for each patient record
- Allows copying hash for verification

---

## 4. Data Flow Examples

### Example 1: Medical Record Creation

```
1. Doctor creates medical record
   ↓
2. Record encrypted and stored in database
   ↓
3. Hash of encrypted record calculated
   ↓
4. Hash added to in-memory blockchain
   ↓
5. Blockchain transaction returned:
   {
     "block_index": 5,
     "hash": "0000abc123...",
     "timestamp": "2025-01-15T10:30:00"
   }
```

### Example 2: Admin Updates User Profile

```
1. Admin updates user profile via API
   ↓
2. Profile updated in database
   ↓
3. AuditService.log_action() called
   ↓
4. Previous hash retrieved from latest audit entry
   ↓
5. Current hash calculated (includes all entry data)
   ↓
6. New audit entry created:
   {
     "previous_hash": "abc123...",
     "current_hash": "def456...",
     "block_number": 42,
     "admin_id": "admin_uid",
     "action_type": "UPDATE",
     "entity_type": "user",
     "data_before": {...},
     "data_after": {...},
     "data_changes": {...}
   }
   ↓
7. Entry stored in audit_ledger table
   ↓
8. Chain integrity maintained
```

---

## 5. Security Features

### Immutability
- **In-Memory Blockchain**: Blocks cannot be modified (hash verification)
- **Audit Ledger**: Database entries are append-only (previous_hash linking)

### Tamper Detection
- **Hash Verification**: Any change to data changes the hash
- **Chain Verification**: Broken links indicate tampering
- **Recalculation**: Stored hashes can be recalculated and compared

### Integrity Checks
- `verify_chain()` - Validates in-memory blockchain
- `verify_chain_integrity()` - Validates audit ledger
- Both can be run periodically to ensure data integrity

---

## 6. Current Limitations & Future Enhancements

### In-Memory Blockchain Limitations
- ❌ Not persisted (resets on server restart)
- ❌ Single server instance (not distributed)
- ✅ Can be enhanced to persist to database

### Audit Ledger Strengths
- ✅ Persisted in database
- ✅ Immutable chain structure
- ✅ Full audit trail
- ✅ Queryable and searchable

### Potential Enhancements
1. **Persist in-memory blockchain to database**
2. **Distributed blockchain** (multiple nodes)
3. **Smart contracts** for automated verification
4. **Blockchain API endpoints** for external verification
5. **Integration with external blockchain** (Ethereum, Hyperledger)

---

## 7. API Endpoints

### Audit Ledger Endpoints
- `GET /api/admin/audit-ledger` - Get audit entries
- `GET /api/admin/audit-ledger/verify` - Verify chain integrity
- `GET /api/admin/audit-ledger/<admin_id>` - Get admin activity

### Blockchain Status (Potential)
- `GET /api/blockchain/status` - Get blockchain status
- `GET /api/blockchain/verify/<record_id>` - Verify record integrity

---

## Summary

MediChain uses **two-layer blockchain integration**:

1. **In-Memory Blockchain**: Fast, real-time medical record hash verification
2. **Database Audit Ledger**: Persistent, immutable admin action logging

Both systems use:
- ✅ SHA-256 hashing
- ✅ Hash chaining (previous_hash linking)
- ✅ Integrity verification
- ✅ Tamper detection

This provides **comprehensive data integrity** for both medical records and administrative actions, ensuring the system maintains an auditable, tamper-proof record of all critical operations.



