# Integration Flow Tests

## Test Scenarios

### 1. Complete Patient Booking Flow
**Steps:**
1. Patient selects GP
2. Patient selects symptoms (multi-select bubbles)
3. Patient uploads documents
4. Patient selects date/time
5. Patient books appointment
6. AI diagnosis is processed automatically
7. Doctor sees appointment with AI diagnosis

**Expected Results:**
- Symptoms are stored in `appointments.symptoms` (array)
- Documents are stored in `appointments.documents` (JSONB)
- AI diagnosis is stored in `appointments.ai_diagnosis` (JSONB)
- `ai_diagnosis_processed` is set to `true`
- Doctor can see AI diagnosis in schedule

### 2. Doctor Reviews AI Diagnosis
**Steps:**
1. Doctor clicks "AI Diagnosis" button in schedule
2. Doctor views 5 slides (Possible Conditions, Recommended Action, Medication, Final Diagnosis, Prescription)
3. Doctor edits Recommended Action
4. Doctor edits Final Diagnosis
5. Doctor edits Prescription
6. Doctor saves medical report

**Expected Results:**
- Medical report is created/updated in `medical_records`
- `review_status` is set to `'reviewed'`
- `updated_at` is automatically updated
- `appointment_id` links report to appointment
- Patient name is fetched and displayed

### 3. Dashboard Statistics Update
**Steps:**
1. Doctor saves medical report
2. Doctor refreshes dashboard

**Expected Results:**
- "Pending Reviews" decreases by 1
- "AI Diagnosis Reviewed" increases by 1
- "Today's Activity" increases by 1
- "Recent Medical Activity" shows new entry with "created for [Patient]"

### 4. Doctor Updates Medical Report
**Steps:**
1. Doctor edits existing medical report
2. Doctor saves changes

**Expected Results:**
- Medical report is updated (not created new)
- `review_status` remains `'reviewed'`
- `updated_at` is automatically updated
- "Today's Activity" updates
- "Recent Medical Activity" shows "updated for [Patient]"

### 5. Patient Views Health Record
**Steps:**
1. Patient logs in
2. Patient views health record

**Expected Results:**
- Only shows Final Diagnosis (from medical report)
- Only shows Prescription (from medical report)
- Does NOT show raw AI diagnosis
- Shows doctor's edited information only

## API Endpoint Tests

### GET /api/medical-reports/doctor
**Test Cases:**
- Returns all medical reports for logged-in doctor
- Ordered by `updated_at` DESC, then `created_at` DESC
- Includes patient info via join or separate query
- Handles missing patient info gracefully
- Returns empty array if no reports

### POST /api/medical-reports
**Test Cases:**
- Creates new medical report with `review_status = 'reviewed'`
- Updates existing medical report with `review_status = 'reviewed'`
- Sets `updated_at` automatically
- Requires `appointment_id` and `patient_firebase_uid`
- Only doctors can create/update

### GET /api/medical-reports/appointment/<appointment_id>
**Test Cases:**
- Returns medical report for specific appointment
- Returns 404 if not found (graceful)
- Verifies access (patient or doctor)
- Returns 403 if unauthorized

## Database Tests

### review_status Column
- Exists with CHECK constraint
- Default value is 'pending'
- Can be 'pending', 'reviewed', or 'in_progress'
- Index exists for performance

### updated_at Column
- Exists with default `now()`
- Trigger automatically updates on row modification
- No NULL values

### appointment_id Column
- Exists with foreign key to appointments
- Can be NULL (for records not linked to appointments)
- Index exists for performance

