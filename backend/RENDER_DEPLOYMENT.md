# Render Deployment Guide for MediChain Backend

## Quick Setup Steps

### 1. On Render Dashboard

After selecting **Web Services**, you'll configure:

**Name:** `medichain-backend` (or any name you prefer)

**Environment:** `Python 3`

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

**Root Directory:** `backend` (if deploying from repo root)

### 2. Environment Variables

You'll need to add these in the Render dashboard → Environment:

#### Required Variables:
- `PORT` - Automatically set by Render (don't override)
- `FLASK_ENV=production`
- `PYTHON_VERSION=3.11` (or your preferred version)

#### Supabase Variables:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `SUPABASE_SERVICE_KEY` - Your Supabase service role key

#### Firebase Variables:
- `FIREBASE_PROJECT_ID` - Your Firebase project ID
- `FIREBASE_PRIVATE_KEY` - Your Firebase private key (full key with \n)
- `FIREBASE_CLIENT_EMAIL` - Your Firebase service account email
- `FIREBASE_PRIVATE_KEY_ID` - Your Firebase private key ID

#### Optional Variables:
- `GMAIL_USER` - For email notifications (if using)
- `GMAIL_APP_PASSWORD` - For email notifications (if using)
- `SECRET_KEY` - Flask secret key for sessions

### 3. Health Check Path

In Render dashboard → Settings → Health Check Path:
```
/health
```

### 4. Auto-Deploy

- Enable **Auto-Deploy** if connecting to a Git repository
- Or use **Manual Deploy** to upload code

### 5. After Deployment

1. Copy the Render service URL (e.g., `https://medichain-backend.onrender.com`)
2. Update your frontend API configuration in `src/config/api.js`:
   - Change line 19 from `'https://medichain.vercel.app'` to your Render URL
   - Or set `REACT_APP_API_URL` environment variable during build

3. Rebuild and redeploy frontend:
   ```bash
   # Set the API URL
   $env:REACT_APP_API_URL="https://your-backend-url.onrender.com"
   npm run build
   firebase deploy
   ```

## Testing Your Deployment

After deployment, test these endpoints:

1. **Health Check:**
   ```
   GET https://your-backend-url.onrender.com/health
   ```

2. **API Health:**
   ```
   GET https://your-backend-url.onrender.com/api/health
   ```

3. **Auth Test:**
   ```
   POST https://your-backend-url.onrender.com/api/auth/verify
   ```

## Troubleshooting

### Build Failures
- Check Python version compatibility
- Ensure all dependencies are in `requirements.txt`
- Check build logs in Render dashboard

### Runtime Errors
- Check environment variables are set correctly
- Verify Supabase credentials
- Check Firebase service account credentials format

### CORS Issues
- Flask-CORS should handle this automatically
- If issues persist, check CORS configuration in `app.py`

## Notes

- Render free tier may spin down after inactivity (15 min timeout)
- First request after spin-down may take 30-60 seconds
- Consider upgrading to paid tier for always-on service

