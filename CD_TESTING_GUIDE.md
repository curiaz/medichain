# 🧪 CD Pipeline Testing Guide

This guide shows you how to test your Continuous Deployment (CD) pipeline in multiple ways.

---

## 📋 Quick Test Methods

### Method 1: Manual Trigger (Fastest - Recommended for First Test)

**Time:** 2-5 minutes  
**Best for:** Testing if CD is configured correctly

#### Steps:

1. **Go to GitHub Actions**
   - Navigate to your repository on GitHub
   - Click on the **Actions** tab

2. **Select CD Workflow**
   - In the left sidebar, find **"CD - Production Deployment"** or **"CD - Staging Deployment"**
   - If you don't see it, click **"All workflows"** and search for it

3. **Trigger Manually**
   - Click on the workflow name
   - Click the **"Run workflow"** dropdown button (top right)
   - Select branch: `master` (for production) or `develop` (for staging)
   - Leave "Skip tests" as `false` (default)
   - Click **"Run workflow"** button

4. **Monitor the Run**
   - You'll see a new workflow run appear
   - Click on it to see the progress
   - Watch for:
     - ✅ Green checkmarks = Success
     - ❌ Red X = Failure
     - 🟡 Yellow circle = In progress

5. **Verify Deployment**
   - **Frontend**: Check https://medichain-8773b.web.app (should update)
   - **Backend**: Check Render dashboard for deployment status

---

### Method 2: Automatic Trigger (Real-World Test)

**Time:** 5-10 minutes  
**Best for:** Testing the full CI → CD flow

#### Steps:

1. **Make a Small Change**
   ```bash
   # For staging test
   git checkout develop
   
   # Or for production test
   git checkout master
   ```

2. **Create a Test Commit**
   ```bash
   # Make a small change (e.g., update README)
   echo "# CD Test - $(date)" >> README.md
   
   # Or create a test file
   echo "CD test file" > test-cd.txt
   
   # Commit and push
   git add .
   git commit -m "Test CD pipeline"
   git push origin develop  # or master
   ```

3. **Watch CI Run First**
   - Go to **GitHub → Actions**
   - Find **"CI/CD Pipeline"** workflow
   - Wait for it to complete (should show ✅)

4. **CD Should Trigger Automatically**
   - After CI passes, **"CD - Production Deployment"** (or Staging) should appear
   - It will run automatically
   - Monitor the progress

5. **Verify Results**
   - Check workflow logs for any errors
   - Verify frontend deployed to Firebase
   - Check backend deployment on Render

---

### Method 3: Test with a Feature Branch (Safest)

**Time:** 5-10 minutes  
**Best for:** Testing without affecting main branches

#### Steps:

1. **Create Test Branch**
   ```bash
   git checkout -b test-cd-pipeline
   ```

2. **Make Test Change**
   ```bash
   echo "CD test" > test-cd.txt
   git add test-cd.txt
   git commit -m "Test CD pipeline"
   git push origin test-cd-pipeline
   ```

3. **Test CI (CD won't trigger on feature branches)**
   - CI will run and test your code
   - CD won't trigger (only triggers on `master`/`develop`)
   - This verifies CI is working

4. **Merge to Test CD**
   ```bash
   # Merge to develop to test staging CD
   git checkout develop
   git merge test-cd-pipeline
   git push origin develop
   
   # Now CD should trigger automatically
   ```

---

## ✅ What to Check When Testing

### 1. Workflow Visibility
- [ ] Can you see "CD - Production Deployment" in Actions sidebar?
- [ ] Can you see "CD - Staging Deployment" in Actions sidebar?
- [ ] If not visible, manually trigger once to make them appear

### 2. Workflow Execution
- [ ] Does the workflow start when triggered?
- [ ] Do all jobs show as running?
- [ ] Do jobs complete successfully?

### 3. Frontend Deployment
- [ ] Does "deploy-frontend" job complete?
- [ ] Check Firebase Hosting dashboard
- [ ] Visit https://medichain-8773b.web.app
- [ ] Verify your changes are live

### 4. Backend Deployment
- [ ] Does "deploy-backend" job complete?
- [ ] Check Render dashboard
- [ ] Verify backend service is running
- [ ] Test API endpoints

### 5. Automatic Triggering
- [ ] After CI passes, does CD trigger automatically?
- [ ] Check workflow logs for trigger information
- [ ] Verify it's using the correct branch

---

## 🔍 Detailed Verification Steps

### Check Workflow Logs

1. **Go to Workflow Run**
   - Click on the workflow run
   - Click on each job to see logs

2. **Check Key Steps**
   - ✅ Checkout code
   - ✅ Set up Node.js
   - ✅ Install dependencies
   - ✅ Build frontend
   - ✅ Deploy to Firebase
   - ✅ Deploy backend (if configured)

3. **Look for Errors**
   - Red text = Error
   - Yellow warnings = Usually OK
   - Check the end of logs for summary

### Verify Firebase Deployment

1. **Firebase Console**
   - Go to https://console.firebase.google.com
   - Select project: `medichain-8773b`
   - Go to **Hosting**
   - Check recent deployments

2. **Check Live Site**
   - Visit https://medichain-8773b.web.app
   - Hard refresh (Ctrl+F5) to see latest version
   - Check browser console for errors

### Verify Render Deployment

1. **Render Dashboard**
   - Go to https://dashboard.render.com
   - Find your backend service
   - Check **Deploys** tab
   - Verify latest deployment status

2. **Test API**
   ```bash
   # Test if backend is responding
   curl https://medichainn.onrender.com/health
   # Or visit in browser
   ```

---

## 🐛 Troubleshooting Common Issues

### Issue: CD Workflow Not Visible

**Solution:**
1. Manually trigger it once (Method 1)
2. Check if workflow files exist in `.github/workflows/`
3. Verify you have Actions permissions

### Issue: CD Not Triggering Automatically

**Possible Causes:**
1. **CI didn't pass** - Check CI workflow status
2. **Wrong branch** - CD only triggers on `master` (production) or `develop` (staging)
3. **Permissions** - Check Settings → Actions → General → Workflow permissions

**Solution:**
```bash
# Check CI status
# Go to Actions → CI/CD Pipeline → Latest run

# Verify branch
git branch  # Should be on master or develop

# Check permissions
# Settings → Actions → General → Workflow permissions
# Should be "Read and write permissions"
```

### Issue: Frontend Deployment Fails

**Check:**
- Firebase service account secret is configured
- Build completes successfully
- Firebase project ID is correct

**Solution:**
```bash
# Check secrets
# Settings → Secrets and variables → Actions
# Verify: FIREBASE_SERVICE_ACCOUNT_MEDICHAIN_8773B exists

# Check build locally
npm run build
# Should complete without errors
```

### Issue: Backend Deployment Fails

**Check:**
- Render auto-deploy is enabled (if using auto-deploy)
- Render API credentials are set (if using API trigger)
- Backend service is configured correctly

**Solution:**
- Check Render dashboard → Your service → Settings
- Verify auto-deploy is enabled
- Or add `RENDER_API_KEY` and `RENDER_SERVICE_ID` secrets

---

## 📊 Expected Results

### Successful CD Test Should Show:

```
✅ check-ci-status - Success
✅ deploy-frontend - Success
✅ deploy-backend - Success
✅ deployment-notification - Success
```

### Workflow Summary Should Show:

```
## 🚀 Frontend Deployment Complete
- Environment: Production
- URL: https://medichain-8773b.web.app
- Branch: master
- Commit: [commit hash]

## 🔄 Backend Deployment
- Backend deployment to Render is configured via Render's auto-deploy feature.

## 📊 Deployment Summary
| Component | Status |
|-----------|--------|
| Frontend | success |
| Backend | success |
```

---

## 🎯 Quick Test Checklist

Use this checklist for a quick test:

- [ ] Can access GitHub Actions
- [ ] CD workflows are visible
- [ ] Manual trigger works
- [ ] Frontend builds successfully
- [ ] Frontend deploys to Firebase
- [ ] Backend deployment step completes
- [ ] Can verify changes on live site
- [ ] Automatic trigger works after CI passes

---

## 🚀 Next Steps After Testing

Once CD is working:

1. **Set up Environments** (Optional but recommended)
   - Settings → Environments
   - Create `production` and `staging` environments
   - Add protection rules if needed

2. **Monitor First Few Deployments**
   - Watch for any issues
   - Check deployment times
   - Verify all components deploy correctly

3. **Configure Secrets** (If needed)
   - Add `REACT_APP_API_URL` if using custom API
   - Add Render API credentials if using API triggers

4. **Document Your Process**
   - Note any custom configurations
   - Document any manual steps needed

---

## 📝 Test Script

You can also use this quick test script:

```bash
#!/bin/bash
# Quick CD Test Script

echo "🧪 Testing CD Pipeline..."
echo ""

# Check if on correct branch
BRANCH=$(git branch --show-current)
echo "Current branch: $BRANCH"

if [ "$BRANCH" != "master" ] && [ "$BRANCH" != "develop" ]; then
    echo "⚠️  Warning: CD only triggers on master or develop"
    echo "   Current branch: $BRANCH"
fi

# Make test change
echo "Creating test file..."
echo "CD test - $(date)" > test-cd-$(date +%s).txt
git add test-cd-*.txt
git commit -m "Test CD pipeline - $(date)"

echo ""
echo "✅ Test commit created"
echo "📤 Pushing to trigger CI/CD..."
git push origin $BRANCH

echo ""
echo "🔍 Check GitHub Actions:"
echo "   https://github.com/YOUR_REPO/actions"
echo ""
echo "⏳ Wait for CI to pass, then CD should trigger automatically"
```

---

**Last Updated:** $(date)  
**Status:** Ready for testing ✅

