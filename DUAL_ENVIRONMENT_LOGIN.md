# Dual Environment Login Support

## Overview
The system now supports login from both:
- **Local Development**: `http://localhost:3000` → `http://localhost:5000`
- **Production Domain**: `https://medichain.clinic` → `https://medichainn.onrender.com`

## How It Works

### Frontend API Detection
**File**: `src/config/api.js`

The API URL is automatically detected based on the current hostname:

```javascript
// Detects if running on localhost
const isLocalhost = window.location.hostname === 'localhost' || 
                    window.location.hostname === '127.0.0.1';

// Uses local backend for localhost, production backend for domain
const API_URL = isLocalhost ? 'http://localhost:5000' : 'https://medichainn.onrender.com';
```

**Priority Order**:
1. `REACT_APP_API_URL` environment variable (if set)
2. Localhost detection (if hostname is localhost/127.0.0.1)
3. `NODE_ENV === 'development'` fallback
4. Production backend (default)

### Backend CORS Configuration
**File**: `backend/app.py`

The backend allows requests from both localhost and production domain:

```python
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://medichain-8773b.web.app",
    "https://medichain-8773b.firebaseapp.com",
    "https://medichain.clinic",
    "http://medichain.clinic"
]
```

## Testing

### Local Development
1. Start backend: `cd backend && python app.py` (runs on port 5000)
2. Start frontend: `npm start` (runs on port 3000)
3. Open: `http://localhost:3000/login`
4. Should connect to: `http://localhost:5000/api/auth/login`

### Production Domain
1. Deploy backend to Render (already deployed)
2. Deploy frontend to hosting (medichain.clinic)
3. Open: `https://medichain.clinic/login`
4. Should connect to: `https://medichainn.onrender.com/api/auth/login`

## Debugging

### Check Current Configuration
Open browser console and run:
```javascript
window.debugLogin.logApiConfig()
```

Expected output:
- **Localhost**: `detectedBackend: 'http://localhost:5000'`
- **Production**: `detectedBackend: 'https://medichainn.onrender.com'`

### Test Backend Connection
```javascript
window.debugLogin.testBackendConnection()
```

### Test CORS
```javascript
window.debugLogin.testCorsPreflight()
```

## Environment Variables

### Override API URL (Optional)
If you need to override the automatic detection:

**Local Development**:
```bash
# .env.local
REACT_APP_API_URL=http://localhost:5000
```

**Production**:
```bash
# .env.production
REACT_APP_API_URL=https://medichainn.onrender.com
```

## Verification Checklist

- [x] Frontend detects localhost automatically
- [x] Frontend uses production backend for domain
- [x] Backend CORS allows localhost origins
- [x] Backend CORS allows medichain.clinic origin
- [x] Debug utility shows correct backend URL
- [x] Login works on localhost
- [x] Login works on production domain

## Common Issues

### Issue: Localhost trying to connect to production backend
**Solution**: Check `window.location.hostname` in console. Should be `localhost` or `127.0.0.1`.

### Issue: Production domain trying to connect to localhost
**Solution**: Verify `NODE_ENV` is set to `production` in build process.

### Issue: CORS errors on localhost
**Solution**: Ensure backend is running on `localhost:5000` and CORS includes `http://localhost:3000`.

### Issue: CORS errors on production
**Solution**: Verify `medichain.clinic` is in `ALLOWED_ORIGINS` in backend.

## Status

✅ **Both environments supported and tested**

- Local development: ✅ Working
- Production domain: ✅ Working
- Automatic detection: ✅ Implemented
- CORS configuration: ✅ Complete

