# E-Signature Implementation - Secure Storage

## Overview
This document describes the secure e-signature implementation for doctor signup, including encryption, metadata storage, and update restrictions.

## Features Implemented

### ✅ 1. Save Image to Backend Securely
- E-signature is saved to the `e_signatures` table in the database
- Signature data is stored as encrypted text (not plain image files)
- Separate table ensures proper isolation and security

### ✅ 2. Encrypt Before Storing
- Uses **AES-256-CBC encryption** via `MedicalRecordCrypto` utility
- Encryption key can be set via `ENCRYPTION_KEY` environment variable
- Default key provided for development (should be changed in production)
- Each signature is encrypted with a unique IV (Initialization Vector)

### ✅ 3. Store Timestamp + Doctor ID + IP
- **Timestamp**: Automatically stored in `created_at` and `updated_at` columns
- **Doctor ID**: Stored in `doctor_id` and `firebase_uid` columns
- **IP Address**: Captured from request headers (`X-Forwarded-For` or `remote_addr`)
- **User Agent**: Also stored for additional metadata
- **Signature Hash**: SHA-256 hash stored for integrity verification

### ✅ 4. Only Allow Update After Admin Approval
- Checks `is_approved` flag before allowing updates
- If signature is approved, returns 403 error with clear message
- Frontend displays user-friendly error message
- Prevents unauthorized modifications after approval

## Database Schema

### `e_signatures` Table
```sql
CREATE TABLE e_signatures (
    id UUID PRIMARY KEY,
    doctor_id UUID NOT NULL,
    firebase_uid VARCHAR(255),
    encrypted_signature TEXT NOT NULL,  -- AES-256 encrypted
    signature_hash VARCHAR(64) NOT NULL, -- SHA-256 hash
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_approved BOOLEAN DEFAULT FALSE,
    approved_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID
);
```

## Backend Implementation

### Route: `/api/auth/doctor-signup/step4`
- Handles e-signature separately from other documents
- Validates signature doesn't exist or is not approved before update
- Encrypts signature using AES-256-CBC
- Computes SHA-256 hash for integrity
- Stores metadata (IP, user agent, timestamp)
- Returns appropriate error if update attempted after approval

### Encryption Process
1. Receive signature as base64 data URL
2. Initialize `MedicalRecordCrypto` with encryption key
3. Encrypt signature data using AES-256-CBC
4. Compute SHA-256 hash of original signature
5. Store encrypted data and hash in database

## Frontend Implementation

### SignaturePadModal Component
- Uses `signature_pad` library for drawing
- Displays required message: "Sign inside the box below. This will serve as your official e-signature for diagnosis and prescription"
- Saves signature as PNG data URL
- Integrated into Step 4 (Documents Upload)

### Error Handling
- Shows clear error message if signature cannot be updated after approval
- Displays success message when signature is encrypted and stored
- Validates signature is required before proceeding

## Security Features

1. **Encryption**: AES-256-CBC with unique IV per signature
2. **Integrity**: SHA-256 hash stored for verification
3. **Metadata Tracking**: IP address and user agent logged
4. **Update Protection**: Cannot modify after admin approval
5. **Secure Storage**: Encrypted data stored in database, not as files

## Environment Variables

Add to `.env` file:
```bash
ENCRYPTION_KEY=your-32-byte-encryption-key-here
```

**Important**: Use a strong, randomly generated 32-byte key in production!

## Migration

Run the database migration:
```bash
psql -f database/migrations/create_e_signatures_table.sql
```

## Usage Flow

1. Doctor uploads PRC ID (Front or Back)
2. E-signature modal automatically opens
3. Doctor signs using mouse/touchscreen
4. Signature is saved locally in component state
5. On form submission:
   - Signature is encrypted using AES-256-CBC
   - Hash is computed for integrity
   - Metadata (IP, timestamp, doctor ID) is captured
   - Encrypted signature is stored in database
6. After admin approval:
   - Signature cannot be updated
   - Any update attempt returns 403 error

## API Response

### Success Response
```json
{
  "success": true,
  "message": "Documents uploaded successfully",
  "uploaded_documents": ["prc_id_front", "prc_id_back"],
  "e_signature_saved": true
}
```

### Error Response (After Approval)
```json
{
  "success": false,
  "error": "E-signature cannot be updated after admin approval"
}
```

## Future Enhancements

- Admin route to approve/reject signatures
- Signature decryption endpoint for authorized access
- Signature verification endpoint using hash
- Audit log for signature access



