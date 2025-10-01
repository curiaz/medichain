# 🔧 Firebase Password Reset Debug Guide

## Current Issue Analysis

Based on your error, the problem is likely one of these:

1. **No Firebase user exists** with the email you're testing
2. **Firebase configuration** issue 
3. **Network/CORS** issue
4. **Firebase Authentication not enabled** for email/password

## 🧪 **Step-by-Step Testing Process**

### Step 1: Access the Debug Tool
Navigate to: `http://localhost:3001/debug-firebase`

This page will show you:
- Firebase initialization status
- Detailed error messages
- Step-by-step testing process

### Step 2: Create a Test User (If Needed)
If you don't have a Firebase user yet:

1. Go to `http://localhost:3001/signup`
2. Create a test account with a real email address you can access
3. Complete the registration process

### Step 3: Test Password Reset
1. Use the same email from Step 2
2. Click "Test Password Reset" in the debug tool
3. Check the logs for detailed error information

## 🔧 **Firebase Console Checklist**

Make sure these are configured in Firebase Console:

### Authentication Settings
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `medichain-8773b`
3. Navigate to **Authentication > Sign-in method**
4. Ensure **Email/Password** is **ENABLED**

### Email Template (Optional)
1. Go to **Authentication > Templates**
2. Click on **Password reset**  
3. Customize the email template if needed
4. Make sure **"From name"** and **"Reply-to"** are set

### Authorized Domains
1. Go to **Authentication > Settings**
2. Under **Authorized domains**, ensure these are added:
   - `localhost`
   - `medichain-8773b.firebaseapp.com`
   - Any production domains

## 🛠️ **Common Fixes**

### Fix 1: User Not Found Error
```javascript
// This means the email isn't registered in Firebase
// Solution: Create the user first via signup, or use an existing email
```

### Fix 2: Invalid Email Error  
```javascript
// Email format is wrong
// Solution: Use proper email format like user@example.com
```

### Fix 3: Network Request Failed
```javascript
// CORS or network issue
// Solution: Check Firebase config and internet connection
```

### Fix 4: Too Many Requests
```javascript
// Rate limiting triggered
// Solution: Wait 15-30 minutes and try again
```

## 📧 **Testing with Real Email**

For best results, test with:
1. **Gmail, Yahoo, or Outlook** account you can access
2. **Don't use** fake emails like `test@example.com`
3. **Check spam folder** if email doesn't arrive in inbox
4. **Wait 2-5 minutes** for email delivery

## 🔍 **Manual Test Script**

You can also test directly in browser console:

```javascript
import { sendPasswordResetEmail } from 'firebase/auth';
import { auth } from './config/firebase';

// Replace with actual registered email
const testEmail = 'your-real-email@gmail.com';

sendPasswordResetEmail(auth, testEmail)
  .then(() => {
    console.log('✅ Password reset email sent!');
  })
  .catch((error) => {
    console.error('❌ Error:', error.code, error.message);
  });
```

## 🚀 **Expected Success Flow**

When working correctly:
1. User enters registered email
2. Firebase sends reset email (usually arrives in 1-5 minutes)
3. User clicks link in email  
4. Firebase redirects to password reset page
5. User enters new password
6. User can login with new password

## 🔧 **If Still Not Working**

1. **Check Firebase Console > Authentication > Users** - Make sure the test email exists
2. **Check browser developer console** for JavaScript errors
3. **Test with the debug tool** at `/debug-firebase`
4. **Verify Firebase config** in `src/config/firebase.js`
5. **Check network tab** in dev tools for failed requests

The debug tool will give you exact error codes and detailed information about what's failing.