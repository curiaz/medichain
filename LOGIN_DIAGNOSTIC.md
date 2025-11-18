# Login Issue Diagnostic Guide

## Common Login Issues & Solutions

### 1. CORS Errors (Most Likely)
**Symptoms:**
- Console shows: `Access to XMLHttpRequest blocked by CORS policy`
- Network tab shows preflight OPTIONS request failing
- Login requests fail with CORS errors

**Solution:**
- ✅ CORS fix has been applied to `backend/app.py`
- ⚠️ **Backend needs to be deployed** to Render for the fix to take effect
- Check if backend is running: `https://medichainn.onrender.com/health`

**To Fix:**
1. Deploy the updated `backend/app.py` with CORS improvements
2. Verify CORS headers are being sent in response

### 2. Network/Connection Errors
**Symptoms:**
- `ERR_NETWORK` or `Network Error` in console
- Backend not reachable

**Check:**
- Is backend running on Render?
- Is API URL correct? (Should be `https://medichainn.onrender.com` in production)
- Check browser console Network tab for failed requests

### 3. Firebase Authentication Errors
**Symptoms:**
- `auth/invalid-credential`
- `auth/user-not-found`
- `auth/wrong-password`

**Solution:**
- Login tries Firebase first, then falls back to backend
- If Firebase fails, it should automatically try backend email/password auth
- Check Firebase configuration in `src/config/firebase.js`

### 4. Backend API Errors
**Symptoms:**
- 500 Internal Server Error
- 401 Unauthorized
- 400 Bad Request

**Check Backend Logs:**
- Look for `[DEBUG]` messages in backend logs
- Check if Supabase connection is working
- Verify user exists in database

## Quick Diagnostic Steps

1. **Check Browser Console:**
   - Open DevTools (F12)
   - Go to Console tab
   - Look for error messages
   - Check Network tab for failed requests

2. **Check API URL:**
   ```javascript
   // In browser console
   console.log('API URL:', process.env.REACT_APP_API_URL || 'https://medichainn.onrender.com');
   ```

3. **Test Backend Health:**
   ```bash
   curl https://medichainn.onrender.com/health
   ```

4. **Test Login Endpoint:**
   ```bash
   curl -X POST https://medichainn.onrender.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"test@example.com","password":"test123"}'
   ```

5. **Check CORS Headers:**
   ```bash
   curl -X OPTIONS https://medichainn.onrender.com/api/auth/login \
     -H "Origin: https://medichain.clinic" \
     -H "Access-Control-Request-Method: POST" \
     -v
   ```

## Most Likely Issue

Based on the earlier CORS fix, the most likely issue is:
1. **CORS fix not deployed yet** - The backend on Render needs to be updated with the new CORS configuration
2. **Backend not running** - Render service might be sleeping or crashed

## Immediate Actions

1. **Deploy CORS Fix:**
   ```bash
   git add backend/app.py
   git commit -m "fix: Improve CORS handling for login"
   git push origin master
   ```

2. **Check Render Dashboard:**
   - Verify backend service is running
   - Check recent deployments
   - Review logs for errors

3. **Test Locally:**
   - Run backend locally: `cd backend && python app.py`
   - Test login from frontend
   - Check if CORS works locally

