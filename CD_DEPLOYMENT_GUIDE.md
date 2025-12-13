# Continuous Deployment (CD) Pipeline Guide

## Overview

This project now has a complete Continuous Deployment (CD) pipeline that automatically deploys your application after successful CI builds. The CD pipeline is separate from CI and only runs when all tests, linting, and security checks pass.

## Architecture

### CI Pipeline (`.github/workflows/ci.yml`)
- Runs on every push and pull request
- Executes tests, linting, security scans, and builds
- Does NOT deploy anything
- Must pass before CD can run

### CD Pipelines

#### 1. Production CD (`.github/workflows/cd-production.yml`)
- **Triggers**: 
  - Automatically after successful CI on `master` branch
  - Manual trigger via GitHub Actions UI
- **Deploys**:
  - Frontend to Firebase Hosting (production)
  - Backend to Render (via auto-deploy or API)

#### 2. Staging CD (`.github/workflows/cd-staging.yml`)
- **Triggers**: 
  - Automatically after successful CI on `develop` branch
  - Manual trigger via GitHub Actions UI
- **Deploys**:
  - Frontend to Firebase Hosting (preview channel)
  - Backend to Render staging (if configured)

## Setup Instructions

### 1. GitHub Secrets Configuration

Navigate to your repository: **Settings → Secrets and variables → Actions**

#### Required Secrets

**Firebase:**
- `FIREBASE_SERVICE_ACCOUNT_MEDICHAIN_8773B` - Already configured ✅

**Frontend Environment Variables (Optional):**
- `REACT_APP_API_URL` - Production API URL (defaults to `https://medichainn.onrender.com`)
- `REACT_APP_STAGING_API_URL` - Staging API URL (optional, falls back to production)

**Backend Deployment (Optional - for manual Render API triggers):**
- `RENDER_API_KEY` - Render API key (if you want to trigger deployments via API)
- `RENDER_SERVICE_ID` - Render production service ID
- `RENDER_SERVICE_ID_STAGING` - Render staging service ID (if you have a separate staging service)

### 2. GitHub Environments

The workflows use GitHub Environments for better control and protection:

**Production Environment:**
- Go to **Settings → Environments → New environment**
- Name: `production`
- Add protection rules if needed (required reviewers, deployment branches, etc.)

**Staging Environment:**
- Name: `staging`
- Configure as needed for your staging workflow

**Backend Environments:**
- `production-backend`
- `staging-backend`

### 3. Render Configuration

#### Option A: Auto-Deploy (Recommended)
1. In Render dashboard, ensure your service has:
   - **Auto-Deploy**: Enabled
   - **Branch**: Set to `master` for production, `develop` for staging
   - **Root Directory**: `backend` (if deploying from repo root)

#### Option B: Manual API Deployment
1. Get your Render API key from: https://dashboard.render.com/account/api-keys
2. Get your service ID from the Render service URL or API
3. Add secrets as mentioned above

### 4. Firebase Configuration

Firebase hosting is already configured. The CD pipeline will:
- Build the React app
- Deploy to Firebase Hosting
- Use the `firebase.json` configuration

## Workflow Details

### Production Deployment Flow

```
Push to master → CI runs → CI passes → CD Production triggers
  ↓
Build frontend → Deploy to Firebase (live channel)
  ↓
Deploy backend → Render (auto-deploy or API trigger)
  ↓
Deployment complete
```

### Staging Deployment Flow

```
Push to develop → CI runs → CI passes → CD Staging triggers
  ↓
Build frontend → Deploy to Firebase (preview channel)
  ↓
Deploy backend → Render staging (auto-deploy or API trigger)
  ↓
Deployment complete
```

## Manual Deployment

You can manually trigger deployments:

1. Go to **Actions** tab in GitHub
2. Select the workflow (CD - Production Deployment or CD - Staging Deployment)
3. Click **Run workflow**
4. Select branch and options
5. Click **Run workflow**

## Monitoring Deployments

### GitHub Actions
- View deployment status in the **Actions** tab
- Check deployment summaries in workflow runs
- View logs for troubleshooting

### Firebase Hosting
- Production: https://medichain-8773b.web.app
- Preview channels: Check Firebase console

### Render
- Check deployment status in Render dashboard
- View logs and metrics

## Rollback Procedures

### Frontend Rollback

**Firebase Hosting:**
1. Go to Firebase Console → Hosting
2. Click on previous deployment
3. Click "Rollback" or redeploy previous version

**Via GitHub:**
1. Revert the commit that caused issues
2. Push to trigger new deployment

### Backend Rollback

**Render:**
1. Go to Render dashboard → Your service
2. Navigate to Deploys
3. Select previous successful deployment
4. Click "Rollback"

## Environment Variables

### Frontend Build Variables

The CD pipeline sets these during build:

**Production:**
- `NODE_ENV=production`
- `REACT_APP_API_URL` (from secrets or default)

**Staging:**
- `NODE_ENV=production`
- `REACT_APP_STAGING_API_URL` or `REACT_APP_API_URL`

### Backend Environment Variables

Configure these in Render dashboard (not in GitHub secrets):
- `FLASK_ENV=production`
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_PRIVATE_KEY`
- And other backend-specific variables

## Troubleshooting

### CD Not Triggering

1. **Check CI Status**: CD only runs after successful CI
   - Go to Actions → CI/CD Pipeline
   - Ensure latest run completed successfully

2. **Check Branch**: 
   - Production CD: Only triggers on `master`
   - Staging CD: Only triggers on `develop`

3. **Check Workflow Permissions**:
   - Ensure workflows have permission to trigger other workflows
   - Check repository settings → Actions → General → Workflow permissions

### Frontend Deployment Fails

1. **Check Build Logs**: Look for build errors in GitHub Actions
2. **Check Firebase Service Account**: Ensure secret is valid
3. **Check Firebase Project**: Verify project ID matches
4. **Check Build Artifacts**: Ensure `build/` directory is created

### Backend Deployment Fails

1. **If using Render Auto-Deploy**: Check Render dashboard for errors
2. **If using API**: Check `RENDER_API_KEY` and `RENDER_SERVICE_ID` secrets
3. **Check Render Logs**: View deployment logs in Render dashboard

## Best Practices

1. **Always test in staging first**: Deploy to `develop` branch before `master`
2. **Monitor deployments**: Watch the first few deployments closely
3. **Use feature flags**: Consider feature flags for gradual rollouts
4. **Keep secrets secure**: Never commit secrets to repository
5. **Review before production**: Use environment protection rules for production
6. **Test rollback procedures**: Know how to rollback before you need to

## Branch Strategy

- **`master`**: Production deployments (auto-deploy after CI)
- **`develop`**: Staging deployments (auto-deploy after CI)
- **Feature branches**: CI runs, but no deployment
- **Pull requests**: CI runs, Firebase previews via existing PR workflow

## Integration with Existing Workflows

The CD pipeline works alongside existing workflows:

- **Firebase PR Previews** (`.github/workflows/firebase-hosting-pull-request.yml`): Still works for PR previews
- **Firebase Merge** (`.github/workflows/firebase-hosting-merge.yml`): Can be disabled or kept as backup

## Next Steps

1. ✅ Configure GitHub secrets (if not already done)
2. ✅ Set up GitHub environments (optional but recommended)
3. ✅ Verify Render auto-deploy is enabled
4. ✅ Test staging deployment (push to `develop`)
5. ✅ Test production deployment (merge to `master`)

## Support

For issues or questions:
- Check GitHub Actions logs
- Review Firebase and Render dashboards
- Consult this guide and CI/CD documentation

---

**Last Updated**: $(date)
**Pipeline Version**: 1.0

