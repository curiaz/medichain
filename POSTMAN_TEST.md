# Postman Test Guide for Blockchain Audit Ledger

## Test 1: Simple Test Endpoint (No Auth Required)

**Endpoint:** `POST http://localhost:5000/api/admin/audit/test-insert`

**Method:** POST

**Headers:**
```
Content-Type: application/json
```

**Body:** (none needed, but you can leave it empty or use)
```json
{}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Test audit log created successfully",
  "entry_id": "...",
  "block_number": 1,
  "current_hash": "..."
}
```

**Check your backend terminal for:**
```
[DEBUG] ===== TEST INSERT ENDPOINT CALLED =====
[DEBUG] Table exists, query successful. Count: X
[DEBUG] Calling audit_service.log_action...
[DEBUG] ===== AUDIT SERVICE LOG_ACTION CALLED =====
[OK] Audit log created: TEST on test by test@example.com (ID: ...)
```

---

## Test 2: Check Audit Ledger (Requires Admin Auth)

**Endpoint:** `GET http://localhost:5000/api/admin/audit/ledger`

**Method:** GET

**Headers:**
```
Authorization: Bearer YOUR_FIREBASE_ADMIN_TOKEN
Content-Type: application/json
```

**Query Parameters (optional):**
- `page=1` (default: 1)
- `limit=10` (default: 50)
- `action_type=TEST` (filter by action type)
- `entity_type=appointment` (filter by entity type)

**Expected Response:**
```json
{
  "success": true,
  "entries": [
    {
      "id": "...",
      "block_number": 1,
      "previous_hash": "",
      "current_hash": "...",
      "admin_id": "test-user-123",
      "admin_email": "test@example.com",
      "action_type": "TEST",
      "entity_type": "test",
      "created_at": "..."
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 1
  }
}
```

---

## Test 3: Test Profile Update (Requires Auth)

**Endpoint:** `PUT http://localhost:5000/api/profile/update`

**Method:** PUT

**Headers:**
```
Authorization: Bearer YOUR_FIREBASE_TOKEN
Content-Type: application/json
```

**Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

**Check your backend terminal for:**
```
[CRITICAL] ===== UPDATE PROFILE FUNCTION CALLED =====
[AUDIT] Attempting to log: UPDATE_PROFILE on user_profile
[AUDIT] Calling audit_service.log_action...
[AUDIT SUCCESS] ✅ Logged to audit ledger: [id]
```

---

## Test 4: Test Appointment Booking (Requires Auth)

**Endpoint:** `POST http://localhost:5000/api/appointments`

**Method:** POST

**Headers:**
```
Authorization: Bearer YOUR_FIREBASE_TOKEN
Content-Type: application/json
```

**Body:**
```json
{
  "doctor_firebase_uid": "doctor_uid_here",
  "appointment_date": "2025-01-20",
  "appointment_time": "10:00",
  "reason": "Checkup"
}
```

**Check your backend terminal for:**
```
[CRITICAL] ===== CREATE APPOINTMENT FUNCTION CALLED =====
[AUDIT] Attempting to log: BOOK_APPOINTMENT on appointment
[AUDIT] Calling audit_service.log_action...
[AUDIT SUCCESS] ✅ Logged to audit ledger: [id]
```

---

## Test 5: Verify Chain Integrity

**Endpoint:** `GET http://localhost:5000/api/admin/audit/ledger/verify`

**Method:** GET

**Headers:**
```
Authorization: Bearer YOUR_FIREBASE_ADMIN_TOKEN
```

**Expected Response:**
```json
{
  "success": true,
  "is_valid": true,
  "total_blocks": 5,
  "verified_blocks": 5,
  "broken_links": 0,
  "tampered_blocks": []
}
```

---

## Quick Steps:

1. **Start your backend server:**
   ```bash
   cd backend
   python app.py
   ```

2. **Test Endpoint 1 (no auth needed):**
   - Open Postman
   - Create new POST request
   - URL: `http://localhost:5000/api/admin/audit/test-insert`
   - Click Send
   - Check response and backend terminal

3. **Check the audit ledger:**
   - Use the GET endpoint above (needs admin token)
   - Or check Supabase directly: Go to `audit_ledger` table

4. **Test real actions:**
   - Test profile update (needs user token)
   - Test appointment booking (needs user token)
   - Check backend terminal for `[AUDIT]` messages
   - Check Supabase `audit_ledger` table for new entries

---

## Troubleshooting:

**If test-insert returns error:**
- Check backend terminal for error messages
- Verify Supabase connection in `.env` file
- Make sure `audit_ledger` table exists (run `database/create_audit_ledger.sql`)

**If no audit logs appear:**
- Check backend terminal for `[AUDIT]` or `[ERROR]` messages
- Make sure you're using the correct endpoints
- Verify your Firebase token is valid

**If you see `[AUDIT ERROR]`:**
- Check if `audit_service.supabase` is initialized
- Verify database connection
- Check Supabase logs


