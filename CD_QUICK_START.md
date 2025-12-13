# CD Pipeline Quick Start

## What Was Added

✅ **Production CD Pipeline** (`.github/workflows/cd-production.yml`)
- Automatically deploys after successful CI on `master` branch
- Deploys frontend to Firebase Hosting
- Deploys backend to Render

✅ **Staging CD Pipeline** (`.github/workflows/cd-staging.yml`)
- Automatically deploys after successful CI on `develop` branch
- Deploys frontend to Firebase Hosting (preview)
- Deploys backend to Render staging

## How It Works

1. **Developer pushes code** → CI runs (tests, linting, builds)
2. **CI passes** → CD automatically triggers
3. **CD deploys** → Frontend and backend are deployed

## Setup Checklist

### Required (Already Done)
- ✅ CD workflows created
- ✅ Firebase service account configured
- ✅ CI pipeline exists

### Optional (Recommended)
- [ ] Add `REACT_APP_API_URL` secret if you need custom API URL
- [ ] Add `RENDER_API_KEY` and `RENDER_SERVICE_ID` if you want API-triggered backend deployments
- [ ] Set up GitHub Environments for deployment protection
- [ ] Configure Render auto-deploy for backend (recommended)

## Testing the Pipeline

### Test Staging Deployment
```bash
# 1. Make a change
git checkout develop
# ... make changes ...
git commit -m "Test CD pipeline"
git push origin develop

# 2. Watch CI run
# Go to GitHub → Actions → CI/CD Pipeline

# 3. After CI passes, CD will automatically trigger
# Go to GitHub → Actions → CD - Staging Deployment
```

### Test Production Deployment
```bash
# 1. Merge to master (or push directly)
git checkout master
git merge develop
git push origin master

# 2. Watch CI run, then CD will trigger automatically
```

## Manual Deployment

If you need to deploy manually:

1. Go to **GitHub → Actions**
2. Select **CD - Production Deployment** or **CD - Staging Deployment**
3. Click **Run workflow**
4. Select branch and run

## Current Workflow Status

- **CI Pipeline**: Runs on every push/PR ✅
- **CD Production**: Runs after CI on `master` ✅
- **CD Staging**: Runs after CI on `develop` ✅
- **Firebase PR Previews**: Still works for PRs ✅
- **Old Firebase Merge**: Still active (can be disabled if preferred)

## Next Steps

1. **Test it**: Push a small change to `develop` and watch it deploy
2. **Monitor**: Check the first few deployments closely
3. **Configure**: Add any missing secrets or environment variables
4. **Protect**: Set up environment protection rules for production

## Troubleshooting

**CD not running?**
- Check that CI passed successfully
- Verify you're on the right branch (`master` or `develop`)
- Check workflow permissions in repository settings

**Deployment failing?**
- Check GitHub Actions logs
- Verify secrets are configured correctly
- Check Firebase and Render dashboards

For detailed information, see `CD_DEPLOYMENT_GUIDE.md`

