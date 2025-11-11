# AI Health Diagnosis System Implementation

## Overview
This implementation adds a complete AI health diagnosis flow to the MediChain appointment booking system. After selecting a GP, users can input symptoms, upload documents, and the system automatically processes AI diagnosis using Supabase datasets. The AI diagnosis results are displayed on the doctor's schedule page.

## Implementation Summary

### 1. Symptoms Selection Page (`/symptoms-selection`)
- **File**: `src/pages/SymptomsSelection.jsx`
- **Features**:
  - Bubbled UI for symptom selection
  - Searchable symptom list (60+ common symptoms)
  - Multi-select capability
  - Selected symptoms summary
  - Responsive design

### 2. Document Upload Page (`/document-upload`)
- **File**: `src/pages/DocumentUpload.jsx`
- **Features**:
  - Drag-and-drop file upload
  - Support for PDF, JPG, PNG, DOC, DOCX
  - File preview and removal
  - Optional step (can be skipped)
  - Shows selected symptoms summary

### 3. Updated Booking Flow
- **Modified Files**:
  - `src/pages/SelectGP.jsx` - Navigates to symptoms selection
  - `src/pages/SelectDateTime.jsx` - Passes symptoms and documents
  - `src/pages/BookAppointmentForm.jsx` - Sends symptoms and documents to backend

### 4. Database Schema Updates
- **File**: `database/add_appointment_ai_fields.sql`
- **New Fields Added to `appointments` table**:
  - `symptoms` (TEXT[]) - Array of selected symptoms
  - `documents` (JSONB) - Document metadata
  - `ai_diagnosis` (JSONB) - AI diagnosis results
  - `ai_diagnosis_processed` (BOOLEAN) - Processing flag
  - `ai_diagnosis_processed_at` (TIMESTAMP) - Processing timestamp

### 5. Backend AI Processing
- **Modified File**: `backend/appointment_routes.py`
- **Features**:
  - Stores symptoms and documents when creating appointment
  - Automatically processes AI diagnosis after successful booking
  - Uses `StreamlinedAIDiagnosis` class with Supabase datasets
  - Stores top 3 conditions with confidence scores, reasons, and recommendations
  - Non-blocking (appointment creation succeeds even if AI processing fails)

### 6. Doctor Schedule Display
- **Modified File**: `src/pages/DoctorSchedule.jsx`
- **Features**:
  - Displays AI diagnosis in `div.timeslot` format
  - Shows primary condition with confidence score
  - Displays reason and recommended action
  - Lists analyzed symptoms
  - Styled with purple gradient theme

### 7. Styling
- **New Files**:
  - `src/assets/styles/SymptomsSelection.css`
  - `src/assets/styles/DocumentUpload.css`
- **Modified Files**:
  - `src/assets/styles/DoctorAvailability.css` - Added AI diagnosis styles

## User Flow

1. **Select GP** → User selects a doctor from the list
2. **Select Symptoms** → User selects symptoms from bubbled UI (searchable, multi-select)
3. **Upload Documents** → User uploads lab test results or other documents (optional)
4. **Select Date & Time** → User selects appointment slot
5. **Confirm Booking** → Appointment is created
6. **AI Processing** → Backend automatically processes symptoms using Supabase datasets
7. **Doctor View** → Doctor sees AI diagnosis in upcoming appointments

## Database Migration

Run the migration script to add new fields:
```sql
-- Run: database/add_appointment_ai_fields.sql
```

## API Changes

### POST `/api/appointments`
**New Request Fields**:
```json
{
  "doctor_firebase_uid": "...",
  "appointment_date": "2025-11-13",
  "appointment_time": "07:00",
  "appointment_type": "consultation",
  "notes": "...",
  "symptoms": ["Headache", "Fever", "Fatigue"],
  "documents": [
    {
      "name": "lab_results.pdf",
      "size": 102400,
      "type": "application/pdf"
    }
  ]
}
```

**Response** (unchanged):
```json
{
  "success": true,
  "message": "Appointment booked successfully!",
  "appointment": {...}
}
```

## AI Diagnosis Data Structure

The `ai_diagnosis` JSONB field contains:
```json
{
  "primary_condition": "Common Cold",
  "confidence_score": 0.85,
  "detailed_results": [
    {
      "condition": "Common Cold",
      "confidence": 0.85,
      "confidence_percent": "85.0%",
      "reason": "Symptoms match common cold pattern...",
      "recommended_action": "Rest, hydration, over-the-counter medications",
      "medication": "Acetaminophen",
      "dosage": "500mg every 6 hours"
    },
    ...
  ],
  "symptoms_analyzed": ["Headache", "Fever", "Fatigue"],
  "processed_at": "2025-11-13T10:30:00Z"
}
```

## Notes

- AI diagnosis processing is asynchronous and non-blocking
- If AI processing fails, the appointment is still created successfully
- Symptoms are required for AI processing (empty array = no processing)
- Documents are stored as metadata only (file upload to storage should be implemented separately)
- AI diagnosis uses the existing `StreamlinedAIDiagnosis` system with Supabase datasets

## Testing Checklist

- [ ] Run database migration
- [ ] Test symptoms selection flow
- [ ] Test document upload (with and without files)
- [ ] Test booking with symptoms
- [ ] Verify AI diagnosis appears in doctor schedule
- [ ] Test booking without symptoms (should work normally)
- [ ] Verify error handling if AI processing fails

