# Symptoms Endpoint Fix

## Issue
The `/api/symptoms` endpoint returns a 500 error with message "404 Not Found", indicating the route is not being found by Flask.

## Root Cause
The backend server needs to be **restarted** to pick up the new route definition.

## Solution

### 1. Restart the Backend Server

**If running with Python directly:**
```bash
# Stop the current server (Ctrl+C)
# Then restart:
cd backend
python app.py
```

**If running with a process manager:**
```bash
# Restart the Flask application
```

### 2. Verify the Endpoint

After restarting, test the endpoint:
```bash
curl http://localhost:5000/api/symptoms
```

Or use the test script:
```bash
python test_symptoms_endpoint.py
```

### 3. Expected Response

You should see:
```json
{
  "success": true,
  "symptoms": [
    {
      "key": "headache",
      "display": "Headache"
    },
    ...
  ],
  "count": 96
}
```

## Code Changes Made

1. ✅ Added `/api/symptoms` endpoint in `backend/app.py` (line 697)
2. ✅ Endpoint fetches symptoms from `ai_engine.symptom_columns`
3. ✅ Formats symptom names (snake_case → Title Case)
4. ✅ Returns both `key` (for backend) and `display` (for UI)
5. ✅ Added comprehensive error handling

## Verification Steps

1. **Check if server is running:**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Test symptoms endpoint:**
   ```bash
   curl http://localhost:5000/api/symptoms
   ```

3. **Check browser console:**
   - Open browser DevTools
   - Navigate to `/symptoms-selection`
   - Check Network tab for `/api/symptoms` request
   - Should see 200 status with symptoms data

## Troubleshooting

If still getting errors after restart:

1. **Check server logs** for any initialization errors
2. **Verify AI engine is initialized:**
   ```bash
   curl http://localhost:5000/api/ai/health
   ```
   Should return `"status": "healthy"`

3. **Check for import errors** in server startup logs
4. **Verify Supabase connection** is working

## Next Steps

After restarting the server:
- The symptoms page should load all 96 symptoms from Supabase
- Symptoms will be displayed in a grid layout
- Search functionality will work
- Selected symptoms will be passed to the booking flow

