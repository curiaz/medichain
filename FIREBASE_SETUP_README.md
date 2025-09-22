# MediChain Firebase + Supabase Integration Setup Guide

## 📋 Overview

This guide will help you set up MediChain with Firebase Authentication and Supabase Database integration. The system uses Firebase for user authentication and Supabase for data storage with Row Level Security (RLS).

## 🏗️ Architecture

```
Frontend (React) → Firebase Auth → Backend (Flask) → Supabase Database
     ↓                    ↓              ↓               ↓
   Login/Signup      User Management   API Routes    User Profiles
   User Dashboard    Password Reset    Auth Middleware Medical Records
   Medical Forms     Email Verification Token Validation AI Diagnoses
```

## 🚀 Quick Setup

### 1. Database Setup

Run the database setup script:

**Windows (PowerShell):**
```powershell
.\setup_firebase_db.ps1
```

**Linux/Mac:**
```bash
chmod +x setup_firebase_db.sh
./setup_firebase_db.sh
```

This will:
- Create all database tables
- Apply Row Level Security policies
- Set up Firebase integration

### 2. Backend Setup

1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Configure environment variables:
- Copy `.env.example` to `.env`
- Update Firebase credentials (already done)
- Supabase credentials are already configured

3. Start the backend:
```bash
python app.py
```

### 3. Frontend Setup

1. Install Node dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.frontend.example .env.local
```

3. Update Firebase API Key in `.env.local`:
```env
REACT_APP_FIREBASE_API_KEY=your-actual-api-key-from-firebase-console
REACT_APP_FIREBASE_APP_ID=your-actual-app-id-from-firebase-console
```

4. Start the frontend:
```bash
npm start
```

## 🔧 Manual Database Setup (Alternative)

If you prefer to set up manually:

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Open your project SQL Editor
3. Copy and paste the contents of `database/enhanced_schema.sql`
4. Execute the SQL
5. Copy and paste the contents of `firebase_rls_policies.sql`
6. Execute the SQL

## 📊 Database Schema

### Core Tables

- **`user_profiles`** - Main user information linked to Firebase UID
- **`doctor_profiles`** - Additional doctor-specific data
- **`medical_records`** - Patient medical history and diagnoses
- **`ai_diagnoses`** - AI diagnosis results and feedback
- **`appointments`** - Doctor-patient appointment scheduling
- **`prescriptions`** - Electronic prescriptions

### Key Relationships

```
Firebase Auth User
    ↓ (firebase_uid)
user_profiles (id, firebase_uid, email, role, ...)
    ↓ (id)
doctor_profiles (user_id, firebase_uid, license_number, ...)
```

## 🔐 Security Features

### Row Level Security (RLS)

- **Patient Access**: Can only view their own records
- **Doctor Access**: Can view records for assigned patients
- **Admin Access**: Can view all records
- **Firebase Integration**: Uses Firebase UID for authentication

### Authentication Flow

1. User signs up/logs in via Firebase
2. Firebase returns ID token
3. Backend verifies token with Firebase Admin SDK
4. User data retrieved from Supabase using Firebase UID
5. RLS policies ensure proper access control

## 🧪 Testing the Integration

### 1. Test User Signup

```javascript
// Frontend - Sign up a new user
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from './config/firebase';

const signUp = async (email, password) => {
  const userCredential = await createUserWithEmailAndPassword(auth, email, password);
  const token = await userCredential.user.getIdToken();

  // Create profile in Supabase
  const response = await fetch('/api/auth/create-profile', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      first_name: 'Juan',
      last_name: 'Dela Cruz',
      role: 'patient'
    })
  });

  return response.json();
};
```

### 2. Test Authentication

```javascript
// Frontend - Make authenticated requests
import { auth } from './config/firebase';

const makeAuthenticatedRequest = async () => {
  const token = await auth.currentUser.getIdToken();

  const response = await fetch('/api/auth/verify', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  return response.json();
};
```

## 🔧 Configuration Files

### Backend (.env)
```env
# Firebase Configuration
FIREBASE_PROJECT_ID=medichain-8773b
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@medichain-8773b.iam.gserviceaccount.com

# Supabase Configuration
SUPABASE_URL=https://royvcmfbcghamnbnxdgb.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
```

### Frontend (.env.local)
```env
REACT_APP_SUPABASE_URL=https://royvcmfbcghamnbnxdgb.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_PROJECT_ID=medichain-8773b
```

## 🚨 Important Notes

### Firebase Credentials
- Get API Key and App ID from Firebase Console → Project Settings → General
- Download service account key for backend from Firebase Console → Project Settings → Service Accounts

### Supabase Setup
- URL and keys are in Supabase Dashboard → Settings → API
- Make sure RLS is enabled on all tables
- Test policies in Supabase Dashboard → Table Editor

### Environment Variables
- Never commit `.env` files to version control
- Use different credentials for development/production
- Keep service account keys secure

## 🐛 Troubleshooting

### Common Issues

1. **Firebase initialization error**
   - Check if API key and project ID are correct
   - Verify service account key format

2. **Supabase connection error**
   - Check URL and anon key
   - Verify RLS policies are applied

3. **Authentication not working**
   - Check Firebase token expiration
   - Verify backend Firebase credentials

4. **Database permission errors**
   - Check RLS policies
   - Verify user roles in database

## 📞 Support

If you encounter issues:

1. Check the browser console for errors
2. Verify all environment variables are set
3. Test Firebase and Supabase consoles directly
4. Check backend logs for authentication errors

## 🎯 Next Steps

1. Complete the database setup
2. Test user registration and login
3. Implement the medical record features
4. Add AI diagnosis integration
5. Set up appointment scheduling

---

**🎉 Your MediChain system is now ready for secure, scalable healthcare management!**</content>
<parameter name="filePath">c:\Users\abayo\OneDrive\Desktop\thesis\medichain\FIREBASE_SETUP_README.md
