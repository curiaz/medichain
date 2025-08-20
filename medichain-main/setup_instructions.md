# MediChain Authentication Setup Instructions

## Overview
This document provides step-by-step instructions to set up and test the complete authentication system for MediChain.

## Prerequisites
1. Python 3.8+ installed
2. Node.js 16+ installed
3. Supabase account and project set up

## Backend Setup

### 1. Install Python Dependencies
```bash
cd medichain/backend
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the `medichain/backend` directory:

```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Encryption
AES_ENCRYPTION_KEY=your_32_character_encryption_key

# Flask
FLASK_PORT=5000
FLASK_ENV=development

# JWT Secret (keep this secure)
JWT_SECRET_KEY=your_jwt_secret_key
```

### 3. Database Schema
Run this SQL in your Supabase SQL editor to create the users table:

```sql
CREATE TABLE users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('doctor', 'patient', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create health_records table if not exists
CREATE TABLE IF NOT EXISTS health_records (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID NOT NULL,
    doctor_id UUID,
    diagnosis TEXT NOT NULL,
    prescription TEXT NOT NULL,
    blockchain_tx_hash VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Frontend Setup

### 1. Install Dependencies
```bash
cd medichain
npm install axios
```

### 2. Configure API Base URL
Update the axios configuration in `src/context/AuthContext.jsx` if needed:

```javascript
// Add this line after imports
axios.defaults.baseURL = 'http://localhost:5000';
```

## Testing the Authentication Flow

### 1. Start the Backend
```bash
cd medichain/backend
python app.py
```

### 2. Start the Frontend
```bash
cd medichain
npm start
```

### 3. Test Signup
1. Navigate to http://localhost:3000
2. Click "Sign Up"
3. Choose role (Doctor/Patient)
4. Fill in the signup form
5. Submit and verify success

### 4. Test Login
1. Navigate to http://localhost:3000/login
2. Enter credentials from signup
3. Login and verify redirect to dashboard

### 5. Test Protected Routes
1. Try accessing /dashboard without login - should redirect to login
2. Login and access /dashboard - should work
3. Logout and try accessing /dashboard - should redirect to login

## API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user (protected)
- `POST /api/auth/password-reset-request` - Request password reset
- `POST /api/auth/password-reset` - Reset password

### Medical Records
- `POST /api/medical-records` - Create medical record
- `GET /api/medical-records/:id` - Get specific record
- `GET /api/medical-records/patient/:patient_id` - Get patient records
- `PUT /api/medical-records/:id` - Update record
- `DELETE /api/medical-records/:id` - Delete record

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure Flask-CORS is properly configured
2. **Database Connection**: Verify Supabase credentials in .env
3. **Password Validation**: Check password meets requirements (6+ chars, uppercase, lowercase, digit)
4. **Email Validation**: Ensure valid email format

### Debug Mode
To enable debug mode:
- Backend: Set `FLASK_ENV=development` in .env
- Frontend: Check browser console for errors

## Security Features
- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- Input validation and sanitization
- CORS protection
- HTTPS ready (configure for production)
